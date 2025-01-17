import re
import json
import chardet
import argparse
from tqdm import tqdm
from glob import glob

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"D:\Fuck_galgame\scenario")
    parser.add_argument("-op", type=str, default=r'D:\Fuck_galgame\index.json')
    parser.add_argument("-ft", type=int, default=2)
    return parser.parse_args(args=args, namespace=namespace)

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
    text = text.replace('　', '').replace('／', '')
    return text

def guess_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    return encoding

def main(JA_dir, op_json, force_type):
    filelist = glob(f"{JA_dir}/**/*.ks", recursive=True)
    filelist += glob(f"{JA_dir}/**/*.txt", recursive=True)
    filelist += glob(f"{JA_dir}/**/*.ms", recursive=True)
    results = []
    for filename in tqdm(filelist):
        try:
            with open(filename, 'r', encoding=guess_encoding(filename)) as file:
                lines = file.readlines()
        except (UnicodeDecodeError, TypeError):  # TypeError 以防 guess_encoding 返回 None 或无效编码
            with open(filename, 'r', encoding='cp932') as file:
                lines = file.readlines()
        
        lines = [line.strip() for line in lines]

        for i, line in enumerate(lines):
            if line.startswith(';'):
                continue
            match force_type:
                case 0:
                    if 'rt=' in line:
                        match = re.findall(r'@nm\s+t="([^"]*)"\s+rt="([^"]*)"\s+s=(.*)$', line)
                        if match:
                            skip = False
                            match = match[0]
                            Speaker = match[1]
                            Voice = match[2]
                            tmp_result = []
                            for j in range(i + 1, len(lines)):
                                if lines[j].startswith(';'):
                                    print(f"\nWarning: {filename} {lines[j]}")
                                    skip = True
                                    break
                                if "[np]" in lines[j]:
                                    tmp_result.append(lines[j])
                                    Text = ''.join(tmp_result)
                                    Text = text_cleaning_01(Text)
                                    break
                                if "[r]" in lines[j]:
                                    tmp_result.append(lines[j])
                            if not skip:
                                results.append((Speaker, Voice, Text))
                    else:
                        match = re.findall(r'@nm\s+t="([^"]*)"\s+s=(.*)$', line)
                        if match:
                            skip = False
                            match = match[0]
                            Speaker = match[0]
                            Voice = match[1]
                            tmp_result = []
                            for j in range(i + 1, len(lines)):
                                if lines[j].startswith(';') and not lines[j].startswith(';//'):
                                    print(f"\nWarning: {filename} {lines[j]}")
                                    skip = True
                                    break
                                if "[np]" in lines[j]:
                                    tmp_result.append(lines[j])
                                    Text = ''.join(tmp_result)
                                    Text = text_cleaning_01(Text)
                                    break
                                if "[r]" in lines[j]:
                                    tmp_result.append(lines[j])
                            if not skip:
                                results.append((Speaker, Voice, Text))

                case 1:
                    match = re.findall(r'\[([^\s\]]+)\s+vo=["]?([^"\s\]]+)["]?', line)
                    if match:
                        match = match[0] 
                        Speaker = match[0]
                        Voice = match[1]
                        Text = lines[i + 1]
                        Text = text_cleaning_02(Text)
                        results.append((Speaker, Voice, Text))

                case 2:
                    match = re.findall(r'@Talk\s+name=(.*?)\s+voice=(.*?)(?=\s|$)', line)
                    if match:
                        Speaker, Voice = match[0]
                        Speaker = Speaker.split('/')[0]
                        Voice = Voice.split('/')[0]
                        tmp_result = []
                        for j in range(i + 1, len(lines)):
                            if lines[j].startswith('@'):
                                Text = ''.join(tmp_result)
                                Text = text_cleaning_02(Text)
                                results.append((Speaker, Voice, Text))
                                break
                            else:
                                tmp_result.append(lines[j])

                case 3:
                    match1 = re.findall(r'[;@]?@(\S+)\s+voice="([^"]+)"', line)
                    if match1:
                        Speaker, Voice = match1[0]
                        Speaker = Speaker.split('/')[0]
                        Voice = Voice.lower()
                        match2 = re.findall(r'[;]?\s*【[^】]+】(.+)', lines[i + 1])
                        if match2:
                            Text = match2[0]
                            Text = text_cleaning_02(Text)
                            results.append((Speaker, Voice, Text))
                        elif lines[i + 2].startswith('['):
                            Text = lines[i + 1]
                            Text = text_cleaning_02(Text)
                            results.append((Speaker, Voice, Text))
                            

                case 4:
                    match = re.findall(r"\[(.*?)\s+voice=(.*?)\]", line)
                    if match:
                        match = match[0]
                        Speaker = match[0]
                        Voice = match[1]
                        Text = lines[i + 2]
                        Text = text_cleaning_02(Text)
                        results.append((Speaker, Voice, Text))

                case 5:
                    match1 = re.search(r'\[Voice\s+file=([^\s]+)\s+id=([^\]]+)\]', line)
                    tmp_voice = []
                    if match1:
                        tmp_voice.append(match1.group(1))
                        for j in range(i + 1, len(lines)):
                            match2 = re.search(r'\[Voice\s+file=([^\s]+)\s+id=([^\]]+)\]', lines[j])
                            match3 = re.search(r'\[Talk\s+name=([^\]]+)\]', lines[j])
                            if match2:
                                tmp_voice.append(match2.group(1))
                            elif match3:
                                elements = re.split(r"[＆&]", match3.group(1))
                                tmp_result = []
                                for n in range(j + 1, len(lines)):
                                    if '[Hitret]' in lines[n]:
                                        Text = ''.join(tmp_result)
                                        Text = text_cleaning_02(Text)
                                        for Voice, Speaker in zip(tmp_voice, elements):
                                            results.append((Speaker, Voice, Text))
                                        break
                                    else:
                                        tmp_result.append(lines[n])
                                break
                        continue

                    match4 = re.search(r'\[Voice\s+file=([^\]]+)\]', line)
                    if match4:
                        Voice = match4.group(1)
                        for j in range(i + 1, len(lines)):
                            match5 = re.search(r'\[Talk\s+name=([^\]]+)\]', lines[j])
                            if match5:
                                Speaker = match5.group(1)
                                tmp_result = []
                                for n in range(j + 1, len(lines)):
                                    if '[Hitret]' in lines[n]:
                                        Text = ''.join(tmp_result)
                                        Text = text_cleaning_02(Text)
                                        results.append((Speaker, Voice, Text))
                                        break
                                    else:
                                        tmp_result.append(lines[n])
                                break

    with open(op_json, mode='w', encoding='utf-8') as file:
        seen = set()
        json_data = []
        for Speaker, Voice, Text in results:
            if Voice.lower() not in seen:
                seen.add(Voice.lower())
                json_data.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
        json.dump(json_data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    args = parse_args()
    main(args.JA, args.op, args.ft)