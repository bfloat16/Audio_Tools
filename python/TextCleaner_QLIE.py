import re
import os
from glob import glob

def main(file_path, output_directory_path, debug_mode=False):
    results = []
    with open(file_path, 'r', encoding='utf-16-le') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]

    for i, line in enumerate(lines):
        if i < len(lines) - 2:
            speaker_match = re.search(r'【(.*?)】', line)
            if speaker_match:
                speaker = speaker_match.group(1)
                speaker = speaker.replace('＠？？？', '')
                if re.match(r'^％', lines[i + 1]):
                    audio_file = re.search(r'％(\w+)', lines[i + 1]).group(1)
                    dialogue = lines[i + 2]
                    dialogue = dialogue.replace('「', '').replace('」', '').replace('〈ハ〉', '')
                    if dialogue == '':
                        continue
                    results.append({'speaker': speaker, 'audio': audio_file, 'text': dialogue})

    subdir_path = file_path.split('\\')[-2]

    for item in results:
        if debug_mode:
            debug_text = os.path.join(output_directory_path, f"{subdir_path}_debug.txt")
            with open(debug_text, 'a', encoding='utf-8') as f:
                f.write(f"{item['audio']}|{item['speaker']}|{item['text']}\n")
        else:
            text_dir = os.path.join(output_directory_path, subdir_path, item['speaker'])
            text_path = os.path.join(text_dir, f"{item['audio']}.txt")
            os.makedirs(text_dir, exist_ok=True)
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(item['text'])

if __name__ == '__main__':
    in_dir = r'C:\Users\bfloat16\Downloads\IBUN01_DL\setup\appdata\scenario'
    out_dir = r'C:\Users\bfloat16\Downloads\IBUN01_DL\setup\appdata\scenario'
    debug_mode = True

    file_paths = glob(f"{in_dir}/*.s", recursive=True)
    for file_path in file_paths:
        main(file_path, out_dir, debug_mode=debug_mode)