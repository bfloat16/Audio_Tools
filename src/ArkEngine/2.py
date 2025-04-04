import re
import os
import json

def extract_text_blocks(input_text):
    # 正则表达式匹配所有\text(...)块及其后的内容直到\endtext
    pattern = re.compile(r'\\text\(([^)]*)\)(.*?)\\endtext', re.DOTALL)
    blocks = []
    
    for match in pattern.finditer(input_text):
        params_str = match.group(1).strip()
        content = match.group(2).strip()
        
        # 分割参数并处理
        params = [p.strip().strip('"') for p in params_str.split(',')]
        if params[0] == '？？？':
            speaker = params[1]
        else:
            speaker = params[0]
        
        if speaker == '':
            continue

        if params[-1] != '':
            voice = params[-1]
        else:
            continue
        
        cleaned_content = content.replace('\n', '').replace('\r', '').replace('　', '')
        
        blocks.append({
            'Speaker': speaker,
            'Voice': voice,
            'Text': cleaned_content
        })
    
    return blocks

def process_snr_files(folder_path):
    result = []
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.snr'):
            file_path = os.path.join(folder_path, filename)
            
            try:
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                
                # 提取文本块并添加到结果中
                blocks = extract_text_blocks(content)
                result.extend(blocks)
                
            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")
    
    return result

# 示例使用
if __name__ == '__main__':
    folder_path = r'scripts'
    
    if os.path.isdir(folder_path):
        all_blocks = process_snr_files(folder_path)
        with open('output.json', 'w', encoding='utf-8') as output_file:
            json.dump(all_blocks, output_file, ensure_ascii=False, indent=4)