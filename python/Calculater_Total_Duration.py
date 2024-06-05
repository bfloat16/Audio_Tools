import argparse
from glob import glob
from pydub import AudioSegment
from concurrent.futures import ProcessPoolExecutor
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn, MofNCompleteColumn
rich_progress = Progress(TextColumn("Running: "), BarColumn(), "[progress.percentage]{task.percentage:>3.1f}%", "•", MofNCompleteColumn(), "•", TimeElapsedColumn(), "|", TimeRemainingColumn())

def ms_to_time(ms):
    total_seconds = ms / 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return int(hours), int(minutes), seconds

def calculate_durations(filenames):
    total_duration_ms = 0
    max_duration_ms = 0
    min_duration_ms = float('inf')
    with rich_progress:
        task2 = rich_progress.add_task("Process", total=len(filenames))
        for filename in filenames:
            try:
                audio = AudioSegment.from_file(filename)
                file_duration_ms = len(audio)
                total_duration_ms += file_duration_ms
                max_duration_ms = max(max_duration_ms, file_duration_ms)
                min_duration_ms = min(min_duration_ms, file_duration_ms)
                rich_progress.update(task2, advance=1)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    return total_duration_ms, max_duration_ms, min_duration_ms

def parallel_process(filenames, num_processes):
    results = []
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        tasks = [executor.submit(calculate_durations, filenames[int(i * len(filenames) / num_processes): int((i + 1) * len(filenames) / num_processes)]) for i in range(num_processes)]
        for future in tasks:
            results.append(future.result())
    return results

def aggregate_results(results):
    total_duration_ms = sum(result[0] for result in results)
    max_duration_ms = max(result[1] for result in results)
    min_duration_ms = min(result[2] for result in results if result[2] != float('inf')) # Avoiding inf if possible
    return ms_to_time(total_duration_ms), ms_to_time(max_duration_ms), ms_to_time(min_duration_ms)

def main(in_dir, num_processes):
    print('Loading audio files...')
    extensions = ["wav", "mp3", "ogg", "flac", "opus", "snd"]
    filenames = []
    for ext in extensions:
        filenames.extend(glob(f"{in_dir}/**/*.{ext}", recursive=True))
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
    parser.add_argument("--in_dir", type=str, default=r"C:\Users\bfloat16\Desktop\WutheringWaves_CHS")
    parser.add_argument('--num_processes', type=int, default=10)
    args = parser.parse_args()

    main(args.in_dir, args.num_processes)