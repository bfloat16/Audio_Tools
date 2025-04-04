import struct
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import msgpack
import os

def read_idx(filename):
    encrypt_key = 'c6eahbq9sjuawhvdr9kvhpsm5qv393ga'.encode('utf-8')
    pack_encrypt_key = 'ARC-PACKPASSWORD'.encode('utf-8')  # 必须正好16字节
    
    pack_infos = []
    with open(filename, 'rb') as f:
        while True:
            len_bytes = f.read(4)
            if not len_bytes:
                break
            data_len = struct.unpack('<i', len_bytes)[0]
            
            encrypted_data = f.read(data_len)
            
            cipher = AES.new(encrypt_key, AES.MODE_CBC, pack_encrypt_key)
            decrypted = cipher.decrypt(encrypted_data)
            
            try:
                decrypted = unpad(decrypted, AES.block_size)
            except ValueError:
                pass
            
            info = msgpack.unpackb(decrypted, raw=False)
            pack_infos.append(info)
    
    return pack_infos

def decrypt_bin(bin_file, index_pos, size):
    encrypt_key = 'c6eahbq9sjuawhvdr9kvhpsm5qv393ga'.encode('utf-8')
    pack_encrypt_key = 'ARC-PACKPASSWORD'.encode('utf-8')
    
    with open(bin_file, 'rb') as f:
        f.seek(index_pos)
        encrypted_data = f.read(size)
    
    cipher = AES.new(encrypt_key, AES.MODE_CBC, pack_encrypt_key)
    decrypted = cipher.decrypt(encrypted_data)
    
    try:
        decrypted = unpad(decrypted, AES.block_size)
    except ValueError:
        pass
    
    return decrypted

def main():
    file = 'scripts'
    pack_list = read_idx(file + '.idx')

    for pack in pack_list:
        print(f"文件名: {pack['fileName']}, 大小: {pack['size']}, 偏移量: {pack['index']}")
        data = decrypt_bin(file + ".bin", pack['index'], pack['size'])
        os.makedirs(os.path.dirname(pack['fileName'][1:]), exist_ok=True)  # 创建目录
        with open(pack['fileName'][1:], 'wb') as f:
            f.write(data)

if __name__ == '__main__':
    main()