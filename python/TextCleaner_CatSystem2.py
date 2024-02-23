import zlib
import os
import re
from glob import glob

def decompress(file_path):
    try:
        with open(file_path, 'rb') as file:
            header = file.read(8)
            if header.decode('cp932') == 'CatScene':
                file.seek(8, 1)
                compressed_data = file.read()
                decompressed_data = zlib.decompress(compressed_data)
                return decompressed_data
            else:
                print("File header does not match 'CatScene'.")
    except Exception as e:
        print(f"Error processing file: {e}")

def main(file_path, output_dir, debug_mode=False):
    hex_str = decompress(file_path).hex()
    header_hex = 'initialize_header'.encode('cp932').hex()
    start_index = hex_str.find(header_hex)
    if start_index == -1:
        return
    start_index += len(header_hex)
    parts = hex_str[start_index:].split("0001")

    results = []
    for i, part in enumerate(parts):
        if part.startswith("3070636d"): # 30 pcm
            audio = bytes.fromhex(part[10:]).decode('cp932')

            if i + 1 < len(parts) and parts[i + 1].startswith("21"): # 21 speaker
                speaker = bytes.fromhex(parts[i + 1][2:]).decode('cp932')

                if i + 2 < len(parts):
                    text = ""
                    for j in range(i + 2, len(parts)):
                        if not parts[j].startswith("20"): # 20 string
                            text =  re.sub(r'\[([^]/]*)/([^]]*)\]', r'\1', text)
                            text = text.replace('」', '').replace('「', '').replace('』', '').replace('『', '').replace('（', '').replace( '）', '').replace('\\@', '').replace('\\n', '').replace('♪', '')
                            results.append({'speaker': speaker, 'audio': audio, 'text': text})
                            break
                        if parts[j].startswith("20"):
                            text += bytes.fromhex(parts[j][2:]).decode('cp932')
    
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
    input_dir = r"E:\Dataset\FuckGalGame\Windmill Oasis\Happiness! 2 樱花盛典\script"
    output_dir = r"E:\Dataset\FuckGalGame\Windmill Oasis\Happiness! 2 樱花盛典"
    debug_mode = True
    
    file_paths = glob(f"{input_dir}/**/*.cst", recursive=True)
    os.makedirs(output_dir, exist_ok=True)

    for file_path in file_paths:
        main(file_path, output_dir, debug_mode=debug_mode)