import urllib.parse
from bs4 import BeautifulSoup
from src.crawlers.base import BaseCrawler

class SeoultechCrawler(BaseCrawler):
    def get_notices(self, **kwargs) -> list[dict]:
        response = self.session.get(self.url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        notices = []
        seen = set()
        
        for tr in soup.find_all('tr'):
            td_list = tr.find_all('td')
            if not td_list or len(td_list) < 5:
                continue
                
            a_tag = td_list[1].find('a')
            if not a_tag:
                continue
                
            href = a_tag.get('href', '')
            parsed = urllib.parse.urlparse(href)
            params = urllib.parse.parse_qs(parsed.query)
            bidx_list = params.get('bidx')
            
            if not bidx_list:
                continue
                
            post_id = int(bidx_list[0])
            title = a_tag.text.strip()
            link = urllib.parse.urljoin(self.url, href)
            
            # 첫번째 td로 공지인지 판별
            num_str = td_list[0].text.strip()
            is_notice = not num_str.isdigit()
            
            if is_notice:
                title = f"[공지] {title}"
            
            author = td_list[3].text.strip()
            date = td_list[4].text.strip()
            
            notices.append({
                'id': post_id,
                'title': title,
                'link': link,
                'author': author,
                'date': date
            })
            
        return notices
