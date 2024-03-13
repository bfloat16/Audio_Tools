import os
import re
from glob import glob

def main(file_path, output_dir, debug_mode=False):
    with open(file_path, 'rb') as f:
        file_byte = f.read()
    results = []
    for i in range(0, len(file_byte)):
        if file_byte[i:i + 5] == b'\x28\x63\x68\x61\x72':
            eng_name = []
            for a in range(i + 5, len(file_byte)):
                if file_byte[a] == 0:
                    break
                eng_name.append(file_byte[a])
            eng_name = bytes(eng_name).decode('cp932')
                
            i = a + 1
            audio = []
            for a in range(i, len(file_byte)):
                if file_byte[a] == 0:
                    break
                audio.append(file_byte[a])
            audio = bytes(audio).decode('cp932')
            
            i = a + 1
            speaker = []
            for a in range(i, len(file_byte)):
                if file_byte[a:a + 3] == b'\x25\x4c\x43' or file_byte[a:a + 3] == b'\x25\x4c\x46':
                    while True:
                        if file_byte[a + 3] == 0:
                            break
                        speaker.append(file_byte[a + 3])
                        a += 1
                    break
            speaker = bytes(speaker).decode('cp932')
            if speaker == '' or speaker == '？？？':
                i = a + 4
                continue

            i = a + 4
            text = []
            for a in range(i, len(file_byte)):
                if file_byte[a: a + 5] == b'\x63\x68\x61\x72\x00':
                    while True:
                        if file_byte[a + 5: a + 7] == b'\x25\x50' or file_byte[a + 5: a + 7] == b'\x25\x4b':
                            break
                        text.append(file_byte[a + 5])
                        a += 1
                    break
            i = a + 6
            text = bytes(text).decode('cp932')
            text = re.sub(r'%XS..', '', text)
            text = re.sub(r'\{[^:]*:([^}]*)\}', r'\1', text) # 用后面的换
            if '・' in text:
                text = re.sub(r'\{([^;]*);[^}]*\}', r'\1', text) # 用前面的换

            text = re.sub(r'\{([^;]*);[^}]*\}', r'\1', text) # 用前面的换

            text = re.sub(r'%XE|%K|「|」|『|』|（|）|\(|\)|\\n|　|', '', text)
            if text == '':
                print(f"Empty text found in {audio} from {file_path}")

            results.append({'audio': audio, 'speaker': speaker, 'text': text})

    subdir_path = file_path.split('\\')[-2]

    for item in results:
        if debug_mode:
            debug_text = os.path.join(output_dir, f"{subdir_path}_debug.txt")
            with open(debug_text, 'a', encoding='utf-8') as f:
                f.write(f"{item['audio']}|{item['speaker']}|{item['text']}\n")
        else:
            text_dir = os.path.join(output_dir, subdir_path, item['speaker'])
            text_path = os.path.join(output_dir, subdir_path, item['speaker'], f"{item['audio'].replace('.ogg', '.txt')}")
            os.makedirs(text_dir, exist_ok=True)
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(item['text'])

if __name__ == '__main__':
    input_dir = r"E:\Dataset\FuckGalGame\ensemble"
    output_dir = r"C:\Users\bfloat16\Desktop"
    debug_mode = True
    
    file_paths = glob(f"{input_dir}/**/*.ws2", recursive=True)

    for file_path in file_paths:
        main(file_path, output_dir, debug_mode=debug_mode)