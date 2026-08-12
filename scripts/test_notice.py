import os
import sys
import asyncio
import argparse

# 루트 경로를 sys.path에 추가하여 src 모듈 임포트 가능하게 함
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import discord
from src.config import BOARDS, DISCORD_TOKEN, PORTAL_ID, PORTAL_PW
from src.crawlers.factory import get_crawler
from src.bot import create_notice_embed

async def test_notice(board_name: str, notice_id: int = None):
    # 1. TEST_CHANNEL_ID 확인
    test_channel_id = os.getenv('TEST_CHANNEL_ID')
    if not test_channel_id:
        print("❌ 오류: .env 파일에 TEST_CHANNEL_ID가 설정되어 있지 않습니다.")
        return

    # 2. 보드 설정 찾기
    board_config = next((b for b in BOARDS if b['name'] == board_name), None)
    if not board_config:
        print(f"❌ 오류: '{board_name}' 게시판을 찾을 수 없습니다.")
        print("사용 가능한 게시판 목록:")
        for b in BOARDS:
            print(f"  - {b['name']}")
        return

    print(f"🔍 '{board_name}' 공지사항을 가져오는 중...")
    try:
        crawler = get_crawler(board_config['crawler_type'], board_config['url'])
        notices = crawler.get_notices(portal_id=PORTAL_ID, portal_pw=PORTAL_PW)
    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
        return
    
    if not notices:
        print("⚠️ 공지사항을 하나도 찾지 못했습니다.")
        return

    # 3. 타겟 공지 찾기
    if notice_id:
        target_notice = next((n for n in notices if n['id'] == notice_id), None)
        if not target_notice:
            print(f"❌ 오류: 첫 페이지에서 공지 번호 {notice_id}를 찾을 수 없습니다.")
            print("현재 첫 페이지에 있는 최근 공지 번호들:", [n['id'] for n in notices])
            return
    else:
        target_notice = notices[0] # ID 지정 안하면 가장 최근 공지 사용

    print(f"✅ 공지 발견: [{target_notice['id']}] {target_notice['title']}")
    print("🚀 디스코드로 메시지 전송 시도 중...")
    
    # 4. 디스코드 클라이언트 실행하여 단일 메시지 전송
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        channel = client.get_channel(int(test_channel_id))
        if not channel:
            print(f"❌ 오류: TEST_CHANNEL_ID({test_channel_id})에 해당하는 채널을 찾을 수 없거나 봇이 채널에 접근할 수 없습니다.")
            await client.close()
            return
            
        embed = create_notice_embed(board_name, target_notice)
        try:
            await channel.send(embed=embed)
            print("🎉 성공적으로 테스트 공지를 전송했습니다!")
        except Exception as e:
            print(f"❌ 메시지 전송 실패: {e}")
        finally:
            await client.close() # 전송 완료 후 봇 종료

    try:
        await client.start(DISCORD_TOKEN)
    except Exception as e:
        print(f"❌ 봇 시작 실패: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="상태 파일 수정 없이 특정 공지를 바로 테스트 전송합니다.")
    parser.add_argument("board_name", type=str, help="테스트할 게시판 이름 (예: '컴공 학부 공지')")
    parser.add_argument("--id", type=int, default=None, help="(선택) 테스트할 특정 공지의 번호 (ID). 생략 시 가장 최근 공지를 전송합니다.")
    
    args = parser.parse_args()
    asyncio.run(test_notice(args.board_name, args.id))
