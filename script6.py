import asyncio
import os
import random
from aiogram import Bot, Dispatcher, types, F
from yt_dlp import YoutubeDL

# --- SOZLAMALAR ---
API_TOKEN = '7780544610:AAGfmsEw5SELtoblUPKsG74ombSxoSW2o88'
CH_ID = "@weakvertual" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def get_ydl_opts(filename):
    return {
        'format': 'bestaudio/best',
        'outtmpl': f"{filename}.%(ext)s",
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'default_search': 'ytsearch1',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

async def auto_post():
    while True:
        try:
            queries = [
                "Konsta yangi qo'shig'i", "Massa rep", "Shaka uzbek rap",
                "Timur Alixonov", "Tohir Sodiqov", "Sahar guruhi",
                "Diyor Mahkamov yangi", "Uzbek Lo-fi 2026"
            ]
            q = random.choice(queries)
            fname = f"best_{random.randint(100,999)}"
            
            with YoutubeDL(get_ydl_opts(fname)) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, q, download=True)
                if 'entries' in info:
                    res = info['entries'][0]
                    title = res.get('title', '').lower()
                    
                    blacklist = ["rasul", "hamdam", "toyona", "yalla", "lazzgi"]
                    if any(word in title for word in blacklist):
                        continue

                    fpath = None
                    for f in os.listdir('.'):
                        if f.startswith(fname) and f.endswith('.mp3'):
                            fpath = f; break
                    
                    if fpath:
                        caption = f"💎 **{res.get('title')}**\n\n🚀 {CH_ID}"
                        await bot.send_audio(CH_ID, types.FSInputFile(fpath), caption=caption)
                        os.remove(fpath)
            
            await asyncio.sleep(1200) # 20 daqiqada bir
        except:
            await asyncio.sleep(60)

async def main():
    asyncio.create_task(auto_post())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
