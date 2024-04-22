from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ContentType, InputMediaVideo, FSInputFile
from aiogram.filters import Command
import asyncio
import requests
import base64

tok = '6730580975:AAFDsqIx48p1ZHLVWI3PZkS2Gmvzc-00AA8'
video_file_path = 'meow.mp4' 
server_url = 'http://127.0.0.1:8000/'

async def get_message(message: types.Message, bot: Bot):
    if message.content_type == types.ContentType.VIDEO:
        await handle_video(message, bot)
    else:
        await get_other(message)

async def send_video_to_server(video_file_path, server_url, message: types.Message,  bot:Bot):
    try:
        response = requests.post(server_url, files={'video': open(video_file_path, 'rb')})
            
        if response.status_code == 200:
            json_response = response.json()
            video_data = json_response.get("video")
            image_data = json_response.get("image")

            video_binary_data = base64.b64decode(video_data)
            image_binary_data = base64.b64decode(image_data)

            with open("clientvideo.mp4", "wb") as video_file:
                video_file.write(video_binary_data)

            with open("clientimage.jpg", "wb") as image_file:
                image_file.write(image_binary_data)
            
            await message.reply_video(video=types.FSInputFile(path="clientvideo.mp4"))
            await message.reply_photo(photo=types.FSInputFile(path="clientimage.jpg"))
        else:
            print(f"Произошла ошибка: {response.status_code}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

async def get_other(message: types.Message):
    await message.reply("Пожалуйста, отправьте только видео.")

async def handle_video(message: types.Message, bot:Bot):
    video = message.video
    file_id = video.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{tok}/{file_path}"
    try:
        with requests.get(file_url) as response:
            if response.status_code == 200:
                with open('meow.mp4', 'wb') as f:
                    f.write(response.content)
                await send_video_to_server(video_file_path, server_url, message,  bot)
            else:
                await message.reply("Произошла ошибка при скачивании видео.")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}")
    
    

async def start():
    bot = Bot(token=tok)
    dp=Dispatcher()

    dp.message.register(get_message)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())

