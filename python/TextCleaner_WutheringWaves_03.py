import os
import subprocess
import threading
import multiprocessing

def convert_wem_to_wav(wem_file_path, vgmstream_path):
    wav_file_path = os.path.splitext(wem_file_path)[0] + '.wav'
    command = f'{vgmstream_path} "{wem_file_path}" -o "{wav_file_path}"'
    subprocess.run(command, shell=True, check=True)
    os.remove(wem_file_path)

def get_wem_files(directory):
    wem_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.wem'):
                wem_files.append(os.path.join(root, file))
    return wem_files

def process_files(file_list, vgmstream_path):
    for wem_file in file_list:
        convert_wem_to_wav(wem_file, vgmstream_path)

def main(source_directory, vgmstream_cli_path):
    wem_files = get_wem_files(source_directory)
    cpu_count = multiprocessing.cpu_count()
    
    # Split wem_files into chunks based on the number of CPU cores
    chunk_size = len(wem_files) // cpu_count
    chunks = [wem_files[i:i + chunk_size] for i in range(0, len(wem_files), chunk_size)]

    threads = []
    for chunk in chunks:
        thread = threading.Thread(target=process_files, args=(chunk, vgmstream_cli_path))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    source_directory = r'C:\Users\bfloat16\Desktop\WutheringWaves_JA'
    vgmstream_cli_path = r"C:\Users\bfloat16\Downloads\#TMP2\vgmstream-win64\vgmstream-cli.exe"
    main(source_directory, vgmstream_cli_path)