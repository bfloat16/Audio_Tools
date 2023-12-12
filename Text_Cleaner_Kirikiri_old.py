import re
import glob
import os

def main(file_path, output_directory_path):
    with open(file_path, 'r', encoding='Shift_JIS') as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    pattern = re.compile(r'voice=[A-Za-z0-9]+')
    voice_lab_mapping = {}
    for i, line in enumerate(lines):
        match = pattern.search(line)
        if match:
            voice_value = lines[i]

            lab_value = lines[i + 1] #往下找1行

            voice_lab_mapping[voice_value] = lab_value
    '''
    for voice_value, lab_value in voice_lab_mapping.items():
        output_file_path = os.path.join(output_directory_path, f'{voice_value}')
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(lab_value)
    '''
    with open("1111.txt", 'a', encoding='utf-8') as output_file:
        for voice_value, lab_value in voice_lab_mapping.items():
            output_file.write(voice_value + '\n')
            output_file.write(lab_value + '\n')

if __name__ == '__main__':
    input_directory_path = r'C:\Users\bfloat16\Desktop\ハルカナソラ\data\scenario'
    output_directory_path = r'D:\Reverse\FreeMoteToolkit\lab'
    os.makedirs(output_directory_path, exist_ok=True)
    file_paths = glob.glob(os.path.join(input_directory_path, '*.ks'))
    if os.path.exists("1111.txt"):
        os.remove("1111.txt")
    for file_path in file_paths:
        main(file_path, output_directory_path)