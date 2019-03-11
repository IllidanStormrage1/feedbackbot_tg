from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.exceptions import Throttled
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import aiosocksy
import config
import aiohttp


storage = MemoryStorage()
loop = asyncio.get_event_loop()

# PROXY_AUTH = aiohttp.BasicAuth(login='telegram', password='telegram')
bot = Bot(config.token, proxy=config.PROXY_URL, loop=loop)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=["start"])
async def process_start_command(msg):
    try:
        await dp.throttle('start', rate=2)
    except Throttled:
        pass
    else:
        if msg.from_user.id in config.admins_id:
            message = config.start_admin.format(msg.from_user.first_name)
        else:
            message = config.start.format(msg.from_user.first_name)
        await bot.send_message(msg.from_user.id, message, disable_notification=True, parse_mode="Markdown")

@dp.message_handler(lambda msg: msg.reply_to_message and msg.from_user.id in config.admins_id)
async def process_reply(msg):
    try:
        await bot.send_message(msg.reply_to_message.forward_from.id, msg.text)
    except:
        await bot.send_message(msg.from_user.id, config.error_id)


@dp.message_handler(lambda msg: msg.from_user.id not in config.admins_id)
async def process_send(msg):
    try:
        await dp.throttle("start", rate=2)
    except Throttled:
        pass
    else:
        for id in config.admins_id:
           await bot.forward_message(id, msg.from_user.id, msg.message_id)
        await bot.send_message(msg.from_user.id, config.repl, reply_to_message_id=msg.message_id, disable_notification=True)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, loop=loop)
