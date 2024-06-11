import re
import json
import argparse
from glob import glob
from tqdm import tqdm

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"E:\Dataset\FuckGalGame\PULLTOP\Miagete Goran, Yozora no Hoshi o\script")
    parser.add_argument("-op", type=str, default=r'D:\AI\Audio_Tools\python\1.json')
    return parser.parse_args(args=args, namespace=namespace)

def text_cleaning(text):
    text = re.sub(r'\{([^:]*):[^}]*\}|\{(.*?);.*?\}', r'\1', text)
    text = re.sub(r'%\w+', '', text)
    text = text.replace('『', '').replace('』', '').replace('「', '').replace('」', '').replace('（', '').replace('）', '')
    text = text.replace('　', '').replace('\\n', '')
    return text

def main(JA_dir, op_json):
    filelist = glob(f"{JA_dir}/**/*.ws2", recursive=True)
    dialogue_start0 = False
    dialogue_start1 = False
    results = []
    for filename in tqdm(filelist):
        with open(filename, 'rb') as file:
            data = file.read()

        i = 0
        while i < len(data):
            if data[i: i + 2] == b'\x2E\x28':
                i += 2
                segment = bytearray()
                while i < len(data) and data[i] != 0:
                    segment.append(data[i])
                    i += 1
                decoded_segment = segment.decode('cp932').replace('char', '')
                Speaker_id = decoded_segment
                i += 1
                segment = bytearray()
                while i < len(data) and data[i] != 0:
                    segment.append(data[i])
                    i += 1
                decoded_segment = segment.decode('cp932').replace('OGG', 'ogg')
                Voice = decoded_segment
                dialogue_start0 = True

            if data[i: i + 2] == b'\x15\x25' and dialogue_start0:
                i += 4
                segment = bytearray()
                while i < len(data) and data[i] != 0:
                    segment.append(data[i])
                    i += 1
                decoded_segment = segment.decode('cp932')
                Speaker = text_cleaning(decoded_segment)
                dialogue_start1 = True

            if data[i: i + 4] == b'\x63\x68\x61\x72' and dialogue_start1:
                i += 5  # Skip the sequence and one additional byte
                segment = bytearray()
                while i < len(data) and data[i] != 0:
                    segment.append(data[i])
                    i += 1
                decoded_segment = segment.decode('cp932')
                Text = text_cleaning(decoded_segment)
                dialogue_start0 = False
                dialogue_start1 = False
                results.append((Speaker, Speaker_id, Voice, Text))

            else:
                i += 1

    replace_dict = {}
    for Speaker, Speaker_id, Voice, Text in tqdm(results):
        if Speaker != '？？？' and Speaker != '' and Speaker_id not in replace_dict:
            replace_dict[Speaker_id] = Speaker

    fixed_results = []
    for Speaker, Speaker_id, Voice, Text in tqdm(results):
        if (Speaker == '？？？' or Speaker == '') and Speaker_id in replace_dict:
            fixed_results.append((replace_dict[Speaker_id], Speaker_id, Voice, Text))
        else:
            fixed_results.append((Speaker, Speaker_id, Voice, Text))

    with open(op_json, mode='w', encoding='utf-8') as file:
        seen = set()
        json_data = []
        for Speaker, Speaker_id, Voice, Text in fixed_results:
            if (Speaker, Speaker_id, Voice, Text) not in seen:
                seen.add((Speaker, Speaker_id, Voice, Text))
                json_data.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
        json.dump(json_data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    args = parse_args()
    main(args.JA, args.op)  