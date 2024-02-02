import os
import glob  
import wave
import shutil
from tqdm import tqdm

input_dir = r"/home/ooppeenn/Desktop/2"
output_dir = r"/home/ooppeenn/Desktop/3"

unclassified_wav_list = []
short_wav_list = []
total_duration = 0
start_index, end_index = 0, 0

def concatenate_wavs(wav_list, output_path):
    first_wav = wave.open(wav_list[0], 'rb')
    output_wav = wave.open(output_path, 'wb')
    output_wav.setnchannels(first_wav.getnchannels())
    output_wav.setsampwidth(first_wav.getsampwidth())
    output_wav.setframerate(first_wav.getframerate())
    output_wav.setnframes(0)
    for wav_file in wav_list:
        input_wav = wave.open(wav_file, 'rb')
        output_wav.writeframes(input_wav.readframes(input_wav.getnframes()))
        input_wav.close()
    output_wav.close()
    first_wav.close()

def get_audio_duration(file_path):
    with wave.open(file_path, 'r') as audio_file:
        frames = audio_file.getnframes()
        rate = audio_file.getframerate()
        duration = frames / float(rate)
        return duration

for subdir in tqdm(os.listdir(input_dir)):
    subdir_path = os.path.join(input_dir, subdir)
    if os.path.isdir(subdir_path):
        wav_files = glob.glob(os.path.join(subdir_path, '*.wav'))
        unclassified_wav_list.extend(wav_files)
        unclassified_wav_list = sorted(unclassified_wav_list)

    for unclassified_wav in unclassified_wav_list:
        if get_audio_duration(unclassified_wav) >= 6:
            output_subdir = os.path.join(output_dir, subdir)
            os.makedirs(output_subdir, exist_ok=True)
            shutil.copy(unclassified_wav, output_subdir)
        else:
            short_wav_list.append(unclassified_wav)

    short_wav_list = sorted(short_wav_list)

    for short_wav_file in short_wav_list:
        single_duration = get_audio_duration(short_wav_file)
        total_duration += single_duration
        if total_duration < 6:
            end_index += 1
        else:
            output_subdir = os.path.join(output_dir, subdir)
            os.makedirs(output_subdir, exist_ok=True)
            output_wav = os.path.join(output_subdir, f'merge_{subdir}_{start_index}_{end_index}.wav')
            concatenate_wavs(short_wav_list[start_index:end_index + 1], output_wav)
            start_index = end_index + 1
            end_index = start_index
            total_duration = 0
    total_duration = 0
    start_index, end_index = 0, 0
    short_wav_list = []
    unclassified_wav_list = []