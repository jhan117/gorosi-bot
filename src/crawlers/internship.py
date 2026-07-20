import urllib.parse
from bs4 import BeautifulSoup
from src.crawlers.base import BaseCrawler

class InternshipCrawler(BaseCrawler):
    def __init__(self, url):
        super().__init__(url)
        self.login_url = "https://internship.seoultech.ac.kr/hcm/login/"

    def get_notices(self, **kwargs) -> list[dict]:
        portal_id = kwargs.get('portal_id')
        portal_pw = kwargs.get('portal_pw')
        
        if not portal_id or not portal_pw:
            raise ValueError("Portal ID and PW are required for internship crawler")
            
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
        
        response = self.session.get(self.url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        
        # 좀 더 포괄적인 로그인 실패 체크
        error_keywords = ["로그인이 필요합니다", "비밀번호", "일치하지", "로그인 후 이용"]
        if any(keyword in response.text for keyword in error_keywords):
            # HTML 앞부분 일부를 포함해 에러 메시지 생성 (디버깅용)
            snippet = response.text[:300].replace('\n', ' ')
            raise ValueError(f"Login failed or session expired. Check PORTAL_ID/PW. Snippet: {snippet}")
            
        soup = BeautifulSoup(response.text, 'html.parser')
        notices = []
        tr_elements = soup.find_all('tr')
        
        for tr in tr_elements:
            td_list = tr.find_all('td')
            if not td_list or len(td_list) < 9:
                continue
                
            no_str = td_list[0].text.strip()
            if not no_str.isdigit():
                continue
                
            post_id = int(no_str)
            
            if len(td_list) == 10:
                # 일반 기업
                company_a = td_list[1].find('a')
                job_a = td_list[2].find('a')
                if not company_a or not job_a: continue
                
                company_name = company_a.text.strip()
                job_title = job_a.text.strip()
                major = td_list[3].text.strip()
                recruit_count = td_list[4].text.strip()
                work_period = td_list[6].text.strip().replace('\n', ' ')
                recruit_period = td_list[7].text.strip().replace('\n', ' ')
            elif len(td_list) >= 12:
                # KIST
                company_a = td_list[2].find('a')
                job_a = td_list[4].find('a')
                if not company_a or not job_a: continue
                
                company_name = f"{td_list[1].text.strip()} {company_a.text.strip()}"
                job_title = job_a.text.strip()
                major = td_list[5].text.strip()
                recruit_count = td_list[6].text.strip()
                work_period = td_list[8].text.strip().replace('\n', ' ')
                recruit_period = td_list[9].text.strip().replace('\n', ' ')
            else:
                continue
                
            title = f"[{company_name}] {job_title}"
            href = company_a.get('href', '')
            link = urllib.parse.urljoin(self.url, href)
            
            notices.append({
                'id': post_id,
                'title': title[:100],
                'link': link,
                'major': major,
                'recruit_count': recruit_count,
                'work_period': work_period,
                'recruit_period': recruit_period
            })
            
        # HTML 구조 변경으로 인한 '조용한 파싱 실패' 감지
        if len(tr_elements) > 5 and len(notices) == 0:
            raise ValueError(f"Parsing error: HTML 구조가 변경된 것 같습니다. 테이블 행(tr)이 {len(tr_elements)}개 발견되었으나 파싱된 공지가 0개입니다.")
            
        return notices
