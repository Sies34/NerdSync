import os
import re
import subprocess
from dotenv import load_dotenv
from rocketchat_API.rocketchat import RocketChat

# .env-bestand laden
load_dotenv()

server_url = os.getenv("SERVER_URL")
api_token = os.getenv("API_TOKEN")
user_id = os.getenv("USER_ID")

rocket = RocketChat(user_id=user_id, auth_token=api_token, server_url=server_url, ssl_verify=True)

channel_name = "NerdAvond"
channel_info = rocket.channels_info(channel=channel_name).json()
room_id = channel_info.get('channel', {}).get('_id')

youtube_regex = r"(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w\-]+)"
timestamp_file = "last_timestamp.txt"

def download_youtube_url(url):
    print(f"Downloaden: {url}")
    try:
        subprocess.run(["yt-dlp", url], check=True)
        return True
    except Exception as e:
        print(f"Fout bij downloaden: {e}")
        return False

def get_last_timestamp():
    if os.path.exists(timestamp_file):
        with open(timestamp_file, "r") as f:
            return f.read().strip()
    return None

def set_last_timestamp(ts):
    with open(timestamp_file, "w") as f:
        f.write(ts)

def reageer_op_bericht(room_id, message_id, tekst):
    rocket.chat_post_message(
        room_id=room_id,
        text=tekst,
        tmid=message_id  # Reageer in thread
    )

if room_id:
    last_ts = get_last_timestamp()
    params = {}
    if last_ts:
        params["oldest"] = last_ts

    messages = rocket.channels_history(room_id=room_id, **params).json()
    new_messages = messages.get('messages', [])
    new_messages.sort(key=lambda m: m['ts'])

    for message in new_messages:
        print(f"{message['u']['username']}: {message['msg']}")
        urls = re.findall(youtube_regex, message['msg'])
        for url in urls:
            if download_youtube_url(url):
                reageer_op_bericht(room_id, message['_id'], f"✅ Download van {url} is gelukt!")
            else:
                reageer_op_bericht(room_id, message['_id'], f"❌ Download van {url} is mislukt.")
    if new_messages:
        newest_ts = new_messages[-1]['ts']['$date'] / 1000 if isinstance(new_messages[-1]['ts'], dict) else new_messages[-1]['ts']
        set_last_timestamp(str(newest_ts))
else:
    print("Kan het room_id niet vinden. Controleer of het kanaal bestaat.")