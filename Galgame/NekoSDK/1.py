import re
import json
import argparse
from glob import glob
from tqdm import tqdm

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"D:\Fuck_galgame\script")
    parser.add_argument("-op", type=str, default=r'D:\Fuck_galgame\index.json')
    return parser.parse_args(args=args, namespace=namespace)

def text_cleaning(text):
    text = text.replace('『', '').replace('』', '').replace('「', '').replace('」', '').replace('（', '').replace('）', '')
    text = text.replace('　', '').replace('\n', '').replace('\u3000', '')
    return text

def main(JA_dir, op_json):
    filelist = glob(f"{JA_dir}/**/*.txt", recursive=True)
    results = []
    for filename in tqdm(filelist):
        with open(filename, 'rb') as file:
            data = file.read()

        i = 0
        while i < len(data):
            if data[i: i + 14] == b'\x5B\x83\x65\x83\x4C\x83\x58\x83\x67\x95\x5C\x8E\xA6\x5D': # [テキスト表示]
                i += 14

                segment = bytearray()
                while i < len(data) and data[i: i + 2] != b'\x0A\x00':
                    segment.append(data[i])
                    i += 1
                decoded_segment = segment.decode('cp932', errors='ignore')
                match = re.findall(r'^\s*(\S+)\s+voice\\([\w\d_]+\.ogg)\n(.+)$', decoded_segment, re.DOTALL)
                if match:
                    match = match[0]
                    Speaker = match[0]
                    Voice = match[1].replace('.ogg', '')
                    if 'may1_0008' in Voice:
                        print(f"Error: {filename}, {i}")
                    Text = match[2]
                    Text = text_cleaning(Text)
                    results.append((Speaker, Voice, Text))
            else:
                i += 1

    with open(op_json, mode='w', encoding='utf-8') as file:
        seen = set()
        json_data = []
        for Speaker, Voice, Text in results:
            if Voice not in seen:
                seen.add(Voice)
                json_data.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
        json.dump(json_data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    args = parse_args()
    main(args.JA, args.op)