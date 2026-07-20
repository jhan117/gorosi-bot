import asyncio
import sys
import json
import traceback
import urllib.request
from src.bot import run_bot
from src.config import DISCORD_TOKEN, ADMIN_CHANNEL_ID

def send_critical_alert(error_title, error_message):
    if not DISCORD_TOKEN or not ADMIN_CHANNEL_ID:
        return
    url = f"https://discord.com/api/v10/channels/{ADMIN_CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "embeds": [{
            "title": f"🚨 치명적 오류 발생: {error_title}",
            "description": f"**내용**:\n```python\n{error_message}\n```",
            "color": 0xFF0000
        }]
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"Failed to send critical alert: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(asyncio.wait_for(run_bot(), timeout=120))
    except asyncio.TimeoutError:
        msg = "봇 실행 시간이 120초를 초과하여 강제 종료되었습니다. 무한 루프나 네트워크 응답 지연을 확인하세요."
        print(msg)
        send_critical_alert("타임아웃(Timeout) 강제 종료", msg)
        sys.exit(0)
    except KeyboardInterrupt:
        print("Bot stopped by user.")
    except Exception as e:
        msg = traceback.format_exc()
        print(f"Bot encountered a critical error:\n{msg}")
        send_critical_alert("비정상 강제 종료", msg[:1500])
        sys.exit(1)


