import re
import os
import json
import zlib
import argparse
from tqdm import tqdm

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"E:\Dataset\FuckGalGame\Windmill Oasis\Witch's Garden\script")
    parser.add_argument("-op", type=str, default=r'D:\AI\Audio_Tools\python\1.json')
    return parser.parse_args(args=args, namespace=namespace)

def text_cleaning(text):
    text =  re.sub(r'\[([^]/]*)/([^]]*)\]', r'\1', text)
    text = re.sub(r'\\(?!w0)[a-zA-Z0-9]{2}', '', text)
    text = re.sub(r'\\w0;.*', '', text)
    text = text.replace('」', '').replace('「', '').replace('』', '').replace('『', '').replace('（', '').replace( '）', '')
    text = text.replace('\\@', '').replace('\\n', '').replace('♪', '').replace('　', '').replace('"', '')
    return text

def decompress(file_path):
        with open(file_path, 'rb') as file:
            header = file.read(8)
            if header.decode('cp932') == 'CatScene':
                file.seek(8, 1)
                compressed_data = file.read()
                decompressed_data = zlib.decompress(compressed_data)
                return decompressed_data

def main(JA_dir, op_json):
    filelist = []
    for root, dirs, files in os.walk(JA_dir):
        for file in files:
            if file.endswith(".cst"):
                filelist.append(os.path.join(root, file))
    results = []

    for filename in tqdm(filelist):
        hex_str = decompress(filename).hex()
        parts = hex_str.split("0001")

        for i, part in enumerate(parts):
            if part.startswith("3070636d"): # 30 pcm
                Voice = bytes.fromhex(part[10:]).decode('cp932') + ".ogg"
                Voice = Voice.replace(' ', '')

                if i + 1 < len(parts) and parts[i + 1].startswith("21"): # 21 speaker
                    Speaker = bytes.fromhex(parts[i + 1][2:]).decode('cp932')
                    Speaker = Speaker.replace('“', '').replace('”', '').split('＠')[0]

                    if i + 2 < len(parts):
                        Text = ""
                        for j in range(i + 2, len(parts)):
                            if not parts[j].startswith("20"): # 20 string
                                Text = text_cleaning(Text)
                                results.append((Speaker, Voice, Text))
                                break
                            if parts[j].startswith("20"):
                                Text += bytes.fromhex(parts[j][2:]).decode('cp932')

    with open(op_json, mode='w', encoding='utf-8') as file:
        seen = set()
        json_data = []
        for Speaker, Voice, Text in results:
            if (Speaker, Voice, Text) not in seen:
                seen.add((Speaker, Voice, Text))
                json_data.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
        json.dump(json_data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    args = parse_args()
    main(args.JA, args.op)