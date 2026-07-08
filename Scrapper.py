from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl import functions
import asyncio
import os
import re
import time

# --- CONFIGURATION ---
api_id = 39201837
api_hash = 'ca4ca441f67605320f3e71f2539a3eec'
BOT_TOKEN = '8728242418:AAFgUFtn7wfOpB38rKP5jB64kOokeC8N04c' 
STRING_SESSION = '1BVtsOHMBu2wBsIP5CrAmCfPT8EfiF2GuS7hx-pIiysO2qCP-fLYgHgQTRkCT6SC0nC5T_q_jaNY1UFd5mpRKwWWAw3ZR2Nqe9GZLFBcoFp_jh5Pc4cOdZhO96aiMzZLFiyFnkB99rrBpxfoxPZARfRcjZCmy4fOHtyn1ly-57D4TRihk4ZcNEmHemdw5FNj6wFuSfZxesVItC3QYdIcnXAvhRFCzicsClCb6M0lPH6p2FCmFIvfRtoP2SVCvv6YMOIC9aVcNcELsECotb2vyURpckWW3jcM4pjLShjSHbbhMz-mLp6sM4whkZKedsf34ii67S-iJPARFTFcWsPVaTZ2F583LLQ4='
# ---------------------

user_client = TelegramClient(StringSession(STRING_SESSION), api_id, api_hash)
bot_client = TelegramClient('bot_session', api_id, api_hash)

def clean_telegram_link(link_input):
    link_input = link_input.strip()
    if "/" in link_input:
        return link_input.split("/")[-1].replace("@", "")
    return link_input.replace("@", "")

is_running = False

@bot_client.on(events.NewMessage(pattern='/start'))
async def start_cmd(event):
    await event.reply(
        "👋 **Bot Active Aur Ready Hai!**\n\n"
        "Members scrape karke add karne ke liye ye command bhejein:\n"
        "`/scrape [Source_Link] [Dest_Link1,Dest_Link2]`"
    )

@bot_client.on(events.NewMessage(pattern='/scrape'))
async def scrape_cmd(event):
    global is_running
    if is_running:
        return

    try:
        parts = event.text.split(" ", 2)
        if len(parts) < 3:
            return

        source_username = clean_telegram_link(parts[1])
        dest_usernames = [clean_telegram_link(d) for d in parts[2].split(",")]

        is_running = True
        start_time = time.time()

        source_entity = await user_client.get_entity(source_username)
        members = await user_client.get_participants(source_entity)
        
        dest_index = 0

        for member in members:
            if time.time() - start_time > 86400:
                break

            if not is_running:
                break

            if member.bot or member.username is None:
                continue

            current_dest_username = dest_usernames[dest_index]
            try:
                dest_entity = await user_client.get_entity(current_dest_username)
                await user_client(functions.channels.InviteToChannelRequest(
                    channel=dest_entity,
                    users=[member]
                ))
                dest_index = (dest_index + 1) % len(dest_usernames)
                await asyncio.sleep(30) # Safe background delay
            except Exception:
                await asyncio.sleep(10)

        is_running = False

    except Exception:
        is_running = False

async def start_all():
    await user_client.start()
    await bot_client.start(bot_token=BOT_TOKEN)
    print("Bot aur User Client dono chal rahe hain...")
    await bot_client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(start_all())
    except Exception as e:
        print(f"Server Stopped: {e}")
