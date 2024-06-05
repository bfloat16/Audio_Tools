import glob
import os
import subprocess

def main(file_path):
    psb_decompile_path = os.path.join(os.path.dirname(__file__), 'TextCleaner_Kirikiri_scn_Psb.exe')
    command = [psb_decompile_path, file_path]
    try:
        subprocess.run(command, check=True)
        print(f"Decompilation successful for {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error decompiling {file_path}: {e}")

if __name__ == '__main__':
    input_directory_path = r"E:\Dataset\FuckGalGame\Lose\Maitetsu - Last Run!!\script"
    file_paths = glob.glob(os.path.join(input_directory_path, '*'))
    for file_path in file_paths:
        main(file_path)