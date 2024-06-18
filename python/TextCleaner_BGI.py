import re
import json
import struct
import argparse
from tqdm import tqdm
from glob import glob

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"E:\Dataset\FuckGalGame\Lump of Sugar\Arcana Alchemia\script")
    parser.add_argument("-op", type=str, default=r'D:\AI\Audio_Tools\python\1.json')
    return parser.parse_args(args=args, namespace=namespace)

def BGI(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
    
    data_length = len(data)
    results = []
    
    index_start = data.find(b'\x00\x00\x00\x00\x01\x00\x00\x00')
    
    index_start = index_start + 4
    position = index_start
    while position < data_length:
        if data[position:position + 4] == b'\x03\x00\x00\x00':
            position += 4
            
            offset = data[position:position + 4]
            offset = struct.unpack('<I', offset)[0]
            
            target_position = offset + index_start
            
            if target_position >= data_length:
                break
            string_data = b''
            
            while target_position < data_length:
                byte = data[target_position]
                if byte == 0x00:
                    break
                string_data += bytes([byte])
                target_position += 1
            string = string_data.decode('cp932')
            if '\\' in string:
                continue
            results.append(string)
        else:
            position += 4
    
    return results

def text_cleaning(text):
    text = re.sub(r"<.*?>", "", text)
    text = text.replace('「', '').replace('」', '').replace('（', '').replace('）', '').replace('『', '').replace('』', '')
    text = text.replace('　', '')
    return text

def main(JA_dir, op_json):
    filelist = glob(f"{JA_dir}/**/*", recursive=True)
    results = []

    for filename in tqdm(filelist):
        lines = BGI(filename)
        for i, line in enumerate(lines):
            if line == "_PlayVoice":
                Voice = lines[i - 1]
                if Voice == "":
                    print(filename, i)
                    continue
                if Voice == 'NON_a000102':
                    pass
                Speaker_id = Voice.split('_')[0]
                if lines[i + 1] == lines[i + 3]:
                    Speaker = lines[i + 2]
                    Text = lines[i + 3]
                else:
                    Speaker = lines[i + 1]
                    Text = lines[i + 2]
                Text = text_cleaning(Text)
                results.append((Speaker, Speaker_id, Voice, Text))

    replace_dict = {}
    for Speaker, Speaker_id, Voice, Text in results:
        if Speaker != '？？？' and Speaker_id not in replace_dict:
            replace_dict[Speaker_id] = Speaker

    fixed_results = []
    for Speaker, Speaker_id, Voice, Text in results:
        if Speaker == '？？？' and Speaker_id in replace_dict:
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