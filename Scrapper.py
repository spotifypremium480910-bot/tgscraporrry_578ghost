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

# Aapka Bot Token aur Session Key yahan brackets ke andar automatic work karega
BOT_TOKEN = '8728242418:AAFgUFtn7wfOpB38rKP5jB64kOokeC8N04c' 
STRING_SESSION = '1BVtsOHMBu2wBsIP5CrAmCfPT8EfiF2GuS7hx-pIiysO2qCP-fLYgHgQTRkCT6SC0nC5T_q_jaNY1UFd5mpRKwWWAw3ZR2Nqe9GZLFBcoFp_jh5Pc4cOdZhO96aiMzZLFiyFnkB99rrBpxfoxPZARfRcjZCmy4fOHtyn1ly-57D4TRihk4ZcNEmHemdw5FNj6wFuSfZxesVItC3QYdIcnXAvhRFCzicsClCb6M0lPH6p2FCmFIvfRtoP2SVCvv6YMOIC9aVcNcELsECotb2vyURpckWW3jcM4pjLShjSHbbhMz-mLp6sM4whkZKedsf34ii67S-iJPARFTFcWsPVaTZ2F583LLQ4'
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
        "👋 **Welcome to Telegram Scraper Bot!**\n\n"
        "Members ko add karne ke liye ye command bhejein:\n"
        "`/scrape [Source_Link] [Dest_Link1,Dest_Link2]`"
    )

@bot_client.on(events.NewMessage(pattern='/scrape'))
async def scrape_cmd(event):
    global is_running
    if is_running:
        await event.reply("⚠️ **Ek task pehle se chal raha hai!**")
        return

    try:
        parts = event.text.split(" ", 2)
        if len(parts) < 3:
            await event.reply("❌ **Format:** `/scrape [Source] [Dest1,Dest2]`")
            return

        source_link = parts[1]
        dest_links = [link.strip() for link in parts[2].split(",")]

        source_username = clean_telegram_link(source_link)
        dest_usernames = [clean_telegram_link(d) for d in dest_links]

        await event.reply("⏳ **Process shuru ho raha hai...** Members list fetch ho rahi hai.")
        is_running = True
        start_time = time.time()

        source_entity = await user_client.get_entity(source_username)
        members = await user_client.get_participants(source_entity)
        
        await event.reply(f"📊 **Total {len(members)} members mile.** Adding process start ho raha hai...")

        dest_index = 0

        for member in members:
            if time.time() - start_time > 86400:
                await event.reply("⏱️ **24 Ghante poore ho gaye hain!** Script automatically stop ho gayi.")
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
                print(f"Added @{member.username} to {current_dest_username}")
                dest_index = (dest_index + 1) % len(dest_usernames)
                await asyncio.sleep(45) 
            except Exception as e:
                print(f"Error @{member.username}: {e}")
                await asyncio.sleep(5)

        is_running = False
        await event.reply("✅ **Task khatam.**")

    except Exception as e:
        is_running = False
        await event.reply(f"❌ **Error:** {e}")

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
