import argparse
import os
from concurrent.futures import ProcessPoolExecutor
from glob import glob
import subprocess
from tqdm import tqdm
import shutil

def process_batch(file_chunk, in_dir, out_dir):
    for filename in tqdm(file_chunk):
        out_audio = filename.replace(in_dir, out_dir).replace('.opus', '.wav').replace('.ogg', '.wav')
        #out_lab = filename.replace(in_dir, out_dir).replace('.opus', '.lab').replace('.ogg', '.lab').replace('.wav', '.lab')
        os.makedirs(os.path.dirname(out_audio), exist_ok=True)

        # 使用 ffmpeg 进行音频格式转换，屏蔽输出
        command = ['ffmpeg', '-i', filename, '-ar', '16000', '-ac', '1', out_audio]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        #shutil.copy(filename.replace('.opus', '.lab').replace('.ogg', '.lab').replace('.wav', '.lab'), out_lab)

def parallel_process(filenames, num_processes, in_dir, out_dir):
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        tasks = []
        for i in range(num_processes):
            start = int(i * len(filenames) / num_processes)
            end = int((i + 1) * len(filenames) / num_processes)
            file_chunk = filenames[start:end]
            tasks.append(executor.submit(process_batch, file_chunk, in_dir, out_dir))
        for task in tqdm(tasks, position = 0):
            task.result()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", type=str, default=r"D:\GI_4.2_main")
    parser.add_argument("--out_dir", type=str, default=r"D:\GI_4.2_main_16k")
    parser.add_argument('--num_processes', type=int, default=15)
    args = parser.parse_args()

    filenames = glob(f"{args.in_dir}/**/*.wav", recursive=True)

    num_processes = args.num_processes
    if num_processes == 0:
        num_processes = os.cpu_count()

    parallel_process(filenames, num_processes, args.in_dir, args.out_dir)
