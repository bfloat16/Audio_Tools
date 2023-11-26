import re
import json
import glob
import os
import sys

def main(file_path, output_directory_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    pattern = re.compile(r'"voice": "(.*?)"')
    voice_lab_mapping = {}
    for i, line in enumerate(lines):
        match = pattern.search(line)
        if match:
            voice_value = match.group(1)
            voice_value = voice_value.lower() + '.txt'

            lab_value = lines[i - 4] #往上找4行
            lab_value = re.findall(r'"(.*?)"', lab_value) #找到所有的引号里的内容

            if lab_value == []: # 有voice 没有lab，跳过
                continue
            else:
                for value in lab_value:
                    if re.findall(r'「(.*?)', value) != []:
                        lab_value = re.sub(r'[「」]', '', value)
                        break

            if isinstance(lab_value, list): # 有voice 有lab 没有「」，跳过
                continue
            else:
                lab_value = re.sub(r'　', '', lab_value)
                lab_value = re.sub(r'\\\\n', '', lab_value)

                if '9-nine' in file_path.lower():
                    lab_value = re.sub(r'\[.+?\]', '', lab_value)
                    lab_value = re.sub(r'%.+;+', '', lab_value)

                elif 'ginka' in file_path.lower():
                    lab_value = re.sub(r'\[.+?\]', '', lab_value)
                    lab_value = re.sub(r'（.*）', '', lab_value)
                    lab_value = re.sub(r'『|』', '', lab_value)

                elif 'sabbat' in file_path.lower():
                    lab_value = re.sub(r'\[.+?\]', '', lab_value)
                    lab_value = re.sub(r'（|）', '', lab_value)
                    lab_value = re.sub(r'『|』', '', lab_value)
                    lab_value = re.sub(r'%.+;+', '', lab_value)
                    lab_value = re.sub(r'●', '', lab_value)

                if lab_value == '':
                    print(voice_value)
                    print(lines[i - 4])
                    continue

                voice_lab_mapping[voice_value] = lab_value
    '''
    for voice_value, lab_value in voice_lab_mapping.items():
        output_file_path = os.path.join(output_directory_path, f'{voice_value}')
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(lab_value)
    '''
    with open("1111.txt", 'a', encoding='utf-8') as output_file:
        for voice_value, lab_value in voice_lab_mapping.items():
            output_file.write(lab_value + '\n')

if __name__ == '__main__':
    input_directory_path = r'D:\Reverse\FreeMoteToolkit\scn\Sabbat Of The Witch'
    output_directory_path = r'D:\Reverse\FreeMoteToolkit\lab\Sabbat Of The Witch'
    os.makedirs(output_directory_path, exist_ok=True)
    file_paths = glob.glob(os.path.join(input_directory_path, '*.json'))
    if os.path.exists("1111.txt"):
        os.remove("1111.txt")
    for file_path in file_paths:
        main(file_path, output_directory_path)