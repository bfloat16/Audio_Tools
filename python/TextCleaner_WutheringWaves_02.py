import os
import json
import shutil

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def process_tid_talk(tid_talk):
    if isinstance(tid_talk, int) or tid_talk.isdigit():
        return f"{tid_talk}.wem"
    else:
        return f"en_vo_{tid_talk}"

def copy_files(source_dir, dest_dir, file_mapping):
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.wem'):
                base_name = os.path.basename(file).replace('.wem', '')
                if base_name.isdigit():
                    key = int(base_name)
                else:
                    key = base_name[6:]
                
                if key in file_mapping:
                    who_id, text = file_mapping[key]
                elif not isinstance(key, int):
                    if (key.endswith('_F') or key.endswith('_M')):
                        key = key[:-2]  # 去掉尾巴再查找
                        if key in file_mapping:
                            who_id, text = file_mapping[key]
                        else:
                            print(f"未找到文件 {file} 对应的文本")
                            continue
                    else:
                        print(f"未找到文件 {file} 对应的文本")
                        continue
                else:
                    print(f"未找到文件 {file} 对应的文本")
                    continue
                dest_subdir = os.path.join(dest_dir, who_id.replace('?', '？'))
                os.makedirs(dest_subdir, exist_ok=True)
                dest_path = os.path.join(dest_subdir, file)
                shutil.copyfile(os.path.join(root, file), dest_path)
                result[who_id].append({"text": text, "file_path": os.path.relpath(dest_path, dest_dir)})

def create_file_mapping(data):
    file_mapping = {}
    for entry in data:
        tid_talk = entry['TidTalk']
        file_mapping[tid_talk] = (entry['WhoId'], entry['Text'])
    return file_mapping

# 读取JSON数据
json_data = load_json(r'D:\AI\Audio_Tools\python\WutheringWaves_JA_index.json')

# 创建文件映射
file_mapping = create_file_mapping(json_data)

# 初始化结果字典
result = {entry['WhoId']: [] for entry in json_data}

# 复制文件并生成结果
source_directory = r'D:\Wuthering Waves\Saved\Resources\1.0.0\Resource_ja'
destination_directory = r'C:\Users\bfloat16\Desktop\WutheringWaves_JA'
copy_files(source_directory, destination_directory, file_mapping)

result = {who_id: texts for who_id, texts in result.items() if texts}

# 输出结果为JSON文件
with open(os.path.join(destination_directory,'index.json'), 'w', encoding='utf-8') as outfile:
    json.dump(result, outfile, ensure_ascii=False, indent=4)