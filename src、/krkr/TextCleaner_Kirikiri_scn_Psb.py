import os
import subprocess
import threading

print_lock = threading.Lock()

def main(file_path):
    psb_decompile_path = os.path.join(os.path.dirname(__file__), 'TextCleaner_Kirikiri_scn_Psb.exe')
    command = [psb_decompile_path, file_path]
    subprocess.run(command)

def process_files(file_list):
    for file_path in file_list:
        main(file_path)

if __name__ == '__main__':
    input_directory_path = r"C:\Users\bfloat16\Desktop\1\Assets\TextAsset"
    THREAD_NUM = 20

    # 收集所有.scn文件
    scn_files = []
    for root, _, files in os.walk(input_directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            scn_files.append(file_path)

    # 自动调整线程数（不超过文件总数）
    actual_threads = min(THREAD_NUM, len(scn_files))
    
    # 分割文件列表为N个块
    chunks = [scn_files[i::actual_threads] for i in range(actual_threads)]
    chunks = [chunk for chunk in chunks if chunk]  # 过滤空块

    # 创建并启动线程
    threads = []
    for chunk in chunks:
        thread = threading.Thread(target=process_files, args=(chunk,))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    print("All tasks completed.")