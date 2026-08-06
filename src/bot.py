import os
import asyncio
import traceback
import discord
from src.config import DISCORD_TOKEN, BOARDS, PORTAL_ID, PORTAL_PW, ADMIN_CHANNEL_ID

from src.crawlers.factory import get_crawler
from src.config import load_data, save_data
from src.logger import logger

def create_notice_embed(board_name: str, notice: dict) -> discord.Embed:
    """공지사항 디스코드 Embed 메세지를 생성합니다."""
    embed = discord.Embed(
        title=notice['title'],
        url=notice['link'],
        color=0x002F6C
    )
    embed.set_author(
        name=f"[{board_name}] 새 공지",
        icon_url="https://www.seoultech.ac.kr/site/www/images/intro/img_ui05.gif"
    )


    
    if notice.get('author'):
        embed.add_field(name="작성자", value=notice['author'], inline=True)
    if notice.get('date'):
        embed.add_field(name="작성일", value=notice['date'], inline=True)
        
    if notice.get('major'):
        embed.add_field(name="전공분야", value=notice['major'], inline=False)
    if notice.get('recruit_count'):
        embed.add_field(name="모집인원", value=f"{notice['recruit_count']}명", inline=True)
    if notice.get('work_period'):
        embed.add_field(name="근무기간", value=notice['work_period'], inline=True)
    if notice.get('recruit_period'):
        embed.add_field(name="모집기간", value=notice['recruit_period'], inline=True)
        
    embed.set_footer(text=f"게시글 번호: {notice['id']} • 고로시 봇 v2")
    return embed


async def send_admin_error_alert(admin_channel, board_name: str, url: str, error: Exception):
    """크롤링 오류 발생 시 관리자 채널로 에러 알림을 보냅니다."""
    if not admin_channel:
        return
    try:
        embed = discord.Embed(
            title=f"❌ 크롤러 에러 발생 - {board_name}",
            description=f"**에러 메시지**: `{error}`\n**대상 URL**: {url}",
            color=0xFF0000
        )
        tb_str = traceback.format_exc()
        if len(tb_str) > 1000:
            tb_str = tb_str[:1000] + "\n... (truncated)"
        embed.add_field(name="Traceback", value=f"```python\n{tb_str}\n```", inline=False)
        await admin_channel.send(embed=embed)
    except Exception as send_err:
        logger.error(f"[Admin] Failed to send error alert: {send_err}")


async def process_board(board: dict, state_data: dict, client: discord.Client, admin_channel):
    """단일 게시판의 크롤링, 판단, 메세지 전송 및 상태 업데이트를 처리합니다."""
    board_name = board['name']
    crawler_type = board['crawler_type']
    url = board['url']
    
    test_channel_id = os.getenv('TEST_CHANNEL_ID')
    channel_id = int(test_channel_id) if test_channel_id else board.get('channel_id')

    if not channel_id:
        logger.warning(f"[{board_name}] Channel ID is missing in config.")
        return
        
    channel = client.get_channel(channel_id)
    if not channel:
        logger.warning(f"[{board_name}] Channel {channel_id} not found.")
        return


    # 1. 공지 데이터 수집
    try:
        crawler = get_crawler(crawler_type, url)
        notices = crawler.get_notices(portal_id=PORTAL_ID, portal_pw=PORTAL_PW)
    except Exception as e:
        logger.error(f"[{board_name}] Error fetching notices: {e}")
        await send_admin_error_alert(admin_channel, board_name, url, e)
        return

    if not notices:
        logger.info(f"[{board_name}] No notices found.")
        return

    # 2. 게시판 타입별 하이브리드 상태 관리 (일반: int, 인턴십: list)
    saved_state = state_data.get(board_name)
    is_list_type = (crawler_type == 'internship') or isinstance(saved_state, list)

    # 3. 최초 실행 동기화 (도배 방지)
    if saved_state is None:
        if is_list_type:
            current_ids = [n['id'] for n in notices]
            state_data[board_name] = sorted(current_ids)[-200:]
        else:
            max_id = max(n['id'] for n in notices)
            state_data[board_name] = max_id
            
        save_data(state_data)
        logger.info(f"[{board_name}] First run sync done without sending alerts.")
        return

    # 4. 신규 공지 필터링
    if is_list_type:
        seen_set = set(saved_state if isinstance(saved_state, list) else [saved_state])
        new_notices = [n for n in notices if n['id'] not in seen_set]
    else:
        last_id = saved_state if isinstance(saved_state, int) else max(saved_state)
        new_notices = [n for n in notices if n['id'] > last_id]

    if not new_notices:
        return

    # 5. 신규 공지 전송
    new_notices.sort(key=lambda x: x['id'])
    logger.info(f"[{board_name}] Found {len(new_notices)} new notice(s). Processing...")

    success_ids = []
    for notice in new_notices:
        embed = create_notice_embed(board_name, notice)
        try:
            await channel.send(embed=embed)
            logger.info(f"[{board_name}] Sent notice {notice['id']}: {notice['title']}")
            success_ids.append(notice['id'])
        except Exception as e:
            logger.error(f"[{board_name}] Failed to send notice {notice['id']}: {e}")
            
        await asyncio.sleep(1)
        
    # 6. 성공한 ID 기준 상태 저장
    if success_ids:
        if is_list_type:
            seen_set = set(saved_state if isinstance(saved_state, list) else [saved_state])
            seen_set.update(success_ids)
            state_data[board_name] = sorted(list(seen_set))[-200:]
        else:
            max_success_id = max(success_ids)
            last_id = saved_state if isinstance(saved_state, int) else max(saved_state)
            state_data[board_name] = max(last_id, max_success_id)
            
        save_data(state_data)
        logger.info(f"[{board_name}] Updated state_data to: {state_data[board_name]}")


async def run_bot():
    """디스코드 봇 메인 실행 루틴"""
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN is not set.")
        return

    test_channel_id = os.getenv('TEST_CHANNEL_ID')
    if test_channel_id:
        logger.info(f"🧪 [TEST MODE ENABLED] TEST_CHANNEL_ID({test_channel_id}) 감지됨! 모든 공지가 테스트 채널로 우회됩니다.")

    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logger.info(f"Logged in as {client.user}")
        
        try:
            state_data = load_data()
            admin_channel = client.get_channel(ADMIN_CHANNEL_ID) if ADMIN_CHANNEL_ID else None
            if ADMIN_CHANNEL_ID and not admin_channel:
                logger.warning(f"[Admin] Warning: Admin channel {ADMIN_CHANNEL_ID} not found.")

            for board in BOARDS:
                await process_board(board, state_data, client, admin_channel)

        finally:
            await client.close()

    try:
        await client.start(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Error starting discord client: {e}")


