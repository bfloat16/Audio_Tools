import re
import zlib
import json
import struct
import argparse
from glob import glob
from tqdm import tqdm

global pos
pos = 0

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-JA", type=str, default=r"E:\Dataset\FuckGalGame\Archive\Unravel trigger\script")
    parser.add_argument("-op", type=str, default=r'D:\AI\Audio_Tools\python\1.json')
    return parser.parse_args(args=args, namespace=namespace)

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

def main(JA_dir, op_json):
    filelist = glob(f"{JA_dir}/**/*.cstx", recursive=True)
    results = []

    for filename in tqdm(filelist):
        global pos
        pos = 0
        tmp_results = []
        data = uncompress_cstx(filename)
        chunk_num = read_chunk_num(data)
        if chunk_num > 0:
            for i in range(chunk_num):
                string_num = read_string_num(data)
                for j in range(string_num):
                    string = read_string(data)
                    if not string.startswith("//"):
                        tmp_results.append(string)
            a = 0
            b = 0
            is_header = False
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
                            Text = ""
                            while tmp_results[b].startswith("\t") and not re.match(r'(?<!\\)＠', tmp_results[b]):
                                Text += tmp_results[b]
                                if '\\@' in tmp_results[b]:
                                    b += 1
                                    break
                                b += 1
                            break

                    for tmp_audio, tmp_speaker in zip(tmp_audio, tmp_speaker):
                        tmp_audio = tmp_audio.replace("\tpcm ", "")
                        Text = Text.replace("\t", "").replace("\\@", "").replace("　", "").replace("「", "").replace("」", "").replace("『", "").replace("』", "")
                        if tmp_audio == 'SOP_5_13_01_007':
                            pass
                        results.append((tmp_audio, tmp_speaker, Text))
                    a = b
                a += 1

            is_header = False

    with open(op_json, mode='w', encoding='utf-8') as file:
        seen = set()
        json_data = []
        for Speaker, Voice, Text in results:
            record = (Speaker, Voice, Text)
            if record not in seen:
                seen.add(record)
                json_data.append({'Speaker': Speaker, 'Voice': Voice, 'Text': Text})
        json.dump(json_data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    args = parse_args()
    main(args.JA, args.op)