import re
import os
from glob import glob

def match_audio(line):
    return re.search(r"KOE\((\d{9}),\d{3}\)", line).group(1)

def match_speaker(line):
    return re.search(r"【(.+?)】", line).group(1).replace('【', '').replace('】', '').replace('@', '')

def match_text(line):
    return re.search(r"「(.+?)」", line).group(1).replace('「', '').replace('」', '').replace('\\n', '')

def main(file_path, output_dir, debug_mode=False):
    with open(file_path, 'r', encoding='cp932') as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]

    results = []
    for i, line in enumerate(lines):
        if re.search(r"KOE\(\d+,\d+\)【.*?】「.*?」R", line):
            speaker = match_speaker(line)
            audio = match_audio(line)
            audio = f"z{audio[:4]}#{audio[4:]}"
            text = match_text(line)
            results.append({'speaker': speaker, 'audio': audio, 'text': text})

    subdir_path = file_path.split('\\')[-2]

    for item in results:
        if debug_mode:
            debug_text = os.path.join(output_dir, f"debug.txt")
            with open(debug_text, 'a', encoding='utf-8') as f:
                f.write(f"{item['audio']}|{item['speaker']}|{item['text']}\n")
        else:
            text_dir = os.path.join(output_dir, item['speaker'])
            text_path = os.path.join(output_dir, item['speaker'], f"{item['audio']}.txt")
            os.makedirs(text_dir, exist_ok=True)
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(item['text'])

if __name__ == '__main__':
    input_dir = r"E:\Dataset\FuckGalGame\key\Angel Beats! -1st beat-\script"
    output_dir = r"E:\Dataset\FuckGalGame\key\Angel Beats! -1st beat-\lab"
    debug_mode = True
    
    file_paths = glob(f"{input_dir}/**/*.ss", recursive=True)
    os.makedirs(output_dir, exist_ok=True)

    for file_path in file_paths:
        main(file_path, output_dir, debug_mode=debug_mode)