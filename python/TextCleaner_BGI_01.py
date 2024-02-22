import os
import re
from glob import glob
from python.TextCleaner_BGI_00 import BGI

def main(file_path, output_dir, debug_mode=False):
    results = []
    all_texts = BGI(file_path)
    lines = all_texts.split('\n')
    for i, line in enumerate(lines):
        if line == "Voice":
            audio = lines[i - 1]
            if audio == "":
                continue
            speaker = lines[i + 1]
            text = lines[i + 2]
            text = text.replace('「', '').replace('」', '').replace('（', '').replace('）', '')
            text = re.sub(r"<.*?>", "", text)
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
    input_dir = r"E:\Dataset\FuckGalGame\AUGUST\Aiyoku no Eustia\script"
    output_dir = r"E:\Dataset\FuckGalGame\AUGUST\Aiyoku no Eustia"
    debug_mode = True
    
    file_paths = glob(f"{input_dir}/**/*", recursive=True)
    os.makedirs(output_dir, exist_ok=True)

    for file_path in file_paths:
        main(file_path, output_dir, debug_mode=debug_mode)