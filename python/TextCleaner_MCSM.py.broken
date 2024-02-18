import os
import re
from glob import glob

def find_audio(sequence):
    for i in range(0, len(sequence) - 8 + 1, 2):
        subseq = sequence[i:i + 8]
        if sequence.find(subseq, i + 8) != -1:
            return subseq
        
def main(file_path, output_dir, debug_mode=False):
    print(file_path)
    with open(file_path, 'rb') as file:
        file_content = file.read()
    hex = file_content.hex()

    parts = re.split(r'080{6}.{2}.{2}0{4}080{14}', hex) # 切成 None Audio None Audio None Speaker None Text None /n

    main_parts = []
    target = bytes([
        0x2C, 0x00, 0x00, 0x00, 0x14, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x27, 0xAD, 0xEE, 0x2F, 
        0x6B, 0x0D, 0x9A, 0x63, 0x00, 0x00, 0x00, 0x00, 0x14, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x27, 0xAD, 0xEE, 0x2F, 0x6B, 0x0D, 0x9A, 0x63, 0x02, 0x00, 0x00, 0x00, 
        0xAF, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00
        ])
    for i, part in enumerate(parts):
        if i == 0:
            part = part[40:]
        if target.hex() not in part:
            main_parts.append(part)

    results = []
    for i, main_part in enumerate(main_parts):
        sub_parts = re.split(r'0{8}0c0{6}.{16}0c0{6}.{16}080{22}.{2}0{6}.{2}0{6}.{2}0{6}', main_part) # 切成 None Audio None Audio | Speaker None Text None

        for j, sub_part in enumerate(sub_parts):
            if j == 0:
                print(sub_part)
                audio_hex = find_audio(sub_part)
                audio = int(''.join(reversed([audio_hex[i:i+2] for i in range(0, len(audio_hex), 2)])), 16) # hex大端序转uint32小端序

            if j == 1:
                subsub_parts = re.split(r'(?!00).{2}0{6}(?!00).{2}0{6}', sub_part)
                if len(subsub_parts[0]) == 0:
                    continue
                print("0", subsub_parts[0])
                print("1", subsub_parts[1])
                speaker = bytes.fromhex(subsub_parts[0]).decode('utf-8')
                text = bytes.fromhex(subsub_parts[1]).decode('utf-8')
                text = re.sub(r'\{[^}]*\}', '', text)
                text = re.sub(r'\[[^\]]*\]', '', text)
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

if __name__ == "__main__":
    input_dir = r"E:\Dataset\ttarch2\MinecraftStoryMode Season1"
    output_dir = r"D:\2"
    debug_mode = True
    
    file_paths = glob(f"{input_dir}/**/*.landb", recursive=True)
    file_paths = [file for file in file_paths if "env" in file and "english" in file]

    for file_path in file_paths:
        main(file_path, output_dir, debug_mode=debug_mode)