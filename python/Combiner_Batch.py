import os
import glob  
import wave
from pydub import AudioSegment
from tqdm import tqdm

input_dir = r"D:\vcdata\svcdata"
output_dir = r"D:\vcdata\1"

wav_files_list = []


def concatenate_wavs(wav_list, output_path, subdir):
    with wave.open(output_path, 'wb') as output:
        for wav_file in wav_list:
            with wave.open(wav_file, 'rb') as w:
                if not output.getnframes():
                    output.setnchannels(1)  # 设置单声道
                    output.setsampwidth(2)  # 设置采样宽度为16bit
                    output.setframerate(44100)  # 设置采样率为44.1kHz
                output.writeframes(w.readframes(w.getnframes()))

for subdir in tqdm(os.listdir(input_dir), desc=f"Processing"):
    subdir_path = os.path.join(input_dir, subdir)
    if os.path.isdir(subdir_path):
        wav_files = glob.glob(os.path.join(subdir_path, '*.wav'))
        wav_files_list.extend(wav_files)
        wav_files_list = sorted(wav_files_list)

    for i in range(0, len(wav_files_list), 500):
        sub_list = wav_files_list[i:i+500]
        output_wav = os.path.join(output_dir, f'merge_{subdir}_{i//500}.wav')
        concatenate_wavs(sub_list, output_wav, subdir)
        sub_list = []
    wav_files_list = []
