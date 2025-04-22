import os
import json
import shutil
from tqdm import tqdm

ba = r'D:\Fuck_galgame\voice'

with open(r'D:\Fuck_galgame\index.json', 'r', encoding='utf-8') as f:
    index_data = json.load(f)

audio_files = {}
for root, dirs, files in os.walk(ba):
    for file in files:
        if file.endswith('.ogg'):
            audio_files[file.lower()] = os.path.join(root, file)

updated_index = []

for entry in tqdm(index_data):
    speaker = entry['Speaker'].lower()
    voice = entry['Voice'].lower()
    entry['Speaker'] = speaker
    entry['Voice'] = voice

    expected_filename = f"{voice}.ogg"

    audio_file_path = audio_files.get(expected_filename)

    if not audio_file_path:
        for key, path in audio_files.items():
            if key.endswith(expected_filename):
                audio_file_path = path
                break

    if audio_file_path:
        speaker_folder = os.path.join(ba.replace('voice', 'f_'), speaker)
        if not os.path.exists(speaker_folder):
            os.makedirs(speaker_folder)
        shutil.copy(audio_file_path, os.path.join(speaker_folder, expected_filename))
        updated_index.append(entry)
    else:
        print(f"音频文件 {expected_filename} 未找到")

output_index_path = os.path.join(ba.replace('voice', 'f_'), 'index.json')
with open(output_index_path, 'w', encoding='utf-8') as f:
    json.dump(updated_index, f, ensure_ascii=False, indent=4)