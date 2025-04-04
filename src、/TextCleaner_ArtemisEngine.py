import luadata
import re
import json
import argparse
from glob import glob

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"D:\Fuck_galgame\script")
    parser.add_argument("-op", type=str, default=r'D:\Fuck_galgame\index.json')
    parser.add_argument("-fv", type=int, default=1)
    return parser.parse_args(args=args, namespace=namespace)
    
def text_cleaning(text):
    text = text.replace('」', '').replace('「', '').replace('（', '').replace('）', '').replace('『', '').replace('』', '')
    text = text.replace('●', '').replace('　', '')
    return text

def rm_other(text):
    def replacer(match):
        return f"={match.group(1)}"
    
    pattern = re.compile(r'=\s*\[\[(.*?)\]\]', re.MULTILINE)
    new_content = pattern.sub(replacer, text)

    return new_content

def main(JA_dir, op_json, force_version):
    results = []
    seen_voices = set()  # 用于记录已经遇到的 Voice
    filelist = glob(f"{JA_dir}/**/*.ast", recursive=True)

    for filename in filelist:
        match force_version:
            case 0:
                print(f"处理 {filename}")
                with open(filename, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                data = ''.join(lines[0:])
                data = rm_other(data)
                datas = luadata.unserialize(data, encoding="utf-8")
                for block in datas:
                    try:
                        text = datas.get(block, {}).get('text', {})
                        if text.get('vo') and text.get('ja'):
                            Voice = text['vo'][0]['file']
                            Speaker = text['vo'][0]['ch']
                            
                            tmp_result = ''
                            for item in text['ja'][0]:
                                try:
                                    if isinstance(text['ja'][0][item], str):
                                        tmp_result += text['ja'][0][item]
                                except:
                                    if isinstance(item, str):
                                        tmp_result += item
                            
                            Text = text_cleaning(tmp_result)

                            # 检查是否已经遇到过该 Voice
                            if Voice in seen_voices:
                                print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                            else:
                                results.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
                                seen_voices.add(Voice)  # 将 Voice 添加到已处理的集合中

                    except Exception as e:
                        print(f"处理 {block} 时发生错误: {e}")
                        continue
            case 1:
                with open(filename, 'r', encoding='utf-8') as file:
                    data = file.read()
                print(f"处理 {filename}")
                datas = luadata.unserialize(data, encoding="utf-8", multival=False)
                try:
                    texts = datas['text']
                    for text in texts:
                        try:
                            Voice = text['vo'][0]['file']
                            Speaker = text['vo'][0]['ch']
                            tmp_result = ''
                            for item in text['ja'][0]:
                                if isinstance(item, str):
                                    tmp_result += item
                            Text = text_cleaning(tmp_result)
                            if Voice in seen_voices:
                                print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                            else:
                                results.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
                                seen_voices.add(Voice)
                        except:
                            continue
                except:
                    print(f"处理 {filename} 时发生错误")
                    continue

    with open(op_json, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    args = parse_args()
    main(args.JA, args.op, args.fv)