import argparse
import os
from glob import glob
from tqdm import tqdm
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pydub import AudioSegment
from pydub.silence import split_on_silence

def cut_silence(input_file, output_file, silence_threshold=-60, min_silence_len=500):
    audio = AudioSegment.from_file(input_file, format="wav")
    chunks = split_on_silence(audio, silence_thresh=silence_threshold, min_silence_len=min_silence_len, keep_silence=0)
    result = AudioSegment.empty()
    for chunk in chunks:
        result += chunk
    result.export(output_file, format="wav")

def process_one(file, input_folder, output_folder, silence_threshold=-60, min_silence_len=500):
    input_file = file
    output_file = os.path.join(output_folder, os.path.relpath(input_file, start=input_folder))
    output_file_dir = os.path.dirname(output_file)
    os.makedirs(output_file_dir, exist_ok=True)
    audio = AudioSegment.from_file(input_file, format="wav")
    chunks = split_on_silence(audio, silence_thresh=silence_threshold, min_silence_len=min_silence_len, keep_silence=0)
    result = AudioSegment.empty()
    for chunk in chunks:
        result += chunk
    result.export(output_file, format="wav")

def process_batch(file_chunk, input_folder, output_folder):
    for file in tqdm(file_chunk):
        process_one(file, input_folder, output_folder)

def parallel_process(files, input_folder, output_folder, num_processes):
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        tasks = []
        for i in range(num_processes):
            start = int(i * len(files) / num_processes)
            end = int((i + 1) * len(files) / num_processes)
            file_chunk = files[start:end]
            tasks.append(executor.submit(process_batch, file_chunk, input_folder, output_folder))
        for task in tqdm(tasks):
            task.result()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_folder", type=str, default=r"C:\Users\bfloat16\Desktop\33", help="path to input dir")
    parser.add_argument('--output_folder', type=str, default=r"C:\Users\bfloat16\Desktop\44", help='path to output dir')
    parser.add_argument('--num_processes', type=int, default=3, help='set the number of processes')
    args = parser.parse_args()
    output_folder = args.output_folder
    input_folder = args.input_folder

    files = glob(f"{input_folder}/* *.wav", recursive=True)

    multiprocessing.set_start_method("spawn", force=True)
    num_processes = args.num_processes
    if num_processes == 0:
        num_processes = os.cpu_count()
    
    parallel_process(files, input_folder, output_folder, num_processes)