import re
import urllib.parse
from bs4 import BeautifulSoup
from src.crawlers.base import BaseCrawler

class HousingCrawler(BaseCrawler):
    """
    [생활관 공지사항 HTML 구조 샘플]

    <div class="list">
        <h2 class="has_board_tag">
            <a href="?do=commonview&...&bidx=893362">
                No.1022 2026년 8월 13일(목) 정기소독 안내...
            </a>
        </h2>
        <div class="date">
            <span>등록날짜 : 2026-07-30 &nbsp; 조회수 : 124</span>
        </div>
    </div>
    """

    def get_notices(self, **kwargs) -> list[dict]:
        response = self.session.get(self.url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        notices = []
        seen = set()
        
        # 생활관은 a 태그에 bidx=가 포함된 요소 추출
        for a in soup.find_all('a', href=lambda h: h and 'bidx=' in h):
            if a.find_parent(class_='thumb'):
                continue
                
            post_id = self._extract_bidx(a)
            if post_id is None or post_id in seen:
                continue
            seen.add(post_id)
            
            notice = self._parse_notice(a, post_id)
            if notice:
                notices.append(notice)
            
        return notices

    def _extract_bidx(self, a_tag) -> int | None:
        """a 태그의 href 쿼리 파라미터에서 bidx(게시글 ID)를 추출합니다."""
        href = a_tag.get('href', '')
        parsed = urllib.parse.urlparse(href)
        params = urllib.parse.parse_qs(parsed.query)
        bidx_list = params.get('bidx')
        if not bidx_list or not bidx_list[0].isdigit():
            return None
        return int(bidx_list[0])

    def _clean_title(self, a_tag) -> str:
        """게시글 제목 텍스트 정제 및 정규식 처리"""
        title = a_tag.text.strip()
        if title.upper() == 'VIEW':
            parent_box = a_tag.find_parent('div', class_='box')
            if parent_box and parent_box.find('b'):
                title = parent_box.find('b').text.strip()
        
        if not title:
            title = "제목 없음"
            
        title = re.sub(r'^No\.0\s+', '[공지] ', title)
        title = re.sub(r'^No\.\d+\s+', '', title)
        return title

    def _extract_date(self, a_tag) -> str:
        """컨테이너 요소에서 작성날짜(YYYY-MM-DD)를 추출합니다."""
        container = a_tag.find_parent('div', class_='list')
        if container:
            date_div = container.find(class_='date')
            target_text = date_div.text if date_div else container.text
            m = re.search(r'(\d{4}-\d{2}-\d{2})', target_text)
            if m:
                return m.group(1)
        return ""

    def _parse_notice(self, a_tag, post_id: int) -> dict:
        """a_tag 요소에서 공지 데이터를 가공하여 딕셔너리로 반환합니다."""
        title = self._clean_title(a_tag)
        href = a_tag.get('href', '')
        link = urllib.parse.urljoin(self.url, href)
        date = self._extract_date(a_tag)
        
        return {
            'id': post_id,
            'title': title[:100],
            'link': link,
            'author': "생활관",
            'date': date
        }

