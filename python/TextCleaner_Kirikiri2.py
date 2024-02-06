import re
import glob
import os

def encoding_dict():
    #return 'Shift_JIS'
    return 'utf-16le'

def voice_dict():
    #return 'voice=[A-Za-z0-9]+'
    return 's=([a-zA-Z]+)_([0-9]+)'

def lab_dict1():
    return '「(.*?)」'

def lab_dict2():
    return '『(.*?)』'

def main(file_path, output_directory_path, debug_mode=False):
    with open(file_path, 'r', encoding=encoding_dict()) as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    voice_lab_mapping = {}

    for i, line in enumerate(lines):
        if line.startswith(';'):
            continue

        match = re.compile(voice_dict()).search(line)
        if match:
            next_line_index = i + 1
            while next_line_index < len(lines) and (lines[next_line_index].startswith('@') or lines[next_line_index].startswith(';')):
                next_line_index += 1

            if '[r]' in lines[next_line_index]:
                lines[next_line_index] = lines[next_line_index].replace('[r]', '').strip() + lines[next_line_index + 1].strip()
            print(line)
            lab_value = re.findall(lab_dict1(), lines[next_line_index])
            if len(lab_value) == 0:
                lab_value = re.findall(lab_dict2(), lines[next_line_index])
            if len(lab_value) == 0:
                continue
            lab_value = lab_value[0]

            voice_value = match[0].replace('s=', '')
            voice_lab_mapping[voice_value] = lab_value

    
    os.makedirs(output_directory_path, exist_ok=True)
    output_file_path = os.path.join(output_directory_path, 'debug.txt')

    if debug_mode:
        with open(output_file_path, 'a', encoding='utf-8') as output_file:
            for voice_value, lab_value in voice_lab_mapping.items():
                output_file.write(voice_value + '|')
                output_file.write(lab_value + '\n')
    else:
        for voice_value, lab_value in voice_lab_mapping.items():
            output_file_path = os.path.join(output_directory_path, f'{voice_value}.txt')
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(lab_value)

if __name__ == '__main__':
    input_directory_path = r"D:\FuckGalGame\Sousaku Kanojo no Ren'ai Koushiki\script"
    output_directory_path = r"D:\FuckGalGame\Sousaku Kanojo no Ren'ai Koushiki\1"
    debug_mode = True
    
    file_paths = glob.glob(os.path.join(input_directory_path, '*.ks'))

    output_file_path = os.path.join(output_directory_path, 'debug.txt')
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    for file_path in file_paths:
        main(file_path, output_directory_path, debug_mode=debug_mode)