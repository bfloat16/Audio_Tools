import os
import json
import shutil
from tqdm import tqdm

# 读取JSON文件
input_json_filepath = r'D:\AI\Audio_Tools\python\1.json'
source_folder = r"E:\Dataset\FuckGalGame\ASa Project\Koibana Ren'ai - Mini Fandisk - After Festival\voice"
output_folder = r"C:\Users\bfloat16\Desktop\ASa Project_Koibana Ren'ai - Mini Fandisk - After Festival"

# 读取JSON文件数据
with open(input_json_filepath, 'r', encoding='utf-8') as file:
    dialogues = json.load(file)

# 创建文件名到路径的映射，忽略大小写
file_mapping = {}
for root, _, files in os.walk(source_folder):
    for filename in files:
        name, ext = os.path.splitext(filename)
        file_mapping[name.lower()] = os.path.join(root, filename)

# 创建输出文件夹
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 处理对话数据，查找并复制文件
output_data = []
for dialogue in tqdm(dialogues):
    voice = dialogue['Voice']
    name, ext = os.path.splitext(voice)
    name = name.lower()  # 忽略大小写
    if name in file_mapping:
        src_path = file_mapping[name]
        
        # 创建以Speaker命名的子文件夹
        speaker_folder = os.path.join(output_folder, dialogue['Speaker'])
        if not os.path.exists(speaker_folder):
            os.makedirs(speaker_folder)
        
        dest_path = os.path.join(speaker_folder, os.path.basename(src_path))
        shutil.copyfile(src_path, dest_path)
        relative_path = os.path.relpath(dest_path, output_folder)
        
        output_data.append({
            'Speaker': dialogue['Speaker'],
            'Text': dialogue['Text'],
            'FilePath': relative_path
        })

output_json_filepath = os.path.join(output_folder, 'index.json')
with open(output_json_filepath, 'w', encoding='utf-8') as file:
    json.dump(output_data, file, ensure_ascii=False, indent=4)