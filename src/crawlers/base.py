import abc
import requests

class BaseCrawler(abc.ABC):
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36'
        }

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
