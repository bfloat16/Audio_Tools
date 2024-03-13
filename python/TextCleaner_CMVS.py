import os
import struct
from glob import glob

def lzss(CompressData, CompressSize):
    curbyte = 0
    flag = 0
    cur_winpos = 0x7df
    window = [0]*2048
    DeCompressData = []
    while True:
        flag >>= 1
        if not (flag & 0x0100):
            if curbyte >= CompressSize:
                break
            flag = CompressData[curbyte] | 0xff00
            curbyte += 1
        if (flag & 1):
            if curbyte >= CompressSize:
                break
            data = CompressData[curbyte]
            window[cur_winpos] = data
            DeCompressData.append(data)
            curbyte += 1
            cur_winpos = (cur_winpos + 1) & 0x7ff
        else:
            if curbyte >= CompressSize:
                break
            offset = CompressData[curbyte]
            curbyte += 1
            if curbyte >= CompressSize:
                break
            count = CompressData[curbyte]
            curbyte += 1
            offset |= (count & 0xe0) << 3
            count = (count & 0x1f) + 2
            for i in range(count):
                data = window[(offset + i) & 0x7ff]
                DeCompressData.append(data)
                window[cur_winpos] = data
                cur_winpos = (cur_winpos + 1) & 0x7ff
    return DeCompressData

# 0 PS2A 4 HeadSize 8 Unknown 12 SeedKey 16 LabelCount 20 CodeSegSize 24 Unknown 28 TextSegSize 32 BegPC 36 CompressSize 40 DeCompressSize 44 Unknown 48 CompressData......
def main(file_path, output_dir, debug_mode=False):
    with open(file_path, 'rb') as f:
        header = f.read(4).decode()
        if header != 'PS2A':
            raise ValueError('Invalid file header')
        HeadSize, Unknown0, SeedKey, LabelCount, CodeSegSize, UnknownSegSize, TextSegSize, BegPC, CompressSize, DeCompressSize, Unknown2 = struct.unpack('<11I', f.read(44))
        CompressData = bytearray(f.read(CompressSize))

        print(f'File:{os.path.basename(file_path):<15}|HeadSize: {HeadSize:<3}|Unknown0: {Unknown0:<9}|SeedKey: {SeedKey:<11}|LabelCount: {LabelCount:<4}|CodeSegSize: {CodeSegSize:<8}|UnknownSegSize: {UnknownSegSize:<4}|TextSegSize: {TextSegSize:<6}|BegPC: {BegPC:<7}|CompressSize: {CompressSize:<7}|DeCompressSize: {DeCompressSize:<7}|Unknown2: {Unknown2:<2}')
                
        xor = ((SeedKey >> 24) + (SeedKey >> 3)) & 0xFF
        shifts = ((SeedKey >> 20) % 5) + 1

        for i in range(CompressSize):
            tmp = ((CompressData[i] - 0x7c) & 0xFF) ^ xor
            CompressData[i] = ((tmp >> shifts) | (tmp << (8 - shifts))) & 0xFF
        lzss_data = bytearray(lzss(CompressData, CompressSize))

        label_table_offset = 0
        code_seg_offset = LabelCount * 4
        unkonw_offset = code_seg_offset + CodeSegSize
        text_seg_offset = unkonw_offset + UnknownSegSize
        
        results = []
        tmp_result = []
        is_speaker = False
        for i in range(len(lzss_data)):
            command_bytes = lzss_data[i:i+4]
            if command_bytes == b'\x01\x02\x20\x01':
                if i + 8 < len(lzss_data):
                    offset_bytes = lzss_data[i+4:i+8]
                    check_bytes = lzss_data[i+8:i+12]
                    if check_bytes == b'\x0f\x02\x30\x04':
                        offset = struct.unpack('<I', offset_bytes)[0]
                        text_ptr = text_seg_offset + offset
                        text = []
                        while lzss_data[text_ptr] != 0x00:
                            text.append(lzss_data[text_ptr])
                            text_ptr += 1
                        tmp_result.append(bytes(text).decode('cp932'))
                        if is_speaker:
                            try:
                                speaker = tmp_result[-1]
                                audio = tmp_result[-2]
                                text = tmp_result[-3]
                                substrings = ['.ogg', '.wav', '.mv2', '.pb3', '.pb2', '.ps3', '.ps2', '.cur', '.cmv', '.mgv']
                                if all(sub not in speaker for sub in substrings) and all(sub not in text for sub in substrings) and ".ogg" in audio:
                                    results.append({'speaker': speaker, 'audio': audio, 'text': text})
                                    print(f"Speaker: {speaker:<15}, Audio: {audio:<17}, Text: {text}")
                                    tmp_result = []
                                    is_speaker = False
                            except:
                                tmp_result = []
                                is_speaker = False

                        if tmp_result is not None and len(tmp_result) > 0:
                            if ".ogg" in tmp_result[-1]:
                                is_speaker = True
                    else:
                        continue
            else:
                continue

        subdir_path = file_path.split('\\')[-2]

        for item in results:
            if debug_mode:
                debug_text = os.path.join(output_dir, f"{subdir_path}_debug.txt")
                with open(debug_text, 'a', encoding='utf-8') as f:
                    f.write(f"{item['audio']}|{item['speaker']}|{item['text']}\n")
            else:
                text_dir = os.path.join(output_dir, subdir_path, item['speaker'])
                text_path = os.path.join(output_dir, subdir_path, item['speaker'], f"{item['audio'].replace('.ogg', '.txt')}")
                os.makedirs(text_dir, exist_ok=True)
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(item['text'])

if __name__ == '__main__':
    input_dir = r"E:\Dataset\FuckGalGame\Purple software"
    output_dir = r"C:\Users\bfloat16\Desktop\CMVS"
    debug_mode = True
    
    file_paths = glob(f"{input_dir}/**/*.ps3", recursive=True)

    for file_path in file_paths:
        main(file_path, output_dir, debug_mode=debug_mode)