from telethon import TelegramClient, events
from telethon.tl import functions
import asyncio
import os
import re
import time

# --- CONFIGURATION ---
api_id = 39201837
api_hash = 'ca4ca441f67605320f3e71f2539a3eec'
# Apna Bot Token yahan daalein (BotFather se banakar)
BOT_TOKEN = '8728242418:AAFgUFtn7wfOpB38rKP5jB64kOokeC8N04c' 
# ---------------------

# Do alag clients: Ek aapka account adding ke liye, ek bot commands ke liye
user_client = TelegramClient('user_session', api_id, api_hash)
bot_client = TelegramClient('bot_session', api_id, api_hash)

def clean_telegram_link(link_input):
    link_input = link_input.strip()
    if "/" in link_input:
        return link_input.split("/")[-1].replace("@", "")
    return link_input.replace("@", "")

# Global control variable
is_running = False

@bot_client.on(events.NewMessage(pattern='/start'))
async def start_cmd(event):
    await event.reply(
        "👋 Welcome! Members scrape karne ke liye ye command bhejein:\n\n"
        "`/scrape [Source_Link] [Dest_Link1,Dest_Link2]`\n\n"
        "Example:\n`/scrape https://t.me/source https://t.me/dest1,https://t.me/dest2`"
    )

@bot_client.on(events.NewMessage(pattern='/scrape'))
async def scrape_cmd(event):
    global is_running
    if is_running:
        await event.reply("⚠️ Ek task pehle se chal raha hai! Pehle use poora hone dein.")
        return

    try:
        # Command arguments check karna
        parts = event.text.split(" ", 2)
        if len(parts) < 3:
            await event.reply("❌ Sahi format use karein: `/scrape [Source] [Dest1,Dest2]`")
            return

        source_link = parts[1]
        dest_links = [link.strip() for link in parts[2].split(",")]

        source_username = clean_telegram_link(source_link)
        dest_usernames = [clean_telegram_link(d) for d in dest_links]

        await event.reply("⏳ Process shuru ho raha hai... Members fetch kiye ja rahe hain.")
        is_running = True
        start_time = time.time() # 24 hours tracker

        # Fetch entities using user account
        source_entity = await user_client.get_entity(source_username)
        members = await user_client.get_participants(source_entity)
        
        await event.reply(f"📊 Total {len(members)} members mile. Adding process shuru ho raha hai...")

        dest_index = 0  # Multiple channels mein rotate karne ke liye

        for member in members:
            # 24 Hours Time Check (86400 seconds = 24 hours)
            if time.time() - start_time > 86400:
                await event.reply("⏱️ 24 Ghante poore ho gaye hain! Script automatically stop ho gayi hai.")
                break

            if not is_running:
                break

            if member.bot or member.username is None:
                continue

            # Baari-baari sabhi destination channels par add karega
            current_dest_username = dest_usernames[dest_index]
            try:
                dest_entity = await user_client.get_entity(current_dest_username)
                await user_client(functions.channels.InviteToChannelRequest(
                    channel=dest_entity,
                    users=[member]
                ))
                print(f"Added {member.username} to {current_dest_username}")
                
                # Agle channel par switch karein (agar multiple hain)
                dest_index = (dest_index + 1) % len(dest_usernames)
                
                await asyncio.sleep(45) # Too many requests se bachne ke liye safe delay
            except Exception as e:
                print(f"Error adding {member.username}: {e}")
                await asyncio.sleep(5)

        is_running = False
        await event.reply("✅ Task khatam ya stop ho gaya hai.")

    except Exception as e:
        is_running = False
        await event.reply(f"❌ Koi error aaya: {e}")

async def main():
    # Dono clients ko start karna
    await user_client.start()
    await bot_client.start(bot_token=BOT_TOKEN)
    print("Bot aur User Client dono chal rahe hain...")
    await bot_client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
