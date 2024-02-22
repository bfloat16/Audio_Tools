import re
import os
from glob import glob

def match_audio(line):
    return re.findall(r'file="([a-zA-Z0-9_]+)"', line)[0]

def match_speaker(line):
    return re.findall(r'ch="([^"]+)"', line)[0]

def match_text(line):
    if re.findall(r'"(.*?)"', line):
        return re.findall(r'"(.*?)"', line)[0]

def main(file_path, output_dir, debug_mode=False):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]

    results = []
    in_text_table = False
    in_sub_text_table = False
    for i, line in enumerate(lines):
        if line == "label={":
            break
        if line == "text={":
            in_text_table = True
        if in_text_table:
            if "[" in line and "]" in line:
                in_sub_text_table = True
        if in_text_table and in_sub_text_table:
            if lines[i + 1] == "ja={":
                in_sub_text_table = False
            if line == "vo={":
                audio = match_audio(lines[i + 1])
                speaker = match_speaker(lines[i + 1])
                if lines[i + 4] == "ja={":
                    text = ""
                    for j in range(i + 5, len(lines)):
                        if lines[j] == "},":
                            results.append({'speaker': speaker, 'audio': audio, 'text': text})
                            in_sub_text_table = False
                            break
                        if "rt2" not in lines[j]:
                            sub_text = match_text(lines[j])
                            if sub_text is not None:
                                text += sub_text.replace('」', '').replace('「', '').replace('（', '').replace( '）', '').replace('●', '')

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
    input_dir = r"E:\Dataset\FuckGalGame\Wonder Fool\Yukiiro Sign\script"
    output_dir = r"E:\Dataset\FuckGalGame\Wonder Fool\Yukiiro Sign"
    debug_mode = True
    
    file_paths = glob(f"{input_dir}/**/*.ast", recursive=True)
    os.makedirs(output_dir, exist_ok=True)

    for file_path in file_paths:
        main(file_path, output_dir, debug_mode=debug_mode)