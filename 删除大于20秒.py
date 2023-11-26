import os
import wave
from tqdm import tqdm

def get_wav_duration(wav_file):
    try:
        with wave.open(wav_file, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception as e:
        print(f"Error reading {wav_file}: {e}")
        return None

def delete_short_wav_files(folder_path, tag_duration=20):
    for root, _, files in tqdm(os.walk(folder_path)):
        for file in files:
            if file.endswith('.wav'):
                wav_file = os.path.join(root, file)
                duration = get_wav_duration(wav_file)
                if duration is not None and duration >= tag_duration:
                    print(f"Deleting {wav_file} (Duration: {duration} seconds)")
                    os.remove(wav_file)

if __name__ == "__main__":
    folder_path = r'C:\Users\a1004\Desktop\dataset_re'
    delete_short_wav_files(folder_path)
