import re
import json
import argparse
from glob import glob
from lupa import lua_type
from lupa.lua54 import LuaRuntime

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"D:\Fuck_galgame\script")
    parser.add_argument("-op", type=str, default=r'D:\Fuck_galgame\index.json')
    parser.add_argument("-fv", type=int, default=2)
    return parser.parse_args(args=args, namespace=namespace)
    
def text_cleaning(text):
    text = re.sub(r'\[ruby text="[^"]*"\](.*?)\[/ruby\]', r'\1', text)
    text = text.replace('\n', '').replace('\\n', '')
    text = text.replace('」', '').replace('「', '').replace('（', '').replace('）', '').replace('『', '').replace('』', '')
    text = text.replace('●', '').replace('　', '')
    return text

def lua_2_python(obj):
    if lua_type(obj) != 'table':
        return obj
    
    keys = list(obj.keys())
    if all(isinstance(k, int) for k in keys):
        expected_keys = list(range(1, len(keys) + 1))
        if sorted(keys) == expected_keys:
            return [lua_2_python(obj[i]) for i in expected_keys]

    result = {}
    for k, v in obj.items():
        result[k] = lua_2_python(v)
    return result

def main(JA_dir, op_json, force_version):
    results = []
    seen_voices = set()
    filelist = glob(f"{JA_dir}/**/*.ast", recursive=True)
    filelist += glob(f"{JA_dir}/**/*.lua", recursive=True)
    lua = LuaRuntime(unpack_returned_tuples=True)

    for filename in filelist:
        match force_version:
            case 0:
                print(f"{filename}")
                with open(filename, 'r', encoding='utf-8') as f:
                    Text = Voice = Speaker = None
                    data = f.read()
                    data = 'scenario = {}\n' + data
                    try:
                        lua.execute(data)
                        lua_table = lua.globals().scenario
                        python_dict = lua_2_python(lua_table)
                    except:
                        print(f"Error parsing {filename}")
                        continue
                    if python_dict:
                        for value in python_dict.values():
                            for block in value:
                                if isinstance(block, dict):
                                    Text = block.get("text", [])[0] if block.get("text") else None
                                    Text = text_cleaning(Text) if Text else None
                                    for tag in block.get("tag", []):
                                        if len(tag) == 3 and tag.get(1) == "name":
                                            tmp_speaker = re.findall(r"[A-Za-z]+_[A-Za-z]+_\d+", tag["1"])
                                            speakers = []
                                            for tmp in tmp_speaker:
                                                if '_' in tmp:
                                                    parts = tmp.rsplit('_', 1)
                                                    speakers.append(parts[0])
                                                else:
                                                    speakers.append(tmp)

                                            Speaker = '&'.join(speakers)
                                            Voice = tag["1"]
                                            break
                                    if Text and Voice and Speaker:
                                        if Voice in seen_voices:
                                            print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                                        else:
                                            results.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
                                            seen_voices.add(Voice)
                                        Text = Voice = Speaker = None
                                        pass
            case 1:
                print(f"{filename}")
                with open(filename, 'r', encoding='utf-8') as f:
                    Text = Voice = Speaker = None
                    data = f.read()
                    try:
                        lua.execute(data)
                        lua_table = lua.globals().ast
                        python_dict = lua_2_python(lua_table)
                    except:
                        print(f"Error parsing {filename}")
                        continue
                    if python_dict:
                        for value in python_dict.values():
                            for block in value.values():
                                if isinstance(block, dict):
                                    vo = block.get("vo", [])[0] if block.get("vo") else None
                                    if vo:
                                        Speaker = vo['ch']
                                        Voice = vo['file']
                                    else:
                                        continue
                                    
                                    text_block = block.get("ja", [])[0] if block.get("ja") else None
                                    if text_block:
                                        filtered = {k: v for k, v in text_block.items() if isinstance(k, int)}
                                        Text = ''.join(v for k, v in sorted(filtered.items()) if isinstance(v, str))
                                        Text = text_cleaning(Text)
                                    else:
                                        continue

                                    if Voice in seen_voices:
                                        print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                                    else:
                                        results.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
                                        seen_voices.add(Voice)

            case 2:
                print(f"{filename}")
                with open(filename, 'r', encoding='utf-8') as f:
                    Text = Voice = Speaker = None
                    data = f.read()
                    try:
                        lua.execute(data)
                        lua_table = lua.globals().ast
                        python_dict = lua_2_python(lua_table)
                    except:
                        print(f"Error parsing {filename}")
                        continue
                    if python_dict:
                        for value in python_dict.values():
                            if isinstance(value, dict):
                                for block in value.values():
                                    if isinstance(block, dict):
                                        vo = block.get("vo", [])[0] if block.get("vo") else None
                                        if vo:
                                            Speaker = vo['ch']
                                            Voice = vo['file']
                                        else:
                                            continue

                                        text_ja = block.get("ja")[0]
                                        if not text_ja:
                                            continue

                                        Text = ""
                                        if isinstance(text_ja, list):
                                            parts = []
                                            for item in text_ja:
                                                if isinstance(item, str):
                                                    parts.append(item)
                                            Text = ''.join(parts)
                                            Text = text_cleaning(Text)

                                        elif isinstance(text_ja, dict):
                                            filtered = {k: v for k, v in text_ja.items() if isinstance(k, int)}
                                            Text = ''.join(v for k, v in sorted(filtered.items()) if isinstance(v, str))
                                            Text = text_cleaning(Text)

                                        if Voice in seen_voices:
                                            print(f"重复的 Voice: {Voice}, Speaker: {Speaker}, Text: {Text}")
                                        else:
                                            results.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
                                            seen_voices.add(Voice)

    with open(op_json, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    args = parse_args()
    main(args.JA, args.op, args.fv)