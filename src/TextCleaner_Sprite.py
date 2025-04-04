import json
import argparse
from tqdm import tqdm
from glob import glob

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r'E:\Dataset\FuckGalGame\sprite\Ao no Kanata no Four Rhythm\script')
    parser.add_argument("-op", type=str, default=r'D:\AI\Audio_Tools\python\1.json')
    return parser.parse_args(args=args, namespace=namespace)

def text_cleaning(text):
    text = text.replace('『', '').replace('』', '').replace('「', '').replace('」', '').replace('（', '').replace('）', '').replace('“', '').replace('”', '').replace('≪', '').replace('≫', '')
    text = text.replace('\n', '').replace(r'\n', '').replace(r'　', '').replace('♪', '').replace('♥', '').replace('%r', '')
    return text

def read_bs5(JA_dir, op_json):
    files_original = glob(f"{JA_dir}/**/*.bs5", recursive=True)
    for filename in tqdm(files_original):
        with open(filename, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
        
        result = []
        i = 0
        j = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("voice0") and not line.startswith("//") and '流用台詞' not in line:
                elements1 = line.split('\t')
                if len(elements1) == 2:
                    Voice = elements1[1]
                    if i < len(lines):
                        for j in range(i + 1, len(lines)):
                            next_line = lines[j]
                            print(next_line)
                            if not next_line.startswith("//") and not next_line.startswith("@"):
                                elements2 = next_line.split('␂')[2].split('：')
                                Speaker = elements2[0].replace('【', '').replace('】', '')
                                Text = elements2[1]
                                Text = text_cleaning(Text)
                                result.append((Speaker, Voice, Text))
                                break
            i += 1

    with open(op_json, mode='w', encoding='utf-8') as file:
        json_data = [{'Speaker': Speaker, 'Voice': Voice, 'Text': Text} for Speaker, Voice, Text in result]
        json.dump(json_data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    args = parse_args()
    read_bs5(args.JA, args.op)