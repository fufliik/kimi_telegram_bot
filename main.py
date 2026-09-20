
import asyncio
from dotenv import load_dotenv
from get import *
from load import *
from check import *
from logs import *
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
user_logs = {}


@dp.callback_query(F.data == "video_")
async def video(callback: CallbackQuery):
    url = user_urls.get(callback.from_user.id)
    log = "🎬 Выбрал видео\n\n"
    user_logs[callback.from_user.id] = log

    if not url:
        await callback.message.edit_text("❌ Ссылка не найдена")
        log += f"❌ Ссылка не найдена: {url}\n"
        return

    quality = await asyncio.to_thread(get_qualities_video, url)

    if quality is None:
        await callback.message.edit_text("❗ Не удалось найти информацию о файле")
        return

    log += f"⚙️ Доступные качества: {quality}\n"
    user_logs[callback.from_user.id] = log

    await callback.message.edit_text("⚙️ Какое качество хотите получить?", reply_markup=quality_keyboard(quality))

#--------------------------------------------------------------------------------------------------
@dp.callback_query(F.data.startswith("quality"))
async def quality_video(callback: CallbackQuery) -> None:
    url = user_urls.get(callback.from_user.id)
    file = None
    quality = callback.data.split(":")[1]
    log = user_logs[callback.from_user.id]

    log += f" Выбраное качество:  {quality}\n"
    try:
        await callback.message.edit_text("🔍 Проверка размера...")
        size, allowed_size = await asyncio.to_thread(check_video_size, url, quality)
        log += f"📦 Размера файла: {size:.2f} MB\n"

        if size is None:
            await callback.message.edit_text("❌ Не удалось определить размер видео.")
            return

        if not allowed_size:
            await callback.message.edit_text(
                "⚠️ Видео слишком большое!\n\n"
                f"Размер файла — {size:.2f} MB\nМаксимальный размер — 2000 MB."
            )
            return

        await callback.message.edit_text("⬇️ Загрузка...")
        log += "⬇️ Загрузка...\n\n"
        file, title = await asyncio.to_thread(video_load, url, quality)

        log += ("🖥️ Загружен на сервер: \n\n"
                f"📁 Путь: {file}\n\n"
                f"📄 Название: {title}\n\n")

        await callback.message.answer_video(FSInputFile(file, filename=f"{title}.mp4"))

    except Exception as e:
        await callback.message.edit_text("❌ Возникла ошибка!..")
        log += f"❌ Возникла ошибка!.. {e}\n"
    finally:
        if file and os.path.exists(file):
            os.remove(file)
            log += "🗑️ Временный файл удалён\n"
        else:
            log += "❌ Временный файл не обнаружен\n"

        await send_log(callback, log, url=url)
        user_logs.pop(callback.from_user.id, None)

#==================================================================================================
@dp.callback_query(F.data == "audio_")
async def audio_video(callback: CallbackQuery) -> None:
    url = user_urls.get(callback.from_user.id)
    file = None
    log = "🎵 Выбрал аудио\n"
    try:
        if not url:
            await callback.message.edit_text("❌ Ссылка не найдена")
            log += f"❌ Ссылка не найдена -> {url}\n"
            return

        await callback.message.edit_text("🔍 Проверка размера...")
        size, allowed_size = await asyncio.to_thread(check_audio_size, url)
        log += f"📦 Размера файла: {size:.2f} MB\n"

        if allowed_size is None:
            await callback.message.edit_text("❌ Не удалось определить размер аудио.")
            return

        if not allowed_size:
            await callback.message.edit_text(
                "⚠️ Аудио слишком большое!\n\n"
                f"Размер файла — {size:.2f} MB\nМаксимальный размер — 1500 MB."
            )
            return

        await callback.message.edit_text("⬇️ Загрузка...")
        log += "⬇️ Загрузка...\n\n"
        file, title = await asyncio.to_thread(audio_load, url)

        log += ("🖥️ Загружен на сервер: \n\n"
                f"📁 Путь: {file}\n\n"
                f"📄 Название: {title}\n\n")

        await callback.message.answer_audio(FSInputFile(file, filename=f"{title}.mp3"))
    except Exception as e:
        await callback.message.edit_text("❌ Возникла ошибка!..")

        log += f"❌ Возникла ошибка!.. {e}\n"
    finally:
        if file and os.path.exists(file):
            os.remove(file)
            log += "🗑️ Временный файл удалён\n"
        else:
            log += "❌ Временный файл не обнаружен\n"

        await send_log(callback, log, url=url)






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
