import os
import json
import shutil

ba = r'D:\Fuck_galgame\voice'

# 读取 index.json 文件
with open(r'D:\Fuck_galgame\index.json', 'r', encoding='utf-8') as f:
    index_data = json.load(f)

# 缓存音频文件的路径
audio_files = {}
for root, dirs, files in os.walk(ba):
    for file in files:
        if file.endswith('.ogg'):  # 只缓存 .ogg 文件
            audio_files[file.lower()] = os.path.join(root, file)

# 更新的 index 数据
updated_index = []

# 遍历 index.json 中的每个条目
for entry in index_data:
    speaker = entry['Speaker'].lower()  # 获取 Speaker 名称并转换为小写
    voice = entry['Voice'].lower()  # 获取 Voice 名称并转换为小写
    entry['Speaker'] = speaker  # 更新 Speaker 名称
    entry['Voice'] = voice  # 更新 Voice 名称
    # 拼接音频文件名
    audio_file_name = f"{voice}.ogg"

    # 查找音频文件路径
    audio_file_path = audio_files.get(audio_file_name)

    if audio_file_path:
        # 创建以 Speaker 为名称的文件夹（如果不存在）
        speaker_folder = os.path.join(ba.replace('voice', 'f_'), speaker)
        if not os.path.exists(speaker_folder):
            os.makedirs(speaker_folder)
        # 移动音频文件到新的文件夹并转换为小写
        shutil.copy(audio_file_path, os.path.join(speaker_folder, audio_file_name))
        # 添加条目到更新的 index 数据
        updated_index.append(entry)
    else:
        print(f"音频文件 {audio_file_name} 未找到")

# 保存更新后的 index.json
output_index_path = os.path.join(ba.replace('voice', 'f_'), 'index.json')
with open(output_index_path, 'w', encoding='utf-8') as f:
    json.dump(updated_index, f, ensure_ascii=False, indent=4)

print("文件分类整理完成，新的 index.json 已保存")