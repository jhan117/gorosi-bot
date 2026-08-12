import urllib.parse
from bs4 import BeautifulSoup
from src.crawlers.base import BaseCrawler
from src.config import TARGET_MAJORS

class InternshipCrawler(BaseCrawler):

    """
    [현장실습 지원센터 HTML 구조 실측 샘플]

    1. 일반 기업 테이블 (td = 10개):
    <tr>
        <td class="tac">33</td>                                                     <!-- td[0]: 순번 -->
        <td class="al"><a href="...apply_view.jsp?idx=8436">(주)대우건설</a></td>     <!-- td[1]: 기업명 및 idx -->
        <td class="al"><a href="...apply_view.jsp?idx=8436">대우건설...</a></td>     <!-- td[2]: 담당업무 및 idx -->
        <td class="al">안전공학과</td>                                              <!-- td[3]: 전공분야 -->
        <td class="tac">1</td>                                                     <!-- td[4]: 모집인원 -->
        <td class="tac">3</td>                                                     <!-- td[5]: 지원자수 -->
        <td class="tac">2026-09-01~<br>2026-12-20</td>                             <!-- td[6]: 근무기간 -->
        <td class="tac">2026-08-03 13:00 ~ 2026-08-07 16:00</td>                   <!-- td[7]: 모집기간 -->
        <td class="tac">장기</td>                                                   <!-- td[8]: 구분 -->
        <td class="tac"><a href="...">지원</a></td>                                 <!-- td[9]: 상태 -->
    </tr>

    2. KIST 인턴십 테이블 (td = 12개):
    <tr>
        <td class="tac">47</td>                                                     <!-- td[0]: 순번 -->
        <td class="al">청정수소융합연구소</td>                                        <!-- td[1]: 연구소/본부 -->
        <td class="al"><a href="...apply_view.jsp?idx=8443">에너지소재연구센터</a></td><!-- td[2]: 연구단/센터 & idx -->
        <td class="tac">김동익</td>                                                  <!-- td[3]: 담당자 -->
        <td class="al"><a href="...apply_view.jsp?idx=8443">(김동익) ...</a></td>    <!-- td[4]: 담당업무 & idx -->
        <td class="al">신소재공학과 (1명)</td>                                      <!-- td[5]: 전공분야 -->
        <td class="tac">1</td>                                                     <!-- td[6]: 모집인원 -->
        <td class="tac">0</td>                                                     <!-- td[7]: 지원자수 -->
        <td class="tac">2026-09-01~<br>2027-02-28</td>                             <!-- td[8]: 근무기간 -->
        <td class="tac">2026-08-06 00:00 ~ 2026-08-09 23:00</td>                   <!-- td[9]: 모집기간 -->
        <td class="tac">KIST</td>                                                  <!-- td[10]: 구분 -->
        <td class="tac"><a href="...">지원</a></td>                                 <!-- td[11]: 상태 -->
    </tr>
    """

    def __init__(self, url):

        super().__init__(url)
        self.login_url = "https://internship.seoultech.ac.kr/hcm/login/"

    def get_notices(self, **kwargs) -> list[dict]:
        """인턴십 공지사항 목록을 가져옵니다."""
        portal_id = kwargs.get('portal_id')
        portal_pw = kwargs.get('portal_pw')
        
        if not portal_id or not portal_pw:
            raise ValueError("Portal ID and PW are required for internship crawler")
            
        # 1. 로그인
        self._login(portal_id, portal_pw)
        
        # 2. 공지사항 페이지 요청
        response = self.session.get(self.url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        
        # 3. 로그인 성공 검증
        self._check_login_status(response.text)
            
        # 4. 공지사항 테이블 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        tr_elements = soup.find_all('tr')
        raw_notices = []
        
        for tr in tr_elements:
            notice = self._parse_row(tr)
            if notice:
                raw_notices.append(notice)
            
        if len(tr_elements) > 5 and len(raw_notices) == 0:
            raise ValueError(f"Parsing error: HTML 구조가 변경된 것 같습니다. 테이블 행(tr)이 {len(tr_elements)}개 발견되었으나 파싱된 공지가 0개입니다.")
            
        # 타과 전용 공지 필터링 (컴퓨터계열/전공무관만 수신)
        notices = [n for n in raw_notices if self._is_target_major(n['major'])]
        
        return notices

    def _login(self, portal_id: str, portal_pw: str):
        """포털 로그인을 수행합니다."""
        login_data = {
            "scheme": "https",
            "mode": "do",
            "site": "50256",
            "ref": "",
            "lang": "ko",
            "ip": "66.249.92.200",
            "id": portal_id,
            "pw": portal_pw
        }
        res = self.session.post(self.login_url, data=login_data, headers=self.headers, timeout=self.timeout)
        res.raise_for_status()

    def _check_login_status(self, html_text: str):
        """응답 HTML에서 로그인 실패 여부를 체크합니다."""
        error_keywords = ["로그인이 필요합니다", "비밀번호", "일치하지", "로그인 후 이용"]
        if any(keyword in html_text for keyword in error_keywords):
            snippet = html_text[:300].replace('\n', ' ')
            raise ValueError(f"Login failed or session expired. Check PORTAL_ID/PW. Snippet: {snippet}")

    def _extract_post_id(self, company_a) -> int | None:
        """게시글 고유 ID(post_id)를 추출합니다."""
        href = company_a.get('href', '')
        if '?idx=' not in href:
            return None
        
        no_str = href.split('?idx=')[1]
        if not no_str.isdigit():
            return None
        return int(no_str)

    def _is_target_major(self, major_text: str) -> bool:
        """전공분야가 수신 대상(컴퓨터/소프트웨어/인공지능/전공무관 등)인지 검사하며, 아예 기재되지 않은 경우 무조건 통과합니다."""
        if not major_text or not major_text.strip() or major_text.strip() in ("-", "None"):
            return True
        return any(keyword in major_text for keyword in TARGET_MAJORS)


    def _parse_row(self, tr) -> dict | None:
        """한 행(tr)의 공지 데이터를 파싱하여 딕셔너리로 반환합니다."""
        td_list = tr.find_all('td')
        if not td_list or len(td_list) < 9:
            return None
            
        if len(td_list) == 10:
            company_a = td_list[1].find('a')
            job_a = td_list[2].find('a')
            if not company_a or not job_a: 
                return None
            
            company_name = company_a.text.strip()
            job_title = job_a.text.strip()
            major = td_list[3].text.strip()
            recruit_count = td_list[4].text.strip()
            work_period = td_list[6].text.strip().replace('\n', ' ')
            recruit_period = td_list[7].text.strip().replace('\n', ' ')

        elif len(td_list) >= 12:
            company_a = td_list[2].find('a')
            job_a = td_list[4].find('a')
            if not company_a or not job_a: 
                return None
            
            company_name = f"{td_list[1].text.strip()} {company_a.text.strip()}"
            job_title = job_a.text.strip()
            major = td_list[5].text.strip()
            recruit_count = td_list[6].text.strip()
            work_period = td_list[8].text.strip().replace('\n', ' ')
            recruit_period = td_list[9].text.strip().replace('\n', ' ')
        else:
            return None

        post_id = self._extract_post_id(company_a)
        if post_id is None:
            return None

        title = f"[{company_name}] {job_title}"
        href = company_a.get('href', '')
        link = urllib.parse.urljoin(self.url, href)

        return {
            'id': post_id,
            'title': title[:100],
            'link': link,
            'major': major if major else '미기재',
            'recruit_count': recruit_count,
            'work_period': work_period,
            'recruit_period': recruit_period
        }


