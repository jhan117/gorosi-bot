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
        
        if "로그인이 필요합니다" in response.text:
            raise ValueError("Login failed or session expired.")
            
        soup = BeautifulSoup(response.text, 'html.parser')
        notices = []
        
        for tr in soup.find_all('tr'):
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
            
        return notices
