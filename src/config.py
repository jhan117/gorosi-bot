import os
import json
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

# 디스코드 봇 토큰 및 인증 정보
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PORTAL_ID = os.getenv('PORTAL_ID')
PORTAL_PW = os.getenv('PORTAL_PW')
ADMIN_CHANNEL_ID = 1521769149229957202

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'bidx.json')

# 게시판 설정
BOARDS = [
    {
        "name": "서울과기대 일반 공지",
        "crawler_type": "seoultech",
        "url": "https://www.seoultech.ac.kr/service/info/notice/",
        "channel_id": 1521769621168853144
    },
    {
        "name": "서울과기대 학사 공지",
        "crawler_type": "seoultech",
        "url": "https://www.seoultech.ac.kr/service/info/matters/",
        "channel_id": 1521772768654266520
    },
    {
        "name": "서울과기대 장학 공지",
        "crawler_type": "seoultech",
        "url": "https://www.seoultech.ac.kr/service/info/janghak/",
        "channel_id": 1521772796542451744
    },
    {
        "name": "컴공 학부 공지",
        "crawler_type": "seoultech",
        "url": "https://computer.seoultech.ac.kr/info/notice",
        "channel_id": 1521774310463901796
    },
    {
        "name": "생활관 공지사항",
        "crawler_type": "housing",
        "url": "https://housing.seoultech.ac.kr/community/notice?boardFilter=DOMESTIC",
        "channel_id": 1521774721698369616
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
