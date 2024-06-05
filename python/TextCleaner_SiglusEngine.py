import re
import os
import json
import argparse
from glob import glob

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"E:\Dataset\FuckGalGame\catwalkNero\Anastasia to 7-nin no Himegami ~Inmon no Rakuin~\script")
    parser.add_argument("-op", type=str, default=r'D:\AI\Audio_Tools\python\1.json')
    return parser.parse_args(args=args, namespace=namespace)

def match_audio(line):
    return re.search(r"KOE\((\d{9}),\d{3}\)", line).group(1)

def match_speaker(line):
    return re.search(r"【(.+?)】", line).group(1).replace('【', '').replace('】', '').replace('@', '')

def match_text(line):
    return re.search(r"「(.+?)」", line).group(1).replace('「', '').replace('」', '').replace('\\n', '')

def main(JA_dir, op_json):
    filelist = glob(f"{JA_dir}/**/*.ss", recursive=True)
    results = []

    for files in filelist:
        with open(files, 'r', encoding='cp932') as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]

        for i, line in enumerate(lines):
            if re.search(r"KOE\(\d+,\d+\)【.*?】「.*?」R", line):
                Speaker = match_speaker(line)
                Speaker = Speaker.split('＿')[0]
                Speaker = Speaker.split('／')[0]
                Speaker = Speaker.split('/')[0]
                Speaker = Speaker.replace('◎', '').replace('★', '')
                Voice = match_audio(line)
                Voice = f"z{Voice[:4]}#{Voice[4:]}"
                Text = match_text(line)
                Text = re.sub(r'\{[^:]*:([^}]*)\}', r'\1', Text)
                Text = re.sub(r'（[^）]*$', '', Text)
                Text = re.sub(r'『.*?』', '', Text)
                Text = Text.replace('　', '').replace('／／／', '').replace('NLI', '').replace('@heart', '')
                results.append((Speaker, Voice, Text))

    with open(op_json, mode='w', encoding='utf-8') as file:
        json_data = [{'Speaker': Speaker, 'Voice': Voice, 'Text': Text} for Speaker, Voice, Text in results]
        json.dump(json_data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    args = parse_args()
    main(args.JA, args.op)