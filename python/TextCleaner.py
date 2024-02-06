import os
from glob import glob

def process_lab_text(lab_file):
    with open(lab_file, 'r', encoding='utf-8') as lab:
        lab_text = lab.read()
    if '{' in lab_text:
        return ''

def main(input_dir):
    for subdir in os.listdir(input_dir):
        subdir_path = os.path.join(input_dir, subdir)
        lab_files = glob(os.path.join(subdir_path, '*.txt'))
        for lab_file in lab_files:
            wav_file = lab_file.replace('.txt', '.wav')
            if not os.path.exists(wav_file):
                os.remove(lab_file)
                continue
            processed_lab_text = process_lab_text(lab_file)
            if processed_lab_text == '':
                os.remove(lab_file)
                print(f'{lab_file} is removed')
                os.remove(wav_file)
                print(f'{wav_file} is removed')

if __name__ == '__main__':
    main(r'D:\GI_4.3 - 副本')