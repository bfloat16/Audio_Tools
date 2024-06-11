import re
import json
import struct
import argparse
from tqdm import tqdm
from glob import glob

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"E:\Dataset\FuckGalGame\Lump of Sugar\Animal☆Panic\script")
    parser.add_argument("-op", type=str, default=r'D:\AI\Audio_Tools\python\1.json')
    return parser.parse_args(args=args, namespace=namespace)

def find_subarray(data, sub, start=0, exact=False):
    index = data.find(sub, start)
    if exact and index != -1:
        if data[index:index+len(sub)] != sub:
            return -1
    return index

def slice_bytes(data, start, end=None):
    if end:
        return data[start:end]
    return data[start:]

def BGI(file_path):
    with open(file_path, 'rb') as file:
        script_buffer = file.read()
    header_length = 0
    magic_bytes = bytearray([0x42, 0x75, 0x72, 0x69, 0x6B, 0x6F, 0x43, 0x6F, 0x6D, 0x70, 0x69, 0x6C, 0x65, 0x64,
                             0x53, 0x63, 0x72, 0x69, 0x70, 0x74, 0x56, 0x65, 0x72, 0x31, 0x2E, 0x30, 0x30, 0x00])

    if script_buffer.startswith(magic_bytes):
        header_length = 0x1C + struct.unpack_from("<I", script_buffer, 0x1C)[0]

    script_buffer = slice_bytes(script_buffer, header_length)

    first_text_offset = 0
    offset = find_subarray(script_buffer, b'\x7F\x00\x00\x00', 0)

    if 0 <= offset <= 128:
        first_text_offset = struct.unpack_from("<I", script_buffer, offset + 4)[0]

    int_text_offset_label = find_subarray(script_buffer, b'\x00\x03\x00\x00\x00', 0)

    all_texts = ""
    while int_text_offset_label != -1:
        int_text_offset = struct.unpack_from("<I", script_buffer, int_text_offset_label + 5)[0]
        if first_text_offset < int_text_offset < len(script_buffer):
            end_index = find_subarray(script_buffer, b'\x00', int_text_offset, exact=True)
            bytes_text_block = slice_bytes(script_buffer, int_text_offset, end_index)
            if bytes_text_block:
                str_text = bytes_text_block.decode('shift_jis').replace("\n", r"\n")
                all_texts += str_text + "\n"  # 将文本追加到字符串
        int_text_offset_label = find_subarray(script_buffer, b'\x00\x03\x00\x00\x00', int_text_offset_label + 1)
    return all_texts

def text_cleaning(text):
    text = text.replace('「', '').replace('」', '').replace('（', '').replace('）', '')
    text = re.sub(r"<.*?>", "", text)
    return text

def main(JA_dir, op_json):
    filelist = glob(f"{JA_dir}/**/*", recursive=True)
    results = []

    for filename in tqdm(filelist):
        texts = BGI(filename)
        lines = texts.split('\n')
        first_line = lines[0]
        filtered_lines = [line for line in lines if line != first_line]
        for i, line in enumerate(filtered_lines):
            if line == "_PlayVoice":
                Voice = filtered_lines[i - 1]
                if Voice == "":
                    print(filename, i)
                Speaker = filtered_lines[i + 1]
                Speaker_id = Speaker.split('_')[0]
                Text = filtered_lines[i + 2]
                Text = text_cleaning(Text)
                results.append((Speaker, Speaker_id, Voice, Text))

    replace_dict = {}
    for Speaker, Speaker_id, Voice, Text in tqdm(results):
        if Speaker != '？？？' and Speaker_id not in replace_dict:
            replace_dict[Speaker_id] = Speaker

    fixed_results = []
    for Speaker, Speaker_id, Voice, Text in tqdm(results):
        if Speaker == '？？？' and Speaker_id in replace_dict:
            fixed_results.append((replace_dict[Speaker_id], Speaker_id, Voice, Text))
        else:
            fixed_results.append((Speaker, Speaker_id, Voice, Text))

    with open(op_json, mode='w', encoding='utf-8') as file:
        seen = set()
        json_data = []
        for Speaker, Speaker_id, Voice, Text in fixed_results:
            if (Speaker, Speaker_id, Voice, Text) not in seen:
                seen.add((Speaker, Speaker_id, Voice, Text))
                json_data.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
        json.dump(json_data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    args = parse_args()
    main(args.JA, args.op)