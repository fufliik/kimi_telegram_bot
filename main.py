
import asyncio
from dotenv import load_dotenv

from main_video import *
from main_audio import *
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

load_dotenv()
dp = Dispatcher()

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "👋 Привет!\n\n"
        "Я бот для скачивания видео 🎬 и аудио 🎵 по ссылке.\n\n"
        "🧪 Сейчас я нахожусь в бета-тесте.\n"
        "На данный момент я протестирован на ссылках с:\n\n"
        "YouTube\n"
        "YouTube Music\n"
        "Facebook\n"
        "Reddit\n\n"
        "⚠️ Некоторые ссылки или форматы могут пока работать не идеально.\n\n"
        "🔗 Отправь ссылку — я попробую скачать файл!"
    )


#==================================================================================================
user_urls = {}
@dp.message()
async def message_handler(message: Message) -> None:
    text = message.text or "" # если буду делать обработку через шазам нужно будет убрать
    if text.startswith(("http://", "https://")):
        user_urls[message.from_user.id] = text
        await message.answer("🟢 что вы хотите получить?", reply_markup=media_keyboard)
    else:
        await message.answer("🟡 Бот принимает только ссылки")
#--------------------------------------------------------------------------------------------------
media_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🎬 Видео", callback_data="video_")],
        [InlineKeyboardButton(text="🎵 Аудио ", callback_data="audio_")],
        #[InlineKeyboardButton(text="🎤 Shazam ❌", callback_data="shazam_")],
    ]
)
#--------------------------------------------------------------------------------------------------
#отрисовка конпок качество видео
def quality_keyboard(formats):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{height}p",
                callback_data=f"quality:{height}"
            )]
            for height in formats
        ]
    )
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------

@dp.callback_query(F.data == "video_")
async def video(callback: CallbackQuery):
    url = user_urls.get(callback.from_user.id)
    if not url:
        await callback.message.edit_text("❌ Ссылка не найдена")
        return

    quality = await asyncio.to_thread(video_get_qualities, url)

    if quality is None:
        await callback.message.edit_text("❗ Не удалось найти информацию о файле")
        return

    await callback.message.edit_text("⚙️ Какое качество хотите получить?", reply_markup=quality_keyboard(quality))

#--------------------------------------------------------------------------------------------------
@dp.callback_query(F.data.startswith("quality"))
async def quality_video(callback: CallbackQuery) -> None:
    url = user_urls.get(callback.from_user.id)
    file = None
    quality = callback.data.split(":", 1)[1]

    try:
        if not url:
            await callback.message.edit_text("❌ Ссылка не найдена")
            return

        await callback.message.edit_text("⬇️ Загрузка...")
        video_result = await asyncio.to_thread(video_cheker, url, quality)

        if not video_result:
            await callback.message.edit_text("❌ Не удалось загрузить файл...")
            return

        file, title = video_result

        await callback.message.answer_video(FSInputFile(file, filename=f"{title}.mp4"))
        await callback.message.delete()

    except Exception:
        await callback.message.edit_text("❌ Возникла ошибка!..")

    finally:
        if file and os.path.exists(file):
            os.remove(file)


#==================================================================================================
@dp.callback_query(F.data == "audio_")
async def audio(callback: CallbackQuery) -> None:
    url = user_urls.get(callback.from_user.id)
    file = None
    try:
        if not url:
            await callback.message.edit_text("❌ Ссылка не найдена")
            return

        await callback.message.edit_text("⬇️ Загрузка...")
        audio_result =await asyncio.to_thread(audio_cheker, url)

        if not audio_result:
            await callback.message.edit_text("❌ Не удалось загрузить файл...")
            return

        file, title = audio_result

        await callback.message.answer_audio(FSInputFile(file, filename=f"{title}.mp3"))
        await callback.message.delete()

    except Exception:
        await callback.message.edit_text("❌ Возникла ошибка!..")

    finally:
        if file and os.path.exists(file):
            os.remove(file)


async def main() -> None:
    TOKEN = os.getenv("TOKEN")
    ip = os.getenv("SERVER_IP")
    session = AiohttpSession(
        timeout=240,
        api=TelegramAPIServer.from_base(ip, is_local=True))
    bot = Bot(token=TOKEN, session=session)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
