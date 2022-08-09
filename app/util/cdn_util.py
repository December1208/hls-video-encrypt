import hashlib
import time
from urllib.parse import urlparse


class SignType:
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'


class TencentCDNURLGenerate:

    def __init__(self, category, key, sign_key='sign', time_key='t', ttl_format=10):
        self.category = category
        self.key = key
        self.sign_key = sign_key
        self.time_key = time_key

        # SignType.D 才需要
        self.ttl_format = ttl_format

    def generate_url(self, url):
        if self.category == SignType.A:
            raise
        elif self.category == SignType.B:
            raise
        elif self.category == SignType.C:
            raise
        elif self.category == SignType.D:
            return self._type_d_generate_url(url)
        else:
            # do nothing
            raise

    def _type_a_generate_url(self, url):
        raise NotImplementedError

    def _type_b_generate_url(self, url):
        raise NotImplementedError

    def _type_c_generate_url(self, url):
        raise NotImplementedError

    def _type_d_generate_url(self, url):
        now = int(time.time())
        parsed_url = urlparse(url)
        ts = now if self.ttl_format == 10 else hex(now)[2:]
        sign = hashlib.md5(('%s%s%s' % (self.key, parsed_url.path, ts)).encode()).hexdigest()
        request_url = '%s://%s%s?%s=%s&%s=%s' % (
            parsed_url.scheme, parsed_url.hostname, parsed_url.path, self.sign_key, sign, self.time_key, ts)
        return request_url


if __name__ == '__main__':
    tencent_cdn_url_generate = TencentCDNURLGenerate(category=SignType.D, key="")

    req_url = tencent_cdn_url_generate.generate_url('https://videotest2.lintcode.com/static/encrypt_media/4160075117d1494fad994a8980788e74/8736eecefb979dcc_22.ts')
    print(req_url)


