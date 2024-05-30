import re
import os
import json
import struct
import sqlite3
import argparse
from tqdm import tqdm

def parse_args(args=None, namespace=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-fl", type=str, default=r"D:\Wuthering Waves\Content\Paks\pakchunk10-WindowsNoEditor\Client\Content\Aki\ConfigDB\db_flowState.db")
    parser.add_argument("-la", type=str, default=r"D:\Wuthering Waves\Content\Paks\pakchunk10-WindowsNoEditor\Client\Content\Aki\ConfigDB\zh-Hans\lang_multi_text.db")
    parser.add_argument("-fa", type=str, default=r"D:\Wuthering Waves\Content\Paks\pakchunk10-WindowsNoEditor\Client\Content\Aki\ConfigDB\db_favor.db")

    parser.add_argument("-au", type=str, default=r"D:\Wuthering Waves\Saved\Resources\1.0.0\Resource_zh")
    parser.add_argument("-op", type=str, default=r"D:\AI\Audio_Tools\python\WutheringWaves_CHS_index.json")
    return parser.parse_args(args=args, namespace=namespace)
    
def clean_bin_data(data):
    start_index = data.find(b'[{')
    end_index = data.rfind(b'}]')
    if start_index != -1 and end_index != -1:
        cleaned_data = data[start_index:end_index+2]
        return cleaned_data
    return None

def extract_talk_items(data):
    result = []
    for dictionary_A in data:
        if dictionary_A.get("Name") == "ShowTalk":
            talk_items = dictionary_A.get("Params", {}).get("TalkItems", [])
            for dictionary_B in talk_items:
                if dictionary_B.get("Type") == "Talk" and dictionary_B.get("PlayVoice"):
                    result.append({"TidTalk": dictionary_B.get("TidTalk"), "WhoId": dictionary_B.get("WhoId")})
    return result

def get_speaker(cursor_lang, who_id):
    cursor_lang.execute("SELECT Content FROM MultiText WHERE Id=?", (f"Speaker_{who_id}_Name",))
    result = cursor_lang.fetchone()
    if result:
        return result[0]
    return who_id

def get_text(cursor_lang, tid_talk):
    cursor_lang.execute("SELECT Content FROM MultiText WHERE Id=?", (tid_talk,))
    result = cursor_lang.fetchone()
    if result:
        return result[0]
    return None

def process_flowstate(cursor_flowstate, cursor_lang):
    cursor_flowstate.execute("SELECT binData FROM flowstate")
    bin_datas = cursor_flowstate.fetchall()

    result = []

    for bin_data in tqdm(bin_datas):
        bin_data = bin_data[0]
        cleaned_data = clean_bin_data(bin_data)
        if cleaned_data is None:
            continue
        try:
            cleaned_data_str = cleaned_data.decode('utf-8')
            json_data = json.loads(cleaned_data_str)
            extracted_items = extract_talk_items(json_data)
            for item in extracted_items:
                who_id = item["WhoId"]
                tid_talk = item["TidTalk"]
                speaker_name = get_speaker(cursor_lang, who_id)
                talk_text = get_text(cursor_lang, tid_talk)
                result.append({"WhoId": speaker_name, "Text": talk_text, "TidTalk": tid_talk})
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            continue
    return result

def get_bnk(file_path):
    with open(file_path, 'rb') as file:
        file.seek(56)
        
        num_blocks_bytes = file.read(4)
        num_blocks = struct.unpack('<I', num_blocks_bytes)[0]
        
        blocks = []
        for i in range(num_blocks):
            Chunk_Type = struct.unpack('B', file.read(1))[0]

            Chunk_Size_bytes = file.read(4)
            Chunk_Size = struct.unpack('<I', Chunk_Size_bytes)[0]
            
            block_data = file.read(Chunk_Size)
            
            if Chunk_Type == 0x02:
                if Chunk_Size >= 9:
                    offset = 9
                    Source_ID_bytes = block_data[offset:offset + 4]
                    Source_ID = struct.unpack('<I', Source_ID_bytes)[0]
                blocks.append({'SourceID': Source_ID})
        
        return blocks

def find_file(file_name, start_dir):
    for root, dirs, files in os.walk(start_dir):
        if file_name in files:
            return os.path.join(root, file_name)

def get_favorword(cursor_favorword):
    cursor_favorword.execute("SELECT RoleId, BinData FROM favorword")
    rows = cursor_favorword.fetchall()

    function_name = re.compile(rb'/Game/Aki/WwiseAudio/[\w/]+/[\w\.]+')
    function_favorword = re.compile(rb'FavorWord_\d+_Content')

    result = []
    for row in rows:
        bin_data = row[1]
        match_function_name = function_name.findall(bin_data)[0]
        match_function_favorword = function_favorword.findall(bin_data)[0]

        try:
            decoded_name = match_function_name.decode('utf-8', errors='ignore')
            decoded_name = decoded_name.split(".")[-1]
        except UnicodeDecodeError:
            decoded_name = None
        
        try:
            decoded_favorword = match_function_favorword.decode('utf-8', errors='ignore')
        except UnicodeDecodeError:
            decoded_favorword = None

        result.append({"Role_id": row[0], "function_names": decoded_name, "function_favorwords": decoded_favorword})
    return result

def process_favorword(cursor_favorword, cursor_lang, au):
    results = []

    favorwords = get_favorword(cursor_favorword)
    for favorword in tqdm(favorwords):
        function_name = favorword["function_names"] + ".bnk"
        function_favorword = favorword["function_favorwords"]
        role_id = favorword["Role_id"]
        role_id_sql = f"RoleInfo_{role_id}_Name"
        if role_id_sql == "RoleInfo_1501_Name":
            print(function_favorword)   
            print(function_name)
        if role_id_sql == "RoleInfo_1502_Name":
            print(function_favorword)
            print(function_name)

        wwise_short_name = get_bnk(find_file(function_name, au))
        if len(wwise_short_name) != 1:
            print(f"Error: {function_name}, {wwise_short_name}")
        else:
            wwise_short_name = wwise_short_name[0]["SourceID"]

        cursor_lang.execute("SELECT Content FROM MultiText WHERE Id=?", (function_favorword,))
        text = cursor_lang.fetchone()[0]

        cursor_lang.execute("SELECT Content FROM MultiText WHERE Id=?", (role_id_sql,))
        Whoid = cursor_lang.fetchone()[0]
        results.append({"WhoId": Whoid, "Text": text, "TidTalk": wwise_short_name})

    return results

if __name__ == "__main__":
    args = parse_args()

    conn_flowstate = sqlite3.connect(args.fl)
    cursor_flowstate = conn_flowstate.cursor()

    conn_lang = sqlite3.connect(args.la)
    cursor_lang = conn_lang.cursor()

    conn_favorword = sqlite3.connect(args.fa)
    cursor_favorword = conn_favorword.cursor()

    extracted_flowstate = process_flowstate(cursor_flowstate, cursor_lang)
    extracted_favorword = process_favorword(cursor_favorword, cursor_lang, args.au)

    conn_flowstate.close()
    conn_lang.close()
    conn_favorword.close()

    final_index = extracted_favorword + extracted_flowstate

    with open(args.op, 'w', encoding='utf-8') as f:
        json.dump(final_index, f, ensure_ascii=False, indent=4)