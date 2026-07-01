import re
import urllib.parse
from bs4 import BeautifulSoup
from src.crawlers.base import BaseCrawler

class HousingCrawler(BaseCrawler):
    def get_notices(self, **kwargs) -> list[dict]:
        response = self.session.get(self.url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        notices = []
        seen = set()
        
        # 생활관은 a 태그에 bidx=가 포함된 요소 추출
        for a in soup.find_all('a', href=lambda h: h and 'bidx=' in h):
            href = a.get('href', '')
            parsed = urllib.parse.urlparse(href)
            params = urllib.parse.parse_qs(parsed.query)
            bidx_list = params.get('bidx')
            if not bidx_list:
                continue
                
            post_id = int(bidx_list[0])
            
            # 중복 파싱 방지
            if post_id in seen:
                continue
            seen.add(post_id)
            
            title = a.text.strip()
            if not title:
                title = "제목 없음"
                
            link = urllib.parse.urljoin(self.url, href)
            
            container = a.find_parent('div', class_='list')
            author = "생활관"
            date = ""
            if container:
                m = re.search(r'(\d{4}-\d{2}-\d{2})', container.text)
                if m:
                    date = m.group(1)
            
            notices.append({
                'id': post_id,
                'title': title[:100],
                'link': link,
                'author': author,
                'date': date
            })
            
        return notices
