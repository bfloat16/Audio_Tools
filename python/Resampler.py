import os
import shutil
import argparse
import subprocess
from glob import glob
from concurrent.futures import ProcessPoolExecutor
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn, MofNCompleteColumn
rich_progress = Progress(TextColumn("Resample:"), BarColumn(), "[progress.percentage]{task.percentage:>3.1f}%", "•", MofNCompleteColumn(), "•", TimeElapsedColumn(), "|", TimeRemainingColumn())

def process_batch(file_chunk, in_dir, out_dir):
    with rich_progress:
        resample = rich_progress.add_task("Resample", total=len(file_chunk))
        for filename in file_chunk:
            try:
                out_audio = os.path.join(out_dir, os.path.relpath(filename, in_dir)).rsplit('.', 1)[0] + '.wav'
                os.makedirs(os.path.dirname(out_audio), exist_ok=True)

                command = ['ffmpeg', '-y', '-i', filename, '-ar', '16000', '-ac', '1', out_audio]
                subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                '''
                 src_lab = filename.rsplit('.', 1)[0] + '.txt'
                if os.path.exists(src_lab):
                    out_lab = out_audio.rsplit('.', 1)[0] + '.txt'
                    shutil.copy(src_lab, out_lab)
                '''
                rich_progress.update(resample, advance=1)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                with open('error.log', 'a', encoding='utf-8') as error_log:
                    error_log.write(f'Error: {filename}\n')
                rich_progress.update(resample, advance=1)

def parallel_process(filelist, num_processes, in_dir, out_dir):
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        tasks = [executor.submit(process_batch, filelist[rank::num_processes], in_dir, out_dir) for rank in range(num_processes)]
        for task in tasks:
            task.result()

def get_filelist(in_dir):
    extensions = ['wav', 'ogg', 'opus', 'snd']
    files = []
    for ext in extensions:
        files.extend(glob(f"{in_dir}/**/*.{ext}", recursive=True))
    return files

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", type=str, default=r"E:\Dataset\FuckGalGame\#Single\DATE A LIVE - Rio Reincarnation\voice")
    parser.add_argument("--out_dir", type=str, default=r"D:\1")
    parser.add_argument('--num_processes', type=int, default=20)
    args = parser.parse_args()
    in_dir = args.in_dir
    out_dir = args.out_dir
    num_processes = args.num_processes

    print('Loading wav files...')
    filelist = get_filelist(in_dir)
    print(f'Number of wav files: {len(filelist)}')
    print('Start Resample...')

    parallel_process(filelist, num_processes, in_dir, out_dir)