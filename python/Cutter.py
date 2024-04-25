import os
from glob import glob
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from pydub import AudioSegment, silence

def main(input_base_path, output_base_path, files):
    for file_path in tqdm(files):
        audio = AudioSegment.from_file(file_path)
        chunks = silence.split_on_silence(audio, min_silence_len=100, silence_thresh=-35, keep_silence=300)
        
        accumulated_chunk = AudioSegment.empty()
        i = 0
        for chunk in chunks:
            if len(chunk) < 3000:
                accumulated_chunk += chunk
                if len(accumulated_chunk) >= 3000 or i == len(chunks) - 1:
                    chunk_to_process = accumulated_chunk
                    accumulated_chunk = AudioSegment.empty()
                else:
                    continue
            else:
                chunk_to_process = chunk

            relative_path = os.path.relpath(file_path, input_base_path)
            output_dir = os.path.join(output_base_path, os.path.dirname(relative_path))
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(output_dir, f"{filename}_chunk{i}.wav")
            chunk_to_process.export(output_path, format="wav")
            i += 1

if __name__ == "__main__":
    input_folder_path = r"D:\猫雷_clean"
    output_folder_path = r"D:\猫雷_clean_cut"
    num_processes = 20

    extensions = ['wav', 'ogg', 'opus', 'snd']
    files = []
    for ext in extensions:
        files.extend(glob(f"{input_folder_path}/**/*.{ext}", recursive=True))

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        tasks = [executor.submit(main, input_folder_path, output_folder_path, files[rank::num_processes]) for rank in range(num_processes)]
        for task in tasks:
            task.result()
