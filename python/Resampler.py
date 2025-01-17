import os
import av
import argparse
import av.audio
import av.audio.resampler
import numpy as np
import pyloudnorm as pyln
import torch.multiprocessing as mp
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn, MofNCompleteColumn

rich_progress = Progress(TextColumn("Running: "), BarColumn(), "[progress.percentage]{task.percentage:>3.1f}%", "•", MofNCompleteColumn(), "•", TimeElapsedColumn(), "|", TimeRemainingColumn(), refresh_per_second=5)

def save_as_mp3(audio, filename, in_dir, out_dir, sample_rate):
    rel_path = os.path.relpath(filename, in_dir)
    output_path = os.path.join(out_dir, os.path.splitext(rel_path)[0] + ".mp3")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    container = av.open(output_path, mode='w')
    
    stream = container.add_stream('mp3', rate=sample_rate)
    stream.bit_rate = 320000
    stream.format = 's16p'
    stream.layout = 'mono'

    frame = av.AudioFrame.from_ndarray(audio, format='flt', layout='mono')
    frame.sample_rate = sample_rate

    for packet in stream.encode(frame):
        container.mux(packet)

    for packet in stream.encode():
        container.mux(packet)

    container.close()

def process_batch(rank, filelist, in_dir, out_dir, target_sr, num_process):
    filenames = filelist[rank::num_process]
    print(f"\nProcess {rank} - Number of files: {len(filenames)}")
    
    with Progress() as rich_progress:
        task2 = rich_progress.add_task("Processing", total=len(filenames))
        
        for filename in filenames:
            try:
                input_container = av.open(filename)
                input_stream = input_container.streams.audio[0]
                resampler = av.AudioResampler(format='s16', layout='mono', rate=target_sr)
                
                audio_frames = []
                for frame in input_container.decode(input_stream):
                    if isinstance(frame, av.AudioFrame):
                        resampled_frame = resampler.resample(frame)
                        audio_frames.append(resampled_frame)

                if not audio_frames:
                    raise ValueError(f"No valid audio frames in {filename}")
                
                audio = np.hstack([frame.to_ndarray().flatten() for frame in audio_frames])
                duration = len(audio) / target_sr
                
                if duration > 30 or duration < 1:
                    print(f"Skip: {filename} - Duration: {duration:.2f}s")
                    continue

                peak_normalized_audio = pyln.normalize.peak(audio, -1.0)

                meter = pyln.Meter(target_sr)
                loudness = meter.integrated_loudness(peak_normalized_audio)
                loudness_normalized_audio = pyln.normalize.loudness(peak_normalized_audio, loudness, -23.0)

                audio_f = np.expand_dims(loudness_normalized_audio, axis=0)
                save_as_mp3(audio_f, filename, in_dir, out_dir, target_sr)

            except Exception as e:
                print(f"Error: {filename}: {e}")
            rich_progress.update(task2, advance=1)

def main(in_dir):
    print('Loading audio files...')
    extensions = ["wav", "mp3", "ogg", "flac", "opus", "snd"]
    filenames = []

    with rich_progress:
        task1 = rich_progress.add_task("Loading", total=None)
        for root, _, files in os.walk(in_dir):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    filenames.append(os.path.join(root, file))
                    rich_progress.update(task1, advance=1)
        rich_progress.update(task1, total=len(filenames), completed=len(filenames))

    print("==========================================================================")
    return filenames

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", type=str, default=r"D:\Dataset\EN-B000000")
    parser.add_argument("--out_dir", type=str, default=r"D:\Dataset_16k")
    parser.add_argument("--target_sr", type=int, default=16000)
    parser.add_argument('--num_process', type=int, default=1)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    filelist = main(args.in_dir)
    print(f'Number of files: {len(filelist)}')
    print('Start Resample...')

    mp.spawn(process_batch, args=(filelist, args.in_dir, args.out_dir, args.target_sr, args.num_process), nprocs=args.num_process, join=True)