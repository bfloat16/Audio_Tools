import os
import sys
import json
import time
import requests
import argparse
from Crypto.Cipher import AES
from concurrent import futures
from tools import application_info_pb2
from datetime import datetime, timezone
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn

from pythonnet import load
load("coreclr")
import clr
script_dir = os.path.dirname(os.path.realpath(__file__))
tools_dir = os.path.join(script_dir, "tools")
sys.path.append(tools_dir)

dll_path = os.path.join(tools_dir, "BanG_Dream_protobufnet.dll")
clr.AddReference(dll_path)
from BanG_Dream_protobufnet import ManifestLoader #别删，这玩意是从BanG_Dream_protobufnet.dll里导入的

def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", default=r"E:\Game_Dataset\jp.co.craftegg.band\RAW")
    parser.add_argument("--threads", default=32)
    return parser.parse_args()

BASE_URL = "https://api.garupa.jp/api/application"
APP_HASH = "e15bca7f8e1c11ad1284a3ac1f9863b3a513c921c6f8a57a8fbd153c7539055c"
ASSET_URL = "https://content.garupa.jp/Release"

PROXIES= {
    "http": "http://127.0.0.1:7897",
    "https": "http://127.0.0.1:7897",
}

USER_AGENT = "UnityPlayer/2021.3.39f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"

columns = (SpinnerColumn(), TextColumn("[bold blue]{task.description}"), BarColumn(bar_width=100), "[progress.percentage]{task.percentage:>6.2f}%", TextColumn("{task.completed}/{task.total}"), TimeElapsedColumn(), "•", TimeRemainingColumn())

def get_asset_url_dec(data):
    key = b"mikumikulukaluka"
    iv = b"lukalukamikumiku" 
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = cipher.decrypt(data)
    pad_len = padded[-1]
    return padded[:-pad_len]

def get_asset_url():
    headers1 = {
        "Host":             "api.garupa.jp",
        "User-Agent":       USER_AGENT,
        "Accept-Encoding":  "deflate, gzip",
        "Content-Type":     "application/octet-stream",
        "Accept":           "application/octet-stream",
        "X-ClientVersion":  "9.1.0",
        "X-Signature":      "3cde36c1-b431-4458-90cf-469cb0096e0a",
        "X-ClientPlatform": "Android",
    }

    headers2 = {
        "Host":             "content.garupa.jp",
        "User-Agent":       USER_AGENT,
        "Accept-Encoding":  "deflate, gzip",
        "X-ClientPlatform": "Android",
        "X-Unity-Version":  "2021.3.39f1",
    }
    resp = requests.get(BASE_URL, headers=headers1, proxies=PROXIES)
    resp.raise_for_status()
    app_info = application_info_pb2.AppGetResponse()
    resp = get_asset_url_dec(resp.content)
    app_info.ParseFromString(resp)
    app_version = app_info.dataVersion

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    url = f"{ASSET_URL}/{app_version}_{APP_HASH}/Android/AssetBundleInfo?t={timestamp}"
    url_ab = f"{ASSET_URL}/{app_version}_{APP_HASH}/Android"
    resp = requests.get(url, headers=headers2, proxies=PROXIES)
    resp.raise_for_status()

    info = ManifestLoader.LoadBytesAndSerialize(resp.content)
    info = json.loads(info)
    return info, url_ab

def bytes_to_gib(n_bytes):
    return n_bytes / (1024 ** 3)

def calc_total_size(bundles):
    return sum(int(b.get("fileSize", 0)) for b in bundles.values())

def download_once(session, url, dest_path):
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    with open(dest_path, 'wb') as f:
        f.write(resp.content)

def worker(bundle_name, base_url, out_root):
    dest_path = os.path.join(out_root, f"{bundle_name}.unity3d")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    session = requests.Session()
    session.proxies.update(PROXIES)
    session.headers.update({"User-Agent": USER_AGENT})

    while True:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        url = f"{base_url}/{bundle_name}?t={timestamp}"
        try:
            download_once(session, url, dest_path)
            return
        except Exception as exc:
            print(f"[W] Download failed for {bundle_name}: {exc}")
            time.sleep(1)

if __name__ == "__main__":
    args = args_parser()
    meta, url = get_asset_url()

    bundles = meta["bundles"]

    total_bytes = calc_total_size(bundles)
    print(f"Total payload: {bytes_to_gib(total_bytes):.2f} GiB ({total_bytes:,} bytes)")

    out_root = args.output_dir
    os.makedirs(out_root, exist_ok=True)

    bundle_names = list(bundles.keys())
    num_bundles = len(bundle_names)

    with Progress(*columns) as progress:
        task_id = progress.add_task("Downloading", total=num_bundles)

        def wrapped_worker(name):
            worker(name, url, out_root)
            progress.update(task_id, advance=1)

        with futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            executor.map(wrapped_worker, bundle_names)