import os
import sys
import asyncio

# 프로젝트 루트 경로를 sys.path에 추가하여 ModuleNotFoundError 예방
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import json
import traceback
import urllib.request
from src.bot import run_bot
from src.config import DISCORD_TOKEN, ADMIN_CHANNEL_ID
from src.logger import logger


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
            "title": f"[Critical] Error: {error_title}",
            "description": f"**Details**:\n```python\n{error_message}\n```",
            "color": 0xFF0000
        }]
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        logger.error(f"[Critical] Failed to send alert: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(asyncio.wait_for(run_bot(), timeout=120))
    except asyncio.TimeoutError:
        msg = "Bot execution timed out (>120s)."
        logger.error(msg)
        send_critical_alert("Timeout Error", msg)
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        msg = traceback.format_exc()
        logger.critical(f"[Critical] Unhandled error:\n{msg}")
        send_critical_alert("Unhandled Exception", msg[:1500])
        sys.exit(1)



