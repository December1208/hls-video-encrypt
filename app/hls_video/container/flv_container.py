import os

import bitstring
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from app.hls_video import constants


class FLVContainer:
    container_type = constants.ContainerType.FLV

    def __init__(self, filename=None, bytes_input=None, offset_bytes=0):
        if filename:
            self.bs = bitstring.ConstBitStream(filename=filename, offset=offset_bytes * 8)
        elif bytes_input:
            self.bs = bitstring.ConstBitStream(bytes=bytes_input, offset=offset_bytes * 8)

        self.filename = filename
        self.current_directory = os.path.split(self.filename)[0]

    def encrypt(self, new_file_path, key, iv):
        fw = open(new_file_path, 'wb')
        type_ = self.bs.read('bytes:3')
        if type_ != b'FLV':
            raise
        fw.write(type_)
        fw.write(self.bs.read('bytes:10'))
        while self.bs.pos < self.bs.len:
            cipher = Cipher(algorithms.AES(key), modes.OFB(iv))
            encryptor = cipher.encryptor()

            fw.write(self.bs.read('bytes:1'))
            data_size = self.bs.read(24)
            tag_data = self.bs.read('bytes:7')
            # 对data数据进行加密
            payload = self.bs.read(f'bytes:{data_size.int}')
            payload = encryptor.update(payload) + encryptor.finalize()
            payload_length = "{:06X}".format(len(payload))
            if len(payload) != data_size.int:
                raise
            fw.write(bytes.fromhex(payload_length))
            fw.write(tag_data)
            fw.write(payload)
            previous_tag_size = self.bs.read(32)
            new_previous_tag_size = previous_tag_size.int + len(payload) - data_size.int
            fw.write(bytes.fromhex("{:08X}".format(new_previous_tag_size)))

        fw.close()
