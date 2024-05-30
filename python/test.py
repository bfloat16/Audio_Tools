import os
import re
import json
import shutil

# 定义源文件夹和目标文件夹路径
source_folder = r"D:\Wuthering Waves Game\Client\Saved\Resources\1.0.0\Resource_zh - 副本"
target_folder = r"C:\Users\bfloat16\Desktop\12121"
json_file_path = r"D:\AI\Audio_Tools\python\WutheringWaves_CHS_index.json"  # 输入JSON文件的路径

os.makedirs(target_folder, exist_ok=True)

# 从JSON文件中读取数据
with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# 初始化一个大 JSON 对象来存储所有文本信息
all_texts = []

# 创建一个映射表，以 TidTalk 为键，以相应的条目为值
data_dict = {str(item["TidTalk"]): item for item in data}

# 判断 TidTalk 是否全是数字
def is_numeric_tid_talk(tid_talk):
    return tid_talk.isdigit()

# 递归查找目标文件夹中的所有音频文件
for root, _, files in os.walk(source_folder):
    for file in files:
        if file.endswith(".wem"):
            file_base_name = os.path.splitext(file)[0]
            
            # 判断文件名结尾是否为_F或_M，并处理 who_id 后缀
            if file_base_name.endswith('_F'):
                gender_suffix = "_女"
                file_base_name = file_base_name[:-2]
            elif file_base_name.endswith('_M'):
                gender_suffix = "_男"
                file_base_name = file_base_name[:-2]
            else:
                gender_suffix = ""
            
            audio = None
            if is_numeric_tid_talk(file_base_name):
                audio = data_dict.get(file_base_name)
            else:
                audio = data_dict.get(file_base_name[6:])
            
            if audio:
                who_id = audio["WhoId"] + gender_suffix
                text = audio["Text"]
                
                # 创建按 who_id 分类的文件夹
                who_folder = os.path.join(target_folder, who_id)
                os.makedirs(who_folder, exist_ok=True)
                
                # 生成目标路径
                target_path = os.path.join(who_folder, file)
                
                # 将文件复制到目标路径
                shutil.copy2(os.path.join(root, file), target_path)
                
                # 将文本信息添加到大 JSON 对象中
                all_texts.append({"path": os.path.relpath(target_path, target_folder), "text": text})

# 将所有文本信息写入一个大的 JSON 文件
with open(os.path.join(target_folder, "all_texts.json"), "w", encoding="utf-8") as json_file:
    json.dump(all_texts, json_file, ensure_ascii=False, indent=4)

print("文件处理完成，文本信息已写入 all_texts.json")