from binascii import b2a_hex, a2b_hex

from Crypto.Cipher import AES
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms


class AESCrypt:
    """
    AES 加解密
    """

    def __init__(self, key, iv):
        self.key = key
        self.iv = iv

    def encrypt(self, text):
        """
        加密
        :param text: 密文
        :return:
        """

        cryptor = AES.new(self.key, AES.MODE_CBC, self.iv)
        text = self.pkcs7_padding(text)

        ciphertext = cryptor.encrypt(text)
        return ciphertext

    def decrypt(self, text):
        """
        解密
        :param text: 密文
        :return:
        """
        if not isinstance(text, bytes):
            text = text.encode()
        cryptor = AES.new(self.key, AES.MODE_CBC, self.iv)
        plain_text = self.pkcs7_unpadding(a2b_hex(cryptor.decrypt(text)))
        return plain_text

    @staticmethod
    def pkcs7_padding(data):
        if not isinstance(data, bytes):
            data = data.encode()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()

        padded_data = padder.update(data) + padder.finalize()

        return padded_data

    @staticmethod
    def pkcs7_unpadding(padded_data):
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data)

        try:
            uppadded_data = data + unpadder.finalize()
        except ValueError:
            raise Exception('无效的加密信息! ')
        else:
            return uppadded_data


if __name__ == '__main__':
    x = AESCrypt('jo8j9wGw%6HbxfFn', '0123456789ABCDEF').decrypt(
        "95780ba0943730051dccb5fe3918f9feac71754fea3873b762f5f4526de59281c409d31d10e3188ac1c6904df1ee1785f540add027020caecfdb52c66f416181"
    )
    print(x)
