import re
import os
from glob import glob

def match_audio(line):
    return re.search(r'pushint\s+(\d+)', line)

def match_speaker(line):
    return re.search(r'call SPEAK_(\d+)_\s+#\s*([^\n]+)', line)

def match_text(line):
    return re.search(r'pushstring\s+(.+)', line)

def main(file_path, output_dir, debug_mode=False):
    with open(file_path, 'r', encoding='cp932') as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]

    results = []
    skip = -1  # 已经处理过的行

    for i, line in enumerate(lines):
        if i <= skip: # 跳过处理过的行
            continue

        audio = match_audio(line)
        if audio:
            if i + 1 < len(lines) and not re.search(r'pushtrue', lines[i + 1]):
                skip = i + 1
                continue
            if i + 2 < len(lines) and not re.search(r'call SPEAK_\w+_', lines[i + 2]):
                skip = i + 2
                continue
            else:
                audio = int(audio.group(1))
                speaker = match_speaker(lines[i + 2]).group(2)
                text = match_text(lines[i + 3])
                if text:
                    text = text.group(1)
                else:
                    skip = i + 3
                    continue
                skip = i + 3  # 更新skip为已经处理过的行
                results.append({'speaker': speaker, 'audio': audio, 'text': text})

    subdir_path = file_path.split('\\')[-2]

    for item in results:
        if debug_mode:
            debug_text = os.path.join(output_dir, f"{subdir_path}_debug.txt")
            with open(debug_text, 'a', encoding='utf-8') as f:
                f.write(f"{item['audio']:09d}|{item['speaker']}|{item['text']}\n")
        else:
            text_dir = os.path.join(output_dir, subdir_path, item['speaker'])
            text_path = os.path.join(output_dir, subdir_path, item['speaker'], f"{item['audio']:09d}.txt")
            os.makedirs(text_dir, exist_ok=True)
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(item['text'])

if __name__ == '__main__':
    input_dir = r"E:\FuckGalGame\FAVORITE"
    output_dir = r"D:\2"
    debug_mode = False
    
    file_paths = glob(f"{input_dir}/**/script.txt", recursive=True)

    for file_path in file_paths:
        main(file_path, output_dir, debug_mode=debug_mode)