import os

import bitstring

from app.hls_video import constants


class TSContainer:
    container_type = constants.ContainerType.TS

    def __init__(self, filename=None, bytes_input=None, offset_bytes=0):
        if filename:
            self.bs = bitstring.ConstBitStream(filename=filename, offset=offset_bytes * 8)
        elif bytes_input:
            self.bs = bitstring.ConstBitStream(bytes=bytes_input, offset=offset_bytes * 8)

        self.filename = filename
        self.current_directory = os.path.split(self.filename)[0]
