import re
import os
import json
import base64
import msgpack
import hashlib
import argparse
import requests
from dec import decrypt_and_decompress, get_interleaved_split

def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=str, default=r"E:\Game_Dataset\com.aniplex.fategrandorder\RAW")
    parser.add_argument("--action", type=int, default=0)
    return parser.parse_args()

def get_md5_string(input_str):
    m = hashlib.md5()
    m.update((input_str + "pN6ds2Bg").encode('utf-8'))
    return m.hexdigest()

def get_sha_name(name):
    sha1 = hashlib.sha1()
    sha1.update(name.encode('utf-8'))
    hashed = sha1.digest()
    return ''.join(f"{b ^ 0xAA:02x}" for b in hashed) + ".bin"

def fetch_game_data(raw_path):
    url = "https://game.fate-go.jp/gamedata/top"
    resp = requests.get(url, params={"appVer": "0.0"})
    data = resp.json()

    fail = data.get("response", [{}])[0].get("fail")
    if fail:
        action = fail.get("action")
        detail = fail.get("detail", "")
        if action == "app_version_up":
            new_ver = re.search(r"新ver.：(.*?)、", detail).group(1)
            print(f"new version: {new_ver}")
            resp = requests.get(url, params={"appVer": new_ver})
            data = resp.json()
        else:
            raise Exception(detail)

    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def fetch_assetbundle_key(raw_path, output_dir, key):
    with open(raw_path, encoding="utf-8") as f:
        raw = json.load(f)
    success = raw.get("response", [])[0].get("success")

    os.makedirs(output_dir, exist_ok=True)

    for field in ("assetbundle", "assetbundleKey"):
        b64_payload = success[field]

        payload = base64.b64decode(b64_payload)
        iv = payload[:32]
        ciphertext = payload[32:]

        key_bytes = key.encode("utf-8")
        plaintext = decrypt_and_decompress(ciphertext, key_bytes, iv, True)

        data = msgpack.unpackb(plaintext, raw=False)
        out_file_path = os.path.join(output_dir, f"2_{field}.json")
        with open(out_file_path, "w", encoding="utf-8") as out_f:
            json.dump(data, out_f, ensure_ascii=False, indent=2)

def fetch_assetstorages(raw_path, output_dir):
    with open(raw_path, encoding="utf-8") as f:
        raw = json.load(f)
    version = raw["folderName"]
    url = f"https://cdn.data.fate-go.jp/AssetStorages/{version}Android/AssetStorage.txt"
    resp = requests.get(url)
    data = resp.text
    data = base64.b64decode(data)
    base_data, base_top, stage_data, stage_top = get_interleaved_split()
    data = decrypt_and_decompress(data, stage_data, stage_top, True)
    inverted = bytes((~b) & 0xFF for b in data)
    data = inverted.decode('utf-8').rstrip('\x00')
    with open(os.path.join(output_dir, "3_AssetStorage.txt"), "w", encoding="utf-8") as f:
        f.write(data)

def parse_asset_storage(raw_path, output_dir):
    audio_list = []
    asset_list = []
    movie_list = []
    asset_list_with_extra = []

    with open(raw_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    for line in lines[2:]:
        parts = line.split(',')
        try:
            if parts[0] == '1':
                raw_name = parts[4]
                if 'Audio' in raw_name:
                    asset_name = raw_name.replace('/', '@')
                    file_name = get_md5_string(asset_name)
                    audio_list.append({'AssetName': asset_name, 'FileName': file_name})
                elif 'Movie' in raw_name:
                    asset_name = raw_name.replace('/', '@')
                    file_name = get_md5_string(asset_name)
                    movie_list.append({'AssetName': asset_name, 'FileName': file_name})
                else:
                    asset_name = raw_name.replace('/', '@') + '.unity3d'
                    file_name = get_sha_name(asset_name)
                    if len(parts) == 6:
                        key_type = parts[5]
                        asset_list_with_extra.append({'AssetName': key_type, 'FileName': file_name})
                    asset_list.append({'AssetName': asset_name, 'FileName': file_name})

            elif len(parts) == 5:
                raw_name = parts[4]
                asset_name = raw_name.replace('/', '@')
                entry = {'AssetName': asset_name, 'FileName': asset_name}
                if 'Audio' in raw_name:
                    entry['FileName'] = get_md5_string(asset_name)
                    audio_list.append(entry)
                elif 'Movie' in raw_name:
                    entry['FileName'] = get_md5_string(asset_name)
                    movie_list.append(entry)
                else:
                    entry['FileName'] = get_sha_name(asset_name + ' ')
                    asset_list.append(entry)

            elif len(parts) == 7:
                raw_name = parts[4]
                asset_name = raw_name + '.unity3d'
                file_name = parts[0] + '.bin'
                entry = {'AssetName': asset_name, 'FileName': file_name}
                if 'Audio' in raw_name:
                    audio_list.append(entry)
                elif 'Movie' in raw_name:
                    movie_list.append(entry)
                else:
                    asset_list.append(entry)
            else:
                raise ValueError(f"Unsupported format for line: {line}")
        except Exception as e:
            print(f"Error processing line: {line}: {e}")

    # Write JSON outputs
    options = {'indent': 4, 'ensure_ascii': False}
    with open(os.path.join(output_dir, '4_AudioName.json'), 'w', encoding='utf-8') as f:
        json.dump(audio_list, f, **options)
    with open(os.path.join(output_dir, '4_AssetName.json'), 'w', encoding='utf-8') as f:
        json.dump(asset_list, f, **options)
    with open(os.path.join(output_dir, '4_MovieName.json'), 'w', encoding='utf-8') as f:
        json.dump(movie_list, f, **options)
    with open(os.path.join(output_dir, '4_AssetListWithExtraKeyType.json'), 'w', encoding='utf-8') as f:
        json.dump(asset_list_with_extra, f, **options)

if __name__ == "__main__":
    args = args_parser()
    match args.action:
        case 0:
            raw_path = os.path.join(args.root, "1_gamedata.json")
            fetch_game_data(raw_path)

            key = "W0Juh4cFJSYPkebJB9WpswNF51oa6Gm7"
            raw_path = os.path.join(args.root, "1_gamedata.json")
            fetch_assetbundle_key(raw_path, args.root, key)

            raw_path = os.path.join(args.root, "2_assetbundle.json")
            fetch_assetstorages(raw_path, args.root)

            raw_path = os.path.join(args.root, "3_AssetStorage.txt")
            parse_asset_storage(raw_path, args.root)