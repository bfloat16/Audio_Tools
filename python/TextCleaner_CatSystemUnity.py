import os
import re
import zlib
import struct
from glob import glob

global pos
pos = 0

def uncompress_cstx(filename):
    CSTXSig = b'CSTX'
    with open(filename, 'rb') as f:
        data = f.read()
    if not data.startswith(CSTXSig):
        raise ValueError("Invalid file signature")
    
    header_format = '<Iiii'  #uint32, int32, int32, int32
    header_size = struct.calcsize(header_format)
    sig, orig_len, compress_len, mode = struct.unpack_from(header_format, data, 0)
    pos = header_size
    left_len = len(data) - pos - compress_len
    
    if mode == 1:
        uncompressed_data = zlib.decompressobj(-zlib.MAX_WBITS).decompress(data[pos:pos + compress_len])
        data = uncompressed_data + data[pos + compress_len:]
    else:
        data = data[pos:pos + orig_len + left_len]
    return data

def read_chunk_num(data):
    global pos
    if len(data) < pos + 4:
        return 0
    else:
        num = data[pos]
        num |= data[pos + 1] << 8
        num |= data[pos + 2] << 16
        num |= data[pos + 3] << 24
        pos += 4
        return num
    
def read_string_num(data):
    global pos
    num = 0
    shift = 0
    while True:
        if shift >= 32:
            raise ValueError("Invalid length")
        byte = data[pos]
        pos += 1
        num |= (byte & 0x7F) << shift
        shift += 7
        if byte < 128:
            return num
        
def read_string(data):
    global pos
    length = read_string_num(data)
    if length == 0:
        return ""
    elif length < 0 or length > len(data[pos:]):
        raise Exception("Read String Error!")
    str = data[pos:pos + length].decode('utf-8')
    pos += length
    return str

def main(file_path, output_dir=None, debug_mode=False):
    global pos
    pos = 0
    tmp_results = []
    data = uncompress_cstx(file_path)
    chunk_num = read_chunk_num(data)
    if chunk_num > 0:
        for i in range(chunk_num):
            string_num = read_string_num(data)
            for j in range(string_num):
                string = read_string(data)
                if not string.startswith("//"):
                    tmp_results.append(string)

        with open("tmp.txt", "a", encoding="utf-8") as f:
            f.write(f"{file_path}\n")
            for item in tmp_results:
                f.write(f"{item}\n")
        a = 0
        b = 0
        is_header = False
        results = []
        while a < len(tmp_results):
            if tmp_results[a].startswith("\tpcm") and "end" not in tmp_results[a] and "rdraw" not in tmp_results[a]:
                tmp_audio = []
                tmp_speaker = []
                for b in range(a, len(tmp_results)):
                    if tmp_results[b].startswith("\tpcm"):
                        tmp_audio.append(tmp_results[b])

                    elif not tmp_results[b].startswith("\t") and tmp_results[b] != "":
                        tmp_speaker = re.split('[＆＠]', tmp_results[b])[:b - a]

                    elif tmp_results[b].startswith("\t"):
                        text = ""
                        while tmp_results[b].startswith("\t"):
                            text += tmp_results[b]
                            if '\\@' in tmp_results[b]:
                                b += 1
                                break
                            b += 1
                        break

                for tmp_audio, tmp_speaker in zip(tmp_audio, tmp_speaker):
                    tmp_audio = tmp_audio.replace("\tpcm ", "")
                    text = text.replace("\t", "").replace("\\@", "").replace("　", "").replace("「", "").replace("」", "").replace("『", "").replace("』", "")
                    results.append({"audio": tmp_audio, "speaker": tmp_speaker, "text": text})
                a = b
            a += 1

        is_header = False

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

if __name__ == "__main__":
    input_dir = r"E:\sdsdsds"
    output_dir = r"E:"
    debug_mode = True
    
    file_paths = glob(f"{input_dir}/**/*.cstx", recursive=True)

    for file_path in file_paths:
        main(file_path, output_dir, debug_mode=debug_mode)