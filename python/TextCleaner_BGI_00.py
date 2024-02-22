import struct

def find_subarray(data, sub, start=0, exact=False):
    index = data.find(sub, start)
    if exact and index != -1:
        if data[index:index+len(sub)] != sub:
            return -1
    return index

def slice_bytes(data, start, end=None):
    if end:
        return data[start:end]
    return data[start:]

def BGI(file_path):
    with open(file_path, 'rb') as file:
        script_buffer = file.read()

    header_length = 0

    magic_bytes = bytearray([
        0x42, 0x75, 0x72, 0x69, 0x6B,
        0x6F, 0x43, 0x6F, 0x6D, 0x70,
        0x69, 0x6C, 0x65, 0x64, 0x53,
        0x63, 0x72, 0x69, 0x70, 0x74,
        0x56, 0x65, 0x72, 0x31, 0x2E,
        0x30, 0x30, 0x00
    ])

    if script_buffer.startswith(magic_bytes):
        header_length = 0x1C + struct.unpack_from("<I", script_buffer, 0x1C)[0]

    script_buffer = slice_bytes(script_buffer, header_length)

    first_text_offset = 0
    offset = find_subarray(script_buffer, b'\x7F\x00\x00\x00', 0)

    if 0 <= offset <= 128:
        first_text_offset = struct.unpack_from("<I", script_buffer, offset + 4)[0]

    int_text_offset_label = find_subarray(script_buffer, b'\x00\x03\x00\x00\x00', 0)

    all_texts = ""
    while int_text_offset_label != -1:
        int_text_offset = struct.unpack_from("<I", script_buffer, int_text_offset_label + 5)[0]
        if first_text_offset < int_text_offset < len(script_buffer):
            end_index = find_subarray(script_buffer, b'\x00', int_text_offset, exact=True)
            bytes_text_block = slice_bytes(script_buffer, int_text_offset, end_index)
            if bytes_text_block:
                str_text = bytes_text_block.decode('shift_jis').replace("\n", r"\n")
                all_texts += str_text + "\n"  # 将文本追加到字符串
        int_text_offset_label = find_subarray(script_buffer, b'\x00\x03\x00\x00\x00', int_text_offset_label + 1)
    return all_texts