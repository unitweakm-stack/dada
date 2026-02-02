import asyncio
import os
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from yt_dlp import YoutubeDL
from aiohttp import web

# --- SOZLAMALAR ---
API_TOKEN = '8350721461:AAGsYIvy6SdyrwQEXqGCHEFpkx0Kk3KYBZU'
CH_ID = "@weakmwx" 
CH_LINK = "https://t.me/weakmwx"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- AVTO-POSTING (FAQAT MUSIQA - HAR 5 MINUTDA) ---
async def auto_post_system():
    while True:
        try:
            # Ruscha va O'zbekcha trendlarni almashtirib turadi
            queries = ["russian hits 2026", "uzbek rep 2026", "xit qo'shiqlar 2026"]
            query = random.choice(queries)
            
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/best',
                'quiet': True,
                'no_warnings': True,
                'default_search': f"ytsearch1:{query}", 
                'outtmpl': 'auto_music.m4a',
                'noplaylist': True,
                # JavaScript xatosini chetlab o'tish uchun qo'shimcha:
                'extractor_args': {'youtube': {'skip': ['dash', 'hls']}},
                'check_formats': False,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=True)
                if 'entries' in info:
                    entry = info['entries'][0]
                    title = entry.get('title', 'Yangi Xit!')
                    
                    await bot.send_audio(
                        chat_id=CH_ID, 
                        audio=types.FSInputFile('auto_music.m4a'), 
                        caption=f"🎵 **Yangi Trek!**\n\n📌 {title}\n\n🚀 @weakmwx - Eng yangi musiqalar!"
                    )
            
            if os.path.exists('auto_music.m4a'): 
                os.remove('auto_music.m4a')
            
            # Har 5 daqiqada (300 soniya)
            await asyncio.sleep(300) 

        except Exception as e:
            print(f"Auto-post xatosi: {e}")
            await asyncio.sleep(60)

# --- RENDER VEB-SERVER ---
async def handle(request): return web.Response(text="Bot Active!")
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 8080).start()

# --- QIDIRUV VA YUKLASH (FOYDALANUVCHILAR UCHUN) ---
def download_media(url, is_video=False):
    file_path = f"file_{random.randint(1,1000)}.{'mp4' if is_video else 'm4a'}"
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best' if is_video else 'bestaudio[ext=m4a]/best',
        'outtmpl': file_path, 
        'quiet': True,
        'extractor_args': {'youtube': {'skip': ['dash', 'hls']}},
    }
    with YoutubeDL(ydl_opts) as ydl: 
        ydl.download([url])
    return file_path

def search_media(query):
    ydl_opts = {
        'format': 'bestaudio', 
        'quiet': True, 
        'default_search': 'ytsearch10', 
        'noplaylist': True,
        'extractor_args': {'youtube': {'skip': ['dash', 'hls']}},
    }
    with YoutubeDL(ydl_opts) as ydl: 
        return ydl.extract_info(query, download=False).get('entries', [])

# --- HANDLERLAR ---
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("🚀 **WEAK M** bot faol!\nMusiqa nomini yozing yoki Insta/TikTok link yuboring.")

@dp.message(F.text)
async def handle_message(message: types.Message):
    if any(s in message.text for s in ["instagram.com", "tiktok.com"]):
        status = await message.answer("🎬 Yuklanmoqda...")
        try:
            file = await asyncio.to_thread(download_media, message.text, True)
            await message.answer_video(types.FSInputFile(file), caption="🚀 @weakmwx")
            if os.path.exists(file): os.remove(file)
            await status.delete()
        except: await status.edit_text("❌ Xato! Video yuklanmadi.")
        return

    status = await message.answer("🔎 Qidirilmoqda...")
    try:
        results = await asyncio.to_thread(search_media, message.text)
        btns = []
        for i in results[:10]:
            btns.append([InlineKeyboardButton(text=f"• {i.get('duration_string', '0:00')} • {i.get('title', '')[:30]}", 
                                             callback_data=f"dl_{i.get('id')}")])
        await status.delete()
        await message.answer("🎶 Natijalar:", reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))
    except: await status.edit_text("❌ Hech narsa topilmadi.")

@dp.callback_query(F.data.startswith("dl_"))
async def dl_cb(call: CallbackQuery):
    v_id = call.data.split("_")[1]
    await call.answer("Yuklanmoqda... ⏳")
    try:
        file = await asyncio.to_thread(download_media, f"https://www.youtube.com/watch?v={v_id}", False)
        await call.message.answer_audio(types.FSInputFile(file), caption="🚀 @weakmwx")
        if os.path.exists(file): os.remove(file)
    except: await call.message.answer("❌ Yuklashda xatolik!")

async def main():
    asyncio.create_task(auto_post_system())
    asyncio.create_task(start_web_server())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

