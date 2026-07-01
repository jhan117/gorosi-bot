import os
import json

# 디스코드 봇 토큰 및 인증 정보
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PORTAL_ID = os.getenv('PORTAL_ID')
PORTAL_PW = os.getenv('PORTAL_PW')

# 프로젝트 루트 디렉토리 계산 (src/ 의 상위 폴더)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'bidx.json')

# 게시판 설정
BOARDS = [
    {
        "name": "서울과기대 일반공지",
        "crawler_type": "seoultech",
        "url": "https://www.seoultech.ac.kr/service/info/notice/",
        "channel_id": 1332717887372333069
    },
    {
        "name": "서울과기대 학사공지",
        "crawler_type": "seoultech",
        "url": "https://www.seoultech.ac.kr/service/info/matters/",
        "channel_id": 1332717887372333069
    },
    {
        "name": "서울과기대 장학공지",
        "crawler_type": "seoultech",
        "url": "https://www.seoultech.ac.kr/service/info/janghak/",
        "channel_id": 1332717887372333069
    },
    {
        "name": "생활관 공지사항",
        "crawler_type": "housing",
        "url": "https://housing.seoultech.ac.kr/community/notice?boardFilter=58605",
        "channel_id": 1332717887372333069
    },
    {
        "name": "현장실습(인턴십) 공지",
        "crawler_type": "internship",
        "url": "https://internship.seoultech.ac.kr/mypage/recruit?list=1",
        "channel_id": 1521784473618743306
    },
    {
        "name": "KIST 인턴십",
        "crawler_type": "internship",
        "url": "https://internship.seoultech.ac.kr/mypage/recruit?list=2",
        "channel_id": 1521785807810334842
    }
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
