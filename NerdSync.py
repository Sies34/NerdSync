import os
from dotenv import load_dotenv
from rocketchat_API.rocketchat import RocketChat

# .env-bestand laden
load_dotenv()

server_url = os.getenv("SERVER_URL")
api_token = os.getenv("API_TOKEN")
user_id = os.getenv("USER_ID")

# Verbinden met Rocket.Chat
rocket = RocketChat(user_id=user_id, auth_token=api_token, server_url=server_url, ssl_verify=True)

# Kanaal-ID ophalen en berichten lezen
channel_name = "NerdAvond"
channel_info = rocket.channels_info(channel=channel_name).json()
room_id = channel_info.get('channel', {}).get('_id')

if room_id:
    messages = rocket.channels_history(room_id=room_id).json()
    for message in messages.get('messages', []):
        print(f"{message['u']['username']}: {message['msg']}")
else:
    print("Kan het room_id niet vinden. Controleer of het kanaal bestaat.")
