import re
import os
import json

def text_cleaning(text):
    text = text.replace('『', '').replace('』', '').replace('「', '').replace('」', '').replace('（', '').replace('）', '')
    text = text.replace('　', '').replace('\n', '')
    return text

def extract_text_blocks(input_text):
    pattern = re.compile(r'\\text\(([^)]*)\)(.*?)\\endtext', re.DOTALL)
    blocks = []
    
    for match in pattern.finditer(input_text):
        params_str = match.group(1).strip()
        content = match.group(2).strip()
        
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
        
        cleaned_content = text_cleaning(content)
        
        blocks.append({'Speaker': speaker, 'Voice': voice, 'Text': cleaned_content})
    
    return blocks

def process_snr_files(folder_path):
    result = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.snr'):
            file_path = os.path.join(folder_path, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                
                blocks = extract_text_blocks(content)
                result.extend(blocks)
                
            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")
    
    return result

if __name__ == '__main__':
    folder_path = r'D:\Fuck_galgame\scripts'
    
    if os.path.isdir(folder_path):
        all_blocks = process_snr_files(folder_path)
        with open(r'D:\Fuck_galgame\index.json', 'w', encoding='utf-8') as output_file:
            json.dump(all_blocks, output_file, ensure_ascii=False, indent=4)