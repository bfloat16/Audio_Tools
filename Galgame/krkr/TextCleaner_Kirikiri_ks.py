import re
import json
import chardet
import argparse
from tqdm import tqdm
from glob import glob

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"D:\Fuck_galgame\script")
    parser.add_argument("-op", type=str, default=r'D:\Fuck_galgame\index.json')
    parser.add_argument("-ft", type=float, default=10)
    return parser.parse_args(args=args, namespace=namespace)

def text_cleaning_01(text):
    text = text.replace('\n', '')
    text = re.sub(r"\[([^\]]+?)'[^]]+\]", r'\1', text)
    text = re.sub(r"\['([^']+?) text=\"[^\"]+?\"\]", r"\1", text)
    text = re.sub(r"＃\([^()]+\) ", "", text)
    text = text.replace('[r]', '').replace('[np]', '')
    text = text.replace('『', '').replace('』', '').replace('「', '').replace('」', '').replace('（', '').replace('）', '')
    text = text.replace('　', '')
    text = re.sub(r"\[[^\]]*\]", '', text)
    text = text.replace('"', '')
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
        
        lines = [line.lstrip() for line in lines if not line.lstrip().startswith(';')]

        for i, line in enumerate(lines):
            match force_type:
                case 0:
                    if 'rt=' in line:
                        match = re.findall(r'@nm\s+t="([^"]*)"\s+rt="([^"]*)"\s+s=(.*)$', line)
                        if match:
                            skip = False
                            match = match[0]
                            Speaker = match[1]
                            Voice = match[2]
                            Voice = Voice.split("/")[-1]
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
                        match = re.findall(r'@nm\s+t="([^"]+)"\s+s=([^\s"]+)', line)
                        if match:
                            skip = False
                            match = match[0]
                            Speaker = match[0]
                            Voice = match[1]
                            Voice = Voice.split("/")[-1]
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

                case 3.5:
                    match = re.findall(r'@(\S+)\s+voice=([^"]+)', line)
                    if match:
                        Speaker, Voice = match[0]
                        Voice = Voice.lower()
                        if '【' in lines[i + 1] and '】' in lines[i + 1]:
                            Text = lines[i + 2]
                            Text = text_cleaning_02(Text)
                            if '【ゆり】' in Text:
                                pass
                            results.append((Speaker, Voice, Text))
                            

                case 4:
                    match = re.findall(r'\[(.*?)\s+voice="(.*?)"\]', line)
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
                                        Text = text_cleaning_01(Text)
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
                                        Text = text_cleaning_01(Text)
                                        results.append((Speaker, Voice, Text))
                                        break
                                    else:
                                        tmp_result.append(lines[n])
                                break

                case 6:
                    match1 = re.search(r'\[Voice\s+file=([^\]]+)\]', line)
                    if match1:
                        Voice = match1.group(1)
                        for j in range(i + 1, len(lines)):
                            match2 = re.search(r'\[Talk\s+name=([^\]]+)\]', lines[j])
                            if match2:
                                Speaker = match2.group(1)
                                tmp_result = []
                                for j in range(i + 2, len(lines)):
                                    if "[r]" in lines[j]:
                                        tmp_result.append(lines[j])
                                    else:
                                        tmp_result.append(lines[j])
                                        Text = ''.join(tmp_result)
                                        Text = text_cleaning_01(Text)
                                        results.append((Speaker, Voice, Text))
                                        break
                case 7:
                    match = re.findall(r"@hbutton.*?\['storage'\s*=>\s*'([^']+)']", line)
                    if match:
                        Speaker = match[0].split('/')[2]
                        Voice = match[0].split('/')[3]
                        tmp_result = []
                        for j in range(i + 1, len(lines)):
                            if '[endvoice]' in lines[j] or (lines[j].startswith("@") and len(tmp_result) != 0):
                                Text = ''.join(tmp_result)
                                Text = text_cleaning_01(Text)
                                results.append((Speaker, Voice, Text))
                                break
                            elif "@" in lines[j]:
                                continue
                            else:
                                tmp_result.append(lines[j])
                case 7.5:
                    match = re.findall(r'\[voice_([^\s\]]+)\s+storage="([^"]+)"\]', line)
                    if match:
                        Speaker, Voice = match[0]
                        Voice = Voice.split('.')[0]

                        for j in range(i + 1, len(lines)):
                            if '[opacity_indent]' in lines[j] and '[endindent]' in lines[j]:
                                Text = text_cleaning_01(lines[j])
                                results.append((Speaker, Voice, Text))
                                break
                
                case 8:
                    match1 = re.findall(r'\[ps\s+n=([^\s]+)\s+v="([^"]+)"\]', line)
                    if match1:
                        Speaker = match1[0][0].split('/')[0]
                        Voice = match1[0][1]
                        tmp_result = []
                        is_text = False
                        for j in range(i + 1, len(lines)):
                            if "[else]" in lines[j]:
                                is_text = True
                            elif "[endif]"in lines[j]:
                                Text = ''.join(tmp_result)
                                Text = text_cleaning_01(Text)
                                results.append((Speaker, Voice, Text))
                                break
                            elif is_text:
                                tmp_result.append(lines[j])
                case 8.5:
                    match1 = re.findall(r'\[pv\s+char="([^"]+)"\s+voice=([^\s\]]+)', line)
                    if match1:
                        Speaker = match1[0][0].split('/')[0]
                        Voice = match1[0][1].replace('.ogg', '')

                        # 收集从当前行开始往下直到遇到 [ps] 的所有文本
                        dialogue_lines = []
                        j = i + 1
                        while j < len(lines) and '[ps]' not in lines[j]:
                            dialogue_lines.append(lines[j])
                            j += 1

                        # 如果 [ps] 在同一行
                        if j < len(lines):
                            if '[ps]' in lines[j]:
                                dialogue_lines.append(lines[j])

                        # 提取对话内容
                        full_text = ''.join(dialogue_lines)
                        match = re.search(r'「(.*?)」', full_text, re.DOTALL)
                        if match:
                            Text = match.group(1)
                            Text = text_cleaning_01(Text)
                            if Text != '':
                                results.append((Speaker, Voice, Text))
                case 9:
                    match = re.findall(r'\[mess[^\]]*?name=([^\s\]]+)[^\]]*?voice="([^"]+)"', line)
                    if match:
                        match = match[0]
                        Speaker = match[0]
                        Speaker = Speaker.split("／")[0]
                        Voice = match[1]
                        tmp_result = []
                        for j in range(i + 1, len(lines)):
                            if "[p2]" in lines[j]:
                                break
                            line_content = lines[j].replace("[r]", "")
                            tmp_result.append(line_content)
                        Text = ''.join(tmp_result)
                        Text = text_cleaning_01(Text)
                        results.append((Speaker, Voice, Text))

                case 10:
                    match = re.search(r'\[([^ \]]+).*?\bvo=([^\s\]]+)', line)
                    if match:
                        Speaker = match.group(1)
                        Speaker = Speaker.split("／")[0]
                        Voice = match.group(2)
                        if i + 1 < len(lines):
                            text_line = lines[i+1]
                            text_match = re.search(r'\[>>\](.*?)\[<<\]\[c\]', text_line)
                            if text_match:
                                Text = text_match.group(1)
                                Text = text_cleaning_01(Text)
                                results.append((Speaker, Voice, Text))

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