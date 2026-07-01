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
            
            # 공지 작성자나 날짜는 부모 tr 등을 따라가야 하지만, 
            # 기존 crawler.py와 동일하게 처리
            tr = a.find_parent('tr')
            author = "생활관"
            date = ""
            if tr:
                tds = tr.find_all('td')
                if len(tds) >= 5:
                    author = tds[3].text.strip()
                    date = tds[4].text.strip()
            
            notices.append({
                'id': post_id,
                'title': title[:100],
                'link': link,
                'author': author,
                'date': date
            })
            
        return notices
