import re
import json
import chardet
import argparse
from tqdm import tqdm
from glob import glob

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"E:\Dataset\FuckGalGame\ASa Project\Koibana Ren'ai - Mini Fandisk - After Festival\script")
    parser.add_argument("-op", type=str, default=r'D:\AI\Audio_Tools\python\1.json')
    parser.add_argument("-ft", type=int, default=1)
    return parser.parse_args(args=args, namespace=namespace)

def guess_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    return encoding

def text_cleaning_01(text):
    text = re.sub(r"\[([^\]]+?)'[^]]+\]", r'\1', text)
    text = re.sub(r"\['([^']+?) text=\"[^\"]+?\"\]", r"\1", text)
    text = re.sub(r"＃\([^()]+\) ", "", text)
    text = text.replace('[r]', '').replace('[np]', '')
    text = text.replace('『', '').replace('』', '').replace('「', '').replace('」', '').replace('（', '').replace('）', '')
    text = text.replace('　', '')
    text = re.sub(r"\[[^\]]*\]", '', text)
    return text

def text_cleaning_02(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = text.replace('『', '').replace('』', '').replace('「', '').replace('」', '').replace('（', '').replace('）', '')
    text = text.replace('　', '')
    return text

def main(JA_dir, op_json, force_type):
    filelist = glob(f"{JA_dir}/**/*.ks", recursive=True)
    results = []
    for filename in tqdm(filelist):
        with open(filename, 'r', encoding=guess_encoding(filename)) as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]
        for i, line in enumerate(lines):
            if force_type == 0:
                if line.startswith(';'):
                    continue
                if 'rt=' in line:
                    match = re.findall(r'@nm\s+t="([^"]*)"\s+rt="([^"]*)"\s+s=(.*)$', line)
                    if match:
                        match = match[0]
                        Speaker = match[1]
                        Voice = match[2]
                        tmp_result = []
                        for j in range(i + 1, len(lines)):
                            if lines[j].startswith(';'):
                                continue
                            if "[np]" in lines[j]:
                                tmp_result.append(lines[j])
                                Text = ''.join(tmp_result)
                                Text = text_cleaning_01(Text)
                                break
                            if "[r]" in lines[j]:
                                tmp_result.append(lines[j])
                        results.append((Speaker, Voice, Text))
                else:
                    match = re.findall(r'@nm\s+t="([^"]*)"\s+s=(.*)$', line)
                    if match:
                        match = match[0]
                        Speaker = match[0]
                        Voice = match[1]
                        tmp_result = []
                        for j in range(i + 1, len(lines)):
                            if lines[j].startswith(';'):
                                continue
                            if "[np]" in lines[j]:
                                tmp_result.append(lines[j])
                                Text = ''.join(tmp_result)
                                Text = text_cleaning_01(Text)
                                break
                            if "[r]" in lines[j]:
                                tmp_result.append(lines[j])
                        results.append((Speaker, Voice, Text))

            if force_type == 1:
                match = re.findall(r'\[([^\s\]]+)\s+vo=["]?([^"\s\]]+)["]?', line)
                if match:
                    match = match[0] 
                    Speaker = match[0]
                    Voice = match[1]
                    Text = lines[i + 1]
                    Text = text_cleaning_02(Text)
                    results.append((Speaker, Voice, Text))

    with open(op_json, mode='w', encoding='utf-8') as file:
        seen = set()
        json_data = []
        for Speaker, Voice, Text in results:
            record = (Speaker, Voice, Text)
            if record not in seen:
                seen.add(record)
                json_data.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
        json.dump(json_data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    args = parse_args()
    main(args.JA, args.op, args.ft)