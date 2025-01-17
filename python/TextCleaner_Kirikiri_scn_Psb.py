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
    input_directory_path = r"D:\\Fuck_galgame\\scn"

    # 使用 os.walk 遍历嵌套目录
    for root, _, files in os.walk(input_directory_path):
        for file in files:
            if file.endswith('.scn'):
                file_path = os.path.join(root, file)
                main(file_path)