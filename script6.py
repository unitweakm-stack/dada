import asyncio
import os
import qrcode
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web  # Render uchun veb-server

# --- SOZLAMALAR ---
API_TOKEN = '8350721461:AAGsYIvy6SdyrwQEXqGCHEFpkx0Kk3KYBZU'
ARTIST_NAME = "WEAK M🦂"
CH_ID = "@weakmwx"
CH_LINK = "https://t.me/weakmwx"
DB_FILE = "users.txt"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
executor = ThreadPoolExecutor(max_workers=30)

# --- RENDER UCHUN VEB-SERVER (24/7 ISHLASHI UCHUN) ---
async def handle(request):
    return web.Response(text="Bot is running 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080) # Render 8080 portni kutadi
    await site.start()

# --- YORDAMCHI FUNKSIYALAR ---
def save_user(user_id):
    if not os.path.exists(DB_FILE): open(DB_FILE, "w").close()
    with open(DB_FILE, "r") as f: users = f.read().splitlines()
    if str(user_id) not in users:
        with open(DB_FILE, "a") as f: f.write(f"{user_id}\n")

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CH_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except: return False

def sub_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Kanalga obuna bo'lish ➕", url=CH_LINK)],
        [InlineKeyboardButton(text="Tekshirish ✅", callback_data="check_sub")]
    ])

def download_media(query, user_id):
    is_link = query.startswith("http")
    file_path = f"file_{user_id}.{'mp4' if is_link else 'm4a'}"
    
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/best' if not is_link else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'outtmpl': file_path,
        'quiet': True, 
        'no_warnings': True,
        'default_search': 'ytsearch1' if not is_link else None,
        # YOUTUBE BLOKIROVKASINI CHETLAB O'TISH UCHUN:
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        title = info.get('title', 'Media') if is_link else info['entries'][0]['title']
        return file_path, title, is_link

# --- HANDLERLAR ---
@dp.message(CommandStart())
async def start(message: types.Message):
    save_user(message.from_user.id)
    if await is_subscribed(message.from_user.id):
        await message.answer(f"🚀 **{ARTIST_NAME}** botiga xush kelibsiz!\nNom yozing yoki link yuboring.")
    else:
        await message.answer(f"❌ Botdan foydalanish uchun {CH_ID} kanaliga a'zo bo'ling!", reply_markup=sub_keyboard())

@dp.callback_query(F.data == "check_sub")
async def check_sub_btn(call: types.CallbackQuery):
    if await is_subscribed(call.from_user.id):
        await call.message.delete()
        await call.message.answer("Rahmat! Endi botdan foydalanishingiz mumkin. ✅")
    else:
        await call.answer("Siz hali obuna bo'lmagansiz! ❌", show_alert=True)

@dp.message(Command("qr"))
async def qr_gen(message: types.Message):
    text = message.text.replace("/qr", "").strip()
    if not text: return await message.answer("QR uchun matn yozing!")
    path = f"qr_{message.from_user.id}.png"
    qrcode.make(text).save(path)
    await message.answer_photo(types.FSInputFile(path))
    os.remove(path)

@dp.message(F.text)
async def handle_all(message: types.Message):
    if message.text.startswith("/"): return
    if not await is_subscribed(message.from_user.id):
        return await message.answer(f"❌ Avval {CH_ID} kanaliga a'zo bo'ling!", reply_markup=sub_keyboard())

    status = await message.answer("🔍 **WEAK M🦂** qidirmoqda...")
    loop = asyncio.get_event_loop()
    try:
        file_path, title, is_video = await loop.run_in_executor(executor, download_media, message.text, message.from_user.id)
        if is_video:
            await message.answer_video(types.FSInputFile(file_path), caption=f"🎬 {title}\n🎙 {ARTIST_NAME}")
        else:
            await message.answer_audio(types.FSInputFile(file_path), performer=ARTIST_NAME, title=title)
        await status.delete()
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await status.edit_text(f"❌ Xatolik: {str(e)[:50]}...")

async def main():
    # Render uchun veb-serverni fonda ishga tushirish
    asyncio.create_task(start_web_server())
    
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
