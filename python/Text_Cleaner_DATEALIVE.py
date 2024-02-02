import os
import re
from glob import glob

def get_file(path):
    filelist = glob(f"{path}/**/*.bin", recursive=True)
    return filelist

def read_file(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()
    return data

def process(file_path):
    for file in get_file(file_path):
        script = read_file(file)
        script_matchs = re.findall(r'\x00([A-Za-z0-9_]+)\x00「(.*?)」', script)
        if script_matchs != []:
            for script_match in script_matchs:
                with open("1111.txt", 'a', encoding='utf-8') as output_file:
                    output_file.write(script_match[0] + '|' + script_match[1] + '\n')

if __name__ == '__main__':
    file_path = r"D:\Reverse\_GalGame\DALTools\Script"
    process(file_path)