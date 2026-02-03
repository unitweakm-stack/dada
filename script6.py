import asyncio
import os
import random
import string
from aiogram import Bot, Dispatcher, types, F
from yt_dlp import YoutubeDL
from aiohttp import web

# --- SOZLAMALAR ---
API_TOKEN = '7780544610:AAGfmsEw5SELtoblUPKsG74ombSxoSW2o88'
CH_ID = "@weakvertual" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Render uxlab qolmasligi uchun server
async def handle(request):
    return web.Response(text="Bot is running fast on Render!")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

def get_ydl_opts(filename):
    return {
        'format': 'bestaudio/best',
        'outtmpl': f"{filename}.%(ext)s",
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch5',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
    }

# --- 1. MUSIQA QIDIRUV (Bot ichida) ---
@dp.message(F.text)
async def user_search(message: types.Message):
    if message.chat.type != 'private': return
    msg = await message.answer("🔍 Qidirilmoqda...")
    uid = "".join(random.choices(string.digits, k=4))
    fname = f"u_{uid}"
    try:
        with YoutubeDL(get_ydl_opts(fname)) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, message.text, download=True)
            fpath = f"{fname}.mp3"
            if os.path.exists(fpath):
                await message.answer_audio(types.FSInputFile(fpath), caption=f"🎵 {info['entries'][0]['title']}\n🚀 @weakvertual")
                os.remove(fpath)
                await msg.delete()
    except:
        await msg.edit_text("❌ Topilmadi.")

# --- 2. TEZKOR AVTO-POST (2 MINUT) ---
async def auto_post():
    while True:
        try:
            queries = ["Konsta", "Massa rep", "Shaka uzbek rap", "Miyagi hits", "Uzbek underground"]
            q = f"{random.choice(queries)} {random.choice(string.ascii_lowercase)}"
            uid = "".join(random.choices(string.digits, k=4))
            fname = f"a_{uid}"
            
            with YoutubeDL(get_ydl_opts(fname)) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, q, download=True)
                if 'entries' in info and len(info['entries']) > 0:
                    selected = random.choice(info['entries'])
                    if not any(x in selected['title'].lower() for x in ["rasul", "hamdam", "toyona"]):
                        fpath = f"{fname}.mp3"
                        if os.path.exists(fpath):
                            await bot.send_audio(CH_ID, types.FSInputFile(fpath), caption=f"💎 **{selected['title']}**\n🔥 @weakvertual")
                            os.remove(fpath)
            await asyncio.sleep(120) # 2 minut
        except:
            await asyncio.sleep(30)

async def main():
    asyncio.create_task(start_webserver())
    asyncio.create_task(auto_post())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
