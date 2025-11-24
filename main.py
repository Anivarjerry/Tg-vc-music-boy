import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
import yt_dlp

API_ID = int(os.environ["29064120"])
API_HASH = os.environ["e5086b7a82d1b28358856b4f27586a83"]
BOT_TOKEN = os.environ["8232452765:AAG6FOySPgvV2ZfvzgSGWuQd8wzXF5-xsCM"]
SESSION = os.environ["SESSION"]

bot = Client("music-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)

call = PyTgCalls(user)


def search_song(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        return info


def download_song(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "outtmpl": "song.mp3",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


@bot.on_message(filters.command("play"))
async def play(_, msg):
    if len(msg.command) < 2:
        return await msg.reply("Song का नाम दो जानी ❤️")

    query = msg.text.split(" ", 1)[1]

    await msg.reply("🔎 खोज रहा हूँ…")

    info = search_song(query)
    title = info['title']
    artist = info.get('uploader', 'Unknown')
    duration = info.get('duration', 'Unknown')
    url = info['webpage_url']

    # डाउनलोड
    download_song(url)

    # VC play
    chat_id = msg.chat.id
    await call.join_group_call(chat_id, AudioPiped("song.mp3"))

    text = f"""
🎶 **Song Details**  
**नाम:** {title}  
**Artist:** {artist}  
**Duration:** {duration} Sec  
**URL:** {url}
    """

    await msg.reply(text)


@bot.on_message(filters.command("stop"))
async def stop(_, msg):
    await call.leave_group_call(msg.chat.id)
    await msg.reply("⛔ Music Stopped")


async def main():
    await bot.start()
    await user.start()
    await call.start()
    print("Bot Started!")
    await idle()


asyncio.run(main())
