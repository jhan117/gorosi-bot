import abc
import requests
import os
import certifi
from src.config import BASE_DIR

# 프로그램 시작시 1번만 합본 인증서 생성 (certifi + 중간 인증서)
EXTRA_CA_PATH = os.path.join(BASE_DIR, 'data', 'seoultech_ca.crt')
COMBINED_CA_PATH = os.path.join(BASE_DIR, 'data', 'combined_ca.crt')

if os.path.exists(EXTRA_CA_PATH):
    with open(certifi.where(), 'rb') as f_base, open(EXTRA_CA_PATH, 'rb') as f_extra:
        with open(COMBINED_CA_PATH, 'wb') as f_out:
            f_out.write(f_base.read() + b'\n' + f_extra.read())
    CA_BUNDLE = COMBINED_CA_PATH
else:
    CA_BUNDLE = True


class BaseCrawler(abc.ABC):
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.timeout = 15
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session.verify = CA_BUNDLE

    @abc.abstractmethod
    def get_notices(self, **kwargs) -> list[dict]:
        """
        Extract notices from the website and return a list of dictionaries.
        Each dict should contain at least:
        - id (int): Monotonically increasing unique identifier
        - title (str)
        - link (str)
        - author (str)
        - date (str)
        """
        pass
