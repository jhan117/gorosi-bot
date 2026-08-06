import urllib.parse
from bs4 import BeautifulSoup
from src.crawlers.base import BaseCrawler

class SeoultechCrawler(BaseCrawler):
    """
    [서울과기대 일반/학사/장학/컴공 공지사항 HTML 구조 샘플]

    <table class="tbl_list">
        <tbody>
            <tr class="body_tr">
                <td class="dn1">11366 또는 <img alt="공지" ...></td>  <!-- td[0]: 공지 여부 및 순번 -->
                <td class="tit dn2">
                    <a href="?do=commonview&...&bidx=893609">           <!-- td[1]: 제목 및 bidx -->
                        [국제교류처] 해외파견학생 서류 합격자...
                    </a>
                </td>
                <td class="dn3">첨부파일</td>
                <td class="dn4">국제교류처</td>                           <!-- td[3]: 작성자 -->
                <td class="dn5">2026-08-06</td>                           <!-- td[4]: 작성일 -->
            </tr>
        </tbody>
    </table>
    """

    def get_notices(self, **kwargs) -> list[dict]:
        response = self.session.get(self.url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        notices = []
        for tr in soup.find_all('tr'):
            notice = self._parse_row(tr)
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

    def _parse_row(self, tr) -> dict | None:
        """한 행(tr)의 공지 데이터를 파싱하여 딕셔너리로 반환합니다."""
        td_list = tr.find_all('td')
        if not td_list or len(td_list) < 5:
            return None
            
        a_tag = td_list[1].find('a')
        if not a_tag:
            return None
            
        post_id = self._extract_bidx(a_tag)
        if post_id is None:
            return None

        title = a_tag.text.strip()
        href = a_tag.get('href', '')
        link = urllib.parse.urljoin(self.url, href)
        
        # 첫 번째 td가 숫자가 아니면 상단 고정 공지글로 판단
        num_str = td_list[0].text.strip()
        if not num_str.isdigit():
            title = f"[공지] {title}"
        
        author = td_list[3].text.strip()
        date = td_list[4].text.strip()
        
        return {
            'id': post_id,
            'title': title,
            'link': link,
            'author': author,
            'date': date
        }

