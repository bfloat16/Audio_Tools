import os
import argparse
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from concurrent.futures import ProcessPoolExecutor
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn, MofNCompleteColumn

rich_progress = Progress(TextColumn("Running: "), BarColumn(), "[progress.percentage]{task.percentage:>3.1f}%", "•", MofNCompleteColumn(), "•", TimeElapsedColumn(), "|", TimeRemainingColumn(), refresh_per_second=5)

def sec_to_time(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return int(hours), int(minutes), seconds

def calculate_durations(filenames):
    total_duration_sec = 0
    max_duration_sec = 0
    min_duration_sec = float('inf')
    
    with rich_progress:
        task2 = rich_progress.add_task("Processing", total=len(filenames))
        
        for filename in filenames:
            try:
                if filename.endswith('.wav'):
                    audio = WAVE(filename)
                elif filename.endswith('.ogg'):
                    audio = OggVorbis(filename)
                elif filename.endswith('.opus'):
                    audio = OggOpus(filename)
                else:
                    raise ValueError(f"Unsupported file format: {filename}")
                
                file_duration_sec = audio.info.length  # Duration in seconds
                total_duration_sec += file_duration_sec
                max_duration_sec = max(max_duration_sec, file_duration_sec)
                min_duration_sec = min(min_duration_sec, file_duration_sec)
                rich_progress.update(task2, advance=1)
            
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    return total_duration_sec, max_duration_sec, min_duration_sec

def parallel_process(filenames, num_processes):
    results = []
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        tasks = [executor.submit(calculate_durations, filenames[int(i * len(filenames) / num_processes): int((i + 1) * len(filenames) / num_processes)]) for i in range(num_processes)]
        for future in tasks:
            results.append(future.result())
    return results

def aggregate_results(results):
    total_duration_sec = sum(result[0] for result in results)
    max_duration_sec = max(result[1] for result in results)
    min_duration_sec = min(result[2] for result in results if result[2] != float('inf'))  # Avoiding inf if possible
    return sec_to_time(total_duration_sec), sec_to_time(max_duration_sec), sec_to_time(min_duration_sec)

def main(in_dir, num_processes):
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
    
    if filenames:
        results = parallel_process(filenames, num_processes)
        total_duration, max_duration, min_duration = aggregate_results(results)
        print("==========================================================================")
        print(f"SUM: {len(filenames)} files\n")
        print(f"SUM: {total_duration[0]:02d}:{total_duration[1]:02d}:{total_duration[2]:05.2f}")
        print(f"MAX: {max_duration[0]:02d}:{max_duration[1]:02d}:{max_duration[2]:05.2f}")
        print(f"MIN: {min_duration[0]:02d}:{min_duration[1]:02d}:{min_duration[2]:05.2f}")
        return(f'{total_duration[0]:02d}:{total_duration[1]:02d}:{total_duration[2]:05.2f}')

    else:
        print("No audio files found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", type=str, default=r"D:\1")
    parser.add_argument('--num_processes', type=int, default=18)
    args = parser.parse_args()

    main(args.in_dir, args.num_processes)