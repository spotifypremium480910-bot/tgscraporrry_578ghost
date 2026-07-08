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

# Aapka naya fresh string session yahan set hai
STRING_SESSION = 'BQG9HsQAFlgCncNX1UkjMOc1eiAZ1ejs9YNu4UweqRjJ_Q7igQuwYh1cNOM-OaMEmFMYp9ft_G_cXe3hI29nhQujaqIdpzl17MQym0SL92bh6WfyPZsjFe5JiA3oLVU6HBvs4uOT-cyWvJsEh61Rr2FnKvDFeT5yx_PMzBPgdDXjQlSKIxKkCzhiLWK4cDM1szN3ltPFA6T8pOsmJGyxPCjlEMP1B3RrMRIr2r_MysAXS87oHxwxW9IfGEAg-lGj0ba3Umqe249dkmxs4nhi7pvQcWSI8Xphx6hRqddgPudWT3RRPSne96Yhvm5DYPS9KOlHBoZ12Ri1Ddekj3sBD0xMynUWRgAAAABQZ36KAA'
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
    await event.reply("👋 **Bot Active Aur Ready Hai!**\n\nCommand bhejein:\n`/scrape [Source] [Dest]`")

@bot_client.on(events.NewMessage(pattern='/scrape'))
async def scrape_cmd(event):
    global is_running
    if is_running:
        await event.reply("⚠️ Ek task pehle se chal raha hai!")
        return

    try:
        parts = event.text.split(" ", 2)
        if len(parts) < 3:
            return

        source_username = clean_telegram_link(parts[1])
        dest_usernames = [clean_telegram_link(d) for d in parts[2].split(",")]

        is_running = True
        start_time = time.time()

        print("Fetching members from source...")
        source_entity = await user_client.get_entity(source_username)
        members = await user_client.get_participants(source_entity)
        await event.reply(f"📊 Total {len(members)} members mile. 40s safe speed par adding start ho gayi hai...")

        dest_index = 0

        for member in members:
            if time.time() - start_time > 86400:
                print("24 Hours complete. Stopping.")
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
                print(f"📦 [SUCCESS] Added @{member.username} to {current_dest_username}")
                dest_index = (dest_index + 1) % len(dest_usernames)
                await asyncio.sleep(40) # Exactly 40 seconds background delay
            except Exception as e:
                print(f"❌ [FAILED] @{member.username}: {e}")
                await asyncio.sleep(10)

        is_running = False

    except Exception as e:
        print(f"Error: {e}")
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
        
