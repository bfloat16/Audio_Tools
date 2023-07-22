import os
import json
import ffmpeg
from concurrent.futures import ThreadPoolExecutor

# Specify the full paths to the FFmpeg and ffprobe executables
ffmpeg_path = r"D:\Tools\ffmpeg\ffmpeg.exe"
ffprobe_path = r"D:\Tools\ffmpeg\ffprobe.exe"

def concat_audio_in_folders(input_folders, output_folder):
    for folder in input_folders:
        folder_name = os.path.basename(folder)
        input_files = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith('.wav')]
        output_audio = os.path.join(output_folder, f'{folder_name}_output_audio.wav')
        json_file = os.path.join(output_folder, f'{folder_name}_timestamps.json')

        input_streams = [ffmpeg.input(file) for file in input_files]
        audio_concat = ffmpeg.concat(*input_streams, v=0, a=1)
        audio_concat.output(output_audio).run(cmd=ffmpeg_path, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        timestamps = []
        start_time = 0

        for audio_file in input_files:
            audio_duration = ffmpeg.probe(audio_file, cmd=ffprobe_path)['format']['duration']
            timestamps.append({
                'file_name': os.path.basename(audio_file),
                'start_time': start_time,
                'end_time': start_time + float(audio_duration)
            })
            start_time += float(audio_duration)

        with open(json_file, 'w') as f:
            json.dump(timestamps, f, indent=4)

        print(f"Audio concatenation and JSON generation for folder '{folder_name}' complete. Output files saved to '{output_folder}'.")

def process_folders_concurrently(base_folder, output_folder, batch_size=16):
    input_folders = [os.path.join(base_folder, folder) for folder in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, folder))]
    with ThreadPoolExecutor() as executor:
        for i in range(0, len(input_folders), batch_size):
            batch_folders = input_folders[i:i + batch_size]
            executor.submit(concat_audio_in_folders, batch_folders, output_folder)

if __name__ == "__main__":
    base_folder = r'D:\DS_10283_2774'  # Replace with your actual path
    output_folder = r'D:\VCTK'  # Replace with your output folder path
    process_folders_concurrently(base_folder, output_folder, batch_size=16)
