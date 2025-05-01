import re
import json
import argparse
from tqdm import tqdm
from glob import glob

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"D:\Fuck_galgame\scenario")
    parser.add_argument("-op", type=str, default=r'D:\Fuck_galgame\index.json')
    parser.add_argument("-ft", type=int, default=0)
    return parser.parse_args(args=args, namespace=namespace)

def text_cleaning(text):
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r"\[.*?,(.*?),.*?\]", r"\1", text)
    text = text.replace('」', '').replace('「', '').replace('（', '').replace('）', '').replace('『', '').replace('』', '')
    text = text.replace('〈ハ〉', '').replace('　', '')
    return text

def main(JA_dir, op_json, force_type):
    filelist = glob(f"{JA_dir}/**/*.s", recursive=True)
    seen_voices = set()
    results = []
    for filename in tqdm(filelist):
        with open(filename, 'r', encoding='utf-16-le') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]

        if force_type == 0:
            for i, line in enumerate(lines):
                if i < len(lines) - 2:
                    Speaker_match = re.search(r'【(.*?)】', line)
                    if Speaker_match:
                        Speaker_cuts = Speaker_match.group(1)
                        Speaker_cuts = Speaker_cuts.split('＠')
                        for Speaker_cut in Speaker_cuts:
                            if Speaker_cut != '？？？' and Speaker_cut != 'none' and Speaker_cut != '':
                                Speaker = Speaker_cut
                        if re.match(r'^％', lines[i + 1]):
                            Voice = re.search(r'％(\w+)', lines[i + 1]).group(1)
                            Voice = Voice.lower()
                            Text = lines[i + 2]
                            Text = text_cleaning(Text)
                            if Text == '':
                                continue
                            if Voice in seen_voices:
                                print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                            else:
                                results.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
                                seen_voices.add(Voice)

        if force_type == 1:
            for i, line in enumerate(lines):
                if i < len(lines) - 2:
                    Voice_match = re.search(r'^％(\w+)', line)
                    next_line_match = re.match(r'^【', lines[i + 1])
                    if Voice_match and next_line_match:
                        Voice = Voice_match.group(1)
                        Speaker_cuts = re.search(r'【(.*?)】', lines[i + 1]).group(1)
                        Speaker_cuts = Speaker_cuts.split('＠')
                        for Speaker_cut in Speaker_cuts:
                            if Speaker_cut != '？？？' and Speaker_cut != 'none' and Speaker_cut != '':
                                Speaker = Speaker_cut
                        Text = lines[i + 2]
                        Text = text_cleaning(Text)
                        if Text == '':
                            continue
                        results.append((Speaker, Voice, Text))

        if force_type == 2:
            for i, line in enumerate(lines):
                if bool(re.match(r'^(?![Nn][Oo][Nn][Ee])[A-Za-z]', line)):
                    Voice, Speaker, Text = line.split(',', 2)
                    Voice = Voice.lower()
                    if '＠' in Speaker:
                        Speaker = Speaker.split('＠')[1]
                    if Speaker == '？？？' or Speaker == 'none' or Speaker == '':
                        continue
                    Text = text_cleaning(Text)

                    if Voice in seen_voices:
                        print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                    else:
                        results.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
                        seen_voices.add(Voice)  # 将 Voice 添加到已处理的集合中


    with open(op_json, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    args = parse_args()
    main(args.JA, args.op, args.ft)