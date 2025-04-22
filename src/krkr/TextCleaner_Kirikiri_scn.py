import os
import re
import json
import argparse
from tqdm import tqdm

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"D:\Fuck_galgame\script")
    parser.add_argument("-op", type=str, default=r'D:\Fuck_galgame\index.json')
    parser.add_argument("-ft", type=int, default=-1)
    parser.add_argument("-fj", type=str, default='')
    return parser.parse_args(args=args, namespace=namespace)

def read_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def text_cleaning(text):
    text = text.replace('\n', '').replace(r'\n', '')
    text = re.sub(r"%[^;]*;|#[^;]*;|%\d+|\[[^[\\\/]*\]", '', text)
    text = text.replace('\\x', '')
    text = text.replace('\\', '')
    text = text.replace('\n', '')
    text = text.replace('%D$vl1', '')
    text = text.replace('『', '').replace('』', '').replace('「', '').replace('」', '').replace('（', '').replace('）', '').replace('“', '').replace('”', '').replace('≪', '').replace('≫', '')
    text = text.replace(r'　', '').replace('♪', '').replace('♥', '').replace('%r', '').replace('\u3000', '')
    return text

def get_voice_json(voices):
    voice_list = {}
    for voice in voices['list']:
        voice_list[voice['file']] = voice['name']
    return voice_list

def main(JA_dir, op_json, force_type, force_json):
    files_original = []
    for root, dirs, files in os.walk(JA_dir):
        for f in files:
            if f.endswith('.json') and not f.endswith('.resx.json'):
                files_original.append(os.path.join(root, f))

    dialogues = []
    seen_voices = set()

    for filename in tqdm(files_original):
        _0_JA_data = read_json_file(os.path.join(JA_dir, filename))

        if 'scenes' in _0_JA_data:
            for _1_JA_scenes in _0_JA_data['scenes']:
                if 'texts' in _1_JA_scenes:
                    for _2_JA_texts in _1_JA_scenes['texts']:
                        if _2_JA_texts[0] is None or _2_JA_texts[2] is None or _2_JA_texts[3] is None:
                            continue
                        if filename == force_json:
                            Speaker = _2_JA_texts[0]
                            Text = _2_JA_texts[2]
                            Voice = _2_JA_texts[3]
                            dialogues.append((Speaker, Voice, Text))
                        
                        match force_type:
                            case -1:
                                Speaker = _2_JA_texts[3][0]['name']
                                Text = _2_JA_texts[2][0][1]
                                Voice = _2_JA_texts[3][0]['voice']
                                Text = text_cleaning(Text)
                                if Voice in seen_voices:
                                    print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                                else:
                                    seen_voices.add(Voice)
                                    dialogues.append((Speaker, Voice, Text))

                            case 0: # JP
                                Text = _2_JA_texts[1][0][1]
                                Voice = _2_JA_texts[2][0]['voice']
                                for key, value in voice_list.items():
                                    if Voice.startswith(key):
                                        Speaker = key
                                        break
                                Text = text_cleaning(Text)
                                if Voice in seen_voices:
                                    print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                                else:
                                    seen_voices.add(Voice)
                                    dialogues.append((Speaker, Voice, Text))

                            case 1: # JP
                                Speaker = _2_JA_texts[0]
                                Text = _2_JA_texts[2]
                                Voice = _2_JA_texts[3][0]['voice']

                                Speaker = Speaker.replace(' ', '')
                                Text = text_cleaning(Text)
                                if Voice.lower() in seen_voices:
                                    print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                                else:
                                    seen_voices.add(Voice.lower())
                                    dialogues.append((Speaker, Voice, Text))

                            case 2: # JP EN
                                Speaker = _2_JA_texts[0]
                                Text = _2_JA_texts[1][0][1]
                                Voice = _2_JA_texts[2][0]['voice']
                                Text = text_cleaning(Text)
                                if '|' in Voice:
                                    Voice = Voice.split('|')[0]
                                if Voice in seen_voices:
                                    print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                                else:
                                    seen_voices.add(Voice)
                                    dialogues.append((Speaker, Voice, Text))

                            case 3 : # JP EN CHS | JP EN CHS CHT
                                Speaker = _2_JA_texts[2][0]['name']
                                Text = _2_JA_texts[1][0][1]
                                Voice = _2_JA_texts[2][0]['voice']
                                if '|' in Voice:
                                    Voice = Voice.split('|')[0]
                                Text = text_cleaning(Text)
                                if Voice in seen_voices:
                                    print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                                else:
                                    seen_voices.add(Voice)
                                    dialogues.append((Speaker, Voice, Text))
                            
                            case 4:
                                if isinstance(_2_JA_texts[3], list):
                                    for item in _2_JA_texts[3]:
                                        Speaker = item['name']
                                        Text = _2_JA_texts[2]
                                        Voice = item['voice']
                                        Text = text_cleaning(Text)
                                        if Voice in seen_voices:
                                            print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                                        else:
                                            seen_voices.add(Voice)
                                            dialogues.append((Speaker, Voice, Text))
                                else:
                                    Speaker = _2_JA_texts[0]
                                    Text = _2_JA_texts[2]
                                    Voice = _2_JA_texts[3]
                                    Text = text_cleaning(Text)
                                    if Voice in seen_voices:
                                        print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                                    else:
                                        seen_voices.add(Voice)
                                        dialogues.append((Speaker, Voice, Text))
    
    with open(op_json, mode='w', encoding='utf-8') as file:
        json_data = [{'Speaker': Speaker, 'Voice': Voice, 'Text': Text} for Speaker, Voice, Text in dialogues]
        json.dump(json_data, file, ensure_ascii=False, indent=4)

    with open(r"D:\Fuck_galgame\files.txt", mode='w', encoding='utf-16-le') as file:
        for Speaker, Voice, Text in dialogues:
            file.write(f"{Voice}.ogg\n")

if __name__ == '__main__':
    cmd = parse_args()
    main(cmd.JA, cmd.op, cmd.ft, cmd.fj)
    '''
    煞笔PSB SCN文件，瞎套娃搞得乱七八糟的，能不能搞得简洁点，屎山一堆，下面是结构（不一定对，但基本上都是一样的，总有些厂商喜欢乱改）：
    main_json:
        scenes(type=list): # mark_01
            index_0(type=dict):
            index_1(type=dict):
            ......
                texts(type=list): # mark_02
                    index_0(type=list):
                    index_1(type=list):
                    ......
                title(type=list): # 最大是三个，对应日中英三语，可以用len()判断上面的texts(type=list)是哪种格式
                    index_0(type=str)
                    index_1(type=str)
                    index_2(type=str)
    
    if len(title) == 1:
        texts(type=list):
            index_0(type=str) # 真实的角色名（不确定）
            index_1(type=str) # 显示的角色名（刚出场你不知道TA是谁，就会显示？？？）（不确定）
            index_2(type=str) # 对话

    if len(title) == 2:
        texts(type=list):
            index_0(type=list):
                index_0(type=str) # 真实的角色名（角色本来的名字）
                index_1(type=str) # 显示的角色名（刚出场你不知道TA是谁，就会显示？？？）
                index_2(type=list):
                    index_0(type=str): # 中文 或 日文
                        index_0(type=str) # 真实角色名
                        index_1(type=str) # 对话
                    index_1(type=str): # 英文
                        index_0(type=str) # 真实角色名
                        index_1(type=str) # 对话

    if len(title) == 3:
        texts(type=list):
            index_0(type=list):
                index_0(type=str) # 真实的角色名（角色本来的名字）（不确定）
                index_1(type=list):
                    index_0(type=list): # 日文
                        index_0(type=str) # 真实角色名（不确定）
                        index_1(type=str) # 对话
                        index_2(type=int) # 文本长度
                    index_1(type=str): # 英文
                        index_0(type=str) # 真实角色名
                        index_1(type=str) # 对话
                        index_2(type=int) # 文本长度
                    index_2(type=str): # 中文
                        index_0(type=str) # 真实角色名
                        index_1(type=str) # 对话
                        index_2(type=int) # 文本长度
    '''