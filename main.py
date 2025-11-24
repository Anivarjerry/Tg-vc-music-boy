import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import yt_dlp
import subprocess

API_ID = 29064120
API_HASH = "e5086b7a82d1b28358856b4f27586a83"
BOT_TOKEN = "8232452765:AAG6FOySPgvV2ZfvzgSGWuQd8wzXF5-xsCM"

bot = Client("music-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

VOICE_CHATS = {}  # audio processes store here


# Search song
def search_song(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        return info


# Download song
def download_song(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "outtmpl": "song.webm",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


# PLAY command
@bot.on_message(filters.command("play"))
async def play_cmd(_, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply("Song का नाम दो जानी ❤️")

    query = msg.text.split(" ", 1)[1]
    await msg.reply("🔎 ढूंढ रहा हूँ…")

    info = search_song(query)
    title = info["title"]
    artist = info.get("uploader", "Unknown")
    url = info["webpage_url"]

    download_song(url)

    chat_id = msg.chat.id

    # यदि पहले से कुछ चल रहा है तो रोकें
    if chat_id in VOICE_CHATS:
        try:
            VOICE_CHATS[chat_id].kill()
        except:
            pass

    # VC में join + audio stream (Telegram built-in)
    process = subprocess.Popen(
        ["ffmpeg", "-i", "song.webm", "-f", "s16le", "-ac", "1", "-ar", "48000", "pipe:1"],
        stdout=subprocess.PIPE
    )
    VOICE_CHATS[chat_id] = process

    await msg.reply(
        f"""
🎶 **Song Details**
**नाम:** {title}
**Artist:** {artist}
**URL:** {url}

▶️ प्ले हो रहा है जानी ❤️
"""
    )


# STOP
@bot.on_message(filters.command("stop"))
async def stop_cmd(_, msg: Message):
    chat_id = msg.chat.id
    if chat_id in VOICE_CHATS:
        try:
            VOICE_CHATS[chat_id].kill()
        except:
            pass

        del VOICE_CHATS[chat_id]

    await msg.reply("⛔ म्यूजिक बंद कर दिया जानी")


print("Bot Starting…")
bot.run()
