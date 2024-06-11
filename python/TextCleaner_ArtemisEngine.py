import re
import json
import argparse
from tqdm import tqdm
from glob import glob

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"E:\Dataset\FuckGalGame\Makura\Sakura no Toki -Sakura no Mori no Shita o Ayumu-\script")
    parser.add_argument("-op", type=str, default=r'D:\AI\Audio_Tools\python\1.json')
    return parser.parse_args(args=args, namespace=namespace)

def match_voice(line):
    return re.findall(r'file="(.*?)"', line)[0]

def match_speaker(line):
    return re.findall(r'name\s*=\s*\{\s*"([^",]+)"', line)[0]

def match_text(line):
    if re.findall(r'"(.*?)"', line):
        return re.findall(r'"(.*?)"', line)[0]
    
def text_cleaning(text):
    return text.replace('」', '').replace('「', '').replace('（', '').replace('）', '').replace('●', '').replace('　', '')

def main(JA_dir, op_json):
    filelist = glob(f"{JA_dir}/**/*.ast", recursive=True)
    results = []
    for filename in tqdm(filelist):
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]

        in_text_table = False
        in_sub_text_table = False
        if lines[0] == 'astver = 2.0':
            force_type = 1
        else:
            force_type = 0
            
        for i, line in enumerate(lines):
            if force_type == 0:
                if line == "label={":
                    break
                if line == "text={":
                    in_text_table = True
                if in_text_table:
                    if "[" in line and "]" in line in line:
                        in_sub_text_table = True
                if in_text_table and in_sub_text_table:
                    if lines[i + 1] == "ja={":
                        in_sub_text_table = False
                    if line == "vo={":
                        Voice = match_voice(lines[i + 1])
                        Speaker = match_speaker(lines[i + 3])
                        if lines[i + 4] == "ja={":
                            Text = ""
                            for j in range(i + 5, len(lines)):
                                if lines[j] == "},":
                                    results.append((Speaker, Voice, Text))
                                    in_sub_text_table = False
                                    break
                                if "rt2" not in lines[j]:
                                    sub_text = match_text(lines[j])
                                    if sub_text is not None:
                                        Text += text_cleaning(sub_text)
            elif force_type == 1:
                if line == "text = {":
                    in_text_table = True
                if in_text_table:
                    if lines[i + 1] == "ja = {":
                        in_text_table = False
                        continue
                    if line == "vo = {":
                        Voice = match_voice(lines[i + 1])
                        if lines[i + 3] == "ja = {":
                            Text = ""
                            for j in range(i + 4, len(lines)):
                                Speaker0 = re.findall(r'name\s*=\s*\{\s*"([^",]+)"', lines[j])
                                if Speaker0:
                                    Speaker = Speaker0[0]
                                elif lines[j] == "},":
                                    results.append((Speaker, Voice, Text))
                                    in_text_table = False
                                    break
                                elif "rt2" not in lines[j]:
                                    sub_text = match_text(lines[j])
                                    if sub_text:
                                        Text += text_cleaning(sub_text)
                        else:
                            in_text_table = False

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
    main(args.JA, args.op)