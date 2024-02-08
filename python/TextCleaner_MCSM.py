import re

def find_audio(sequence):
    for i in range(0, len(sequence) - 8 + 1, 2):
        subseq = sequence[i:i + 8]
        if sequence.find(subseq, i + 8) != -1:
            return subseq
        
def main(file_path):
    with open(file_path, 'rb') as file:
        file_content = file.read()
    hex = file_content.hex()

    parts = re.split(r'080{6}010{6}080{14}', hex) # 切成 None Audio None Audio None Speaker None Text None /n

    main_parts = []
    target = bytes([
        0x2C, 0x00, 0x00, 0x00, 0x14, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x27, 0xAD, 0xEE, 0x2F, 
        0x6B, 0x0D, 0x9A, 0x63, 0x00, 0x00, 0x00, 0x00, 0x14, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x27, 0xAD, 0xEE, 0x2F, 0x6B, 0x0D, 0x9A, 0x63, 0x02, 0x00, 0x00, 0x00, 
        0xAF, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00
        ])
    for i, part in enumerate(parts):
        if i == 0:
            part = part[40:]
        if target.hex() not in part:
            main_parts.append(part)

    for main_part in main_parts:
        sub_parts = re.split(r'0c0{6}.{16}0c0{6}.{16}080{22}.{2}0{6}.{2}0{6}.{2}0{6}', main_part) # 切成 None Audio None Audio | Speaker None Text None
        for i, sub_part in enumerate(sub_parts):
            if i == 0:
                audio_hex = find_audio(sub_part)
                audio = int(''.join(reversed([audio_hex[i:i+2] for i in range(0, len(audio_hex), 2)])), 16) # hex大端序转uint32小端序
                print("Audio:", audio)
            if i == 1:
                subsub_parts = re.split(r'(?!00).{2}0{6}(?!00).{2}0{6}', sub_part)
                speaker = bytes.fromhex(subsub_parts[0]).decode('utf-8')
                text = bytes.fromhex(subsub_parts[1]).decode('utf-8')
                text = re.sub(r'\{[^}]*\}', '', text)
                text = re.sub(r'\[[^\]]*\]', '', text)
                print("Speaker:", speaker)
                print("Text:", text)
                print("=====================================")

if __name__ == "__main__":
    file_path = r"E:\Dataset\ttarch2\MinecraftStoryMode Season1\MCSM_pc_Minecraft101_data\env_foreststage_english.landb"
    main(file_path)