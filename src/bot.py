import asyncio
import traceback
import discord
from src.config import DISCORD_TOKEN, BOARDS, PORTAL_ID, PORTAL_PW, ADMIN_CHANNEL_ID
from src.crawlers.factory import get_crawler
from src.config import load_data, save_data

async def run_bot():
    if not DISCORD_TOKEN:
        print("DISCORD_TOKEN is not set.")
        return

    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user}")
        
        try:
            state_data = load_data()
            
            admin_channel = None
            if ADMIN_CHANNEL_ID:
                admin_channel = client.get_channel(ADMIN_CHANNEL_ID)
                if not admin_channel:
                    print(f"[Admin] Warning: Admin channel {ADMIN_CHANNEL_ID} not found.")

            for board in BOARDS:
                board_name = board['name']
                crawler_type = board['crawler_type']
                url = board['url']
                
                channel_id = board.get('channel_id')
                if not channel_id:
                    print(f"[{board_name}] Channel ID is missing in config.")
                    continue
                    
                channel = client.get_channel(channel_id)
                if not channel:
                    print(f"[{board_name}] Channel {channel_id} not found.")
                    continue

                try:
                    crawler = get_crawler(crawler_type, url)
                    # Pass credentials if needed (e.g. internship)
                    notices = crawler.get_notices(portal_id=PORTAL_ID, portal_pw=PORTAL_PW)
                except Exception as e:
                    err_msg = f"[{board_name}] Error fetching notices: {e}"
                    print(err_msg)
                    traceback.print_exc()
                    
                    # Send error notification to admin channel if set
                    if admin_channel:
                        try:
                            embed = discord.Embed(
                                title=f"❌ 크롤러 에러 발생 - {board_name}",
                                description=f"**에러 메시지**: `{e}`\n**대상 URL**: {url}",
                                color=0xFF0000
                            )
                            tb_str = traceback.format_exc()
                            if len(tb_str) > 1000:
                                tb_str = tb_str[:1000] + "\n... (truncated)"
                            embed.add_field(name="Traceback", value=f"```python\n{tb_str}\n```", inline=False)
                            await admin_channel.send(embed=embed)
                        except Exception as send_err:
                            print(f"[Admin] Failed to send error alert: {send_err}")
                    continue

                if not notices:
                    print(f"[{board_name}] No notices found.")
                    continue

                last_bidx = state_data.get(board_name, 0)
                print(f"[{board_name}] Last checked ID: {last_bidx}")

                new_notices = [n for n in notices if n['id'] > last_bidx]
                
                if not new_notices:
                    print(f"[{board_name}] No new notices.")
                    continue
                    
                if last_bidx == 0:
                    max_id = max(n['id'] for n in new_notices)
                    state_data[board_name] = max_id
                    save_data(state_data)
                    print(f"[{board_name}] First run. Synchronized last bidx to {max_id}")
                    continue

                new_notices.sort(key=lambda x: x['id'])
                print(f"[{board_name}] Found {len(new_notices)} new notices.")

                success_ids = []
                for notice in new_notices:
                    embed = discord.Embed(
                        title=notice['title'],
                        url=notice['link'],
                        color=0x002F6C
                    )
                    embed.set_author(name=f"[{board_name}] 새 공지", icon_url="https://www.seoultech.ac.kr/common/images/favicon.ico")
                    
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
                    
                    try:
                        await channel.send(embed=embed)
                        print(f"[{board_name}] Sent notice {notice['id']}")
                        success_ids.append(notice['id'])
                    except Exception as e:
                        print(f"[{board_name}] Failed to send notice {notice['id']}: {e}")
                        
                    await asyncio.sleep(1)
                    
                if success_ids:
                    max_success_id = max(success_ids)
                    state_data[board_name] = max(last_bidx, max_success_id)
                    save_data(state_data)
                    print(f"[{board_name}] Updated last_bidx to {state_data[board_name]}")
        finally:
            await client.close()

    try:
        await client.start(DISCORD_TOKEN)
    except Exception as e:
        print(f"Error starting discord client: {e}")
