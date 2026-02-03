import asyncio
import os
import random
import string
from aiogram import Bot, Dispatcher, types
from yt_dlp import YoutubeDL
from aiohttp import web

# --- SOZLAMALAR ---
API_TOKEN = '7780544610:AAGfmsEw5SELtoblUPKsG74ombSxoSW2o88'
CH_ID = "@weakvertual" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Render uxlab qolmasligi uchun kichik server
async def handle(request):
    return web.Response(text="Bot is online and rocking!")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render avtomatik beradigan PORT dan foydalanamiz
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"✅ Web server {port}-portda ishga tushdi")

def get_ydl_opts(filename):
    return {
        'format': 'bestaudio/best',
        'outtmpl': f"{filename}.%(ext)s",
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch20',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

async def auto_post():
    print("📢 Takrorlanmas avto-post tizimi ishga tushdi...")
    while True:
        try:
            queries = [
                "Konsta yangi", "Massa rep", "Shaka uzbek rap", "Milano rep",
                "Miyagi & Эндшпиль", "Macan hits", "Central Cee", 
                "Uzbek underground", "Timur Alixonov", "Sahar guruhi", 
                "Tohir Sodiqov retro", "Diyor Mahkamov", "Massa 2026",
                "Konsta ma'noli", "Uzbek hip hop new", "Miyagi 2026",
                "Uzbek indie", "Uzbek lo-fi"
            ]
            
            base_q = random.choice(queries)
            q = f"{base_q} {random.choice(string.ascii_lowercase)}"
            unique_id = "".join(random.choices(string.digits, k=5))
            fname = f"song_{unique_id}"
            
            with YoutubeDL(get_ydl_opts(fname)) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, q, download=False)
                
                if 'entries' in info and len(info['entries']) > 0:
                    selected_entry = random.choice(info['entries'])
                    title = selected_entry.get('title', '').lower()
                    
                    # Sifat nazorati
                    blacklist = ["rasul", "hamdam", "toyona", "yalla", "lazzgi", "jonli"]
                    if any(word in title for word in blacklist):
                        continue

                    await asyncio.to_thread(ydl.download, [selected_entry['webpage_url']])
                    
                    fpath = f"{fname}.mp3"
                    if os.path.exists(fpath):
                        caption = f"💎 **{selected_entry.get('title')}**\n\n🎧 @weakvertual - Sifatli tanlov"
                        await bot.send_audio(CH_ID, types.FSInputFile(fpath), caption=caption)
                        os.remove(fpath)
            
            # Har 25 daqiqada bitta yangi musiqa
            await asyncio.sleep(1500)
            
        except Exception as e:
            print(f"⚠️ Xato: {e}")
            await asyncio.sleep(60)

async def main():
    # Bir vaqtning o'zida ham serverni, ham botni ishga tushiramiz
    asyncio.create_task(start_webserver())
    asyncio.create_task(auto_post())
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
