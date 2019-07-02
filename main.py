from aiogram import Bot, types
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

PROXY_AUTH = aiohttp.BasicAuth(login='telegram', password='telegram')
bot = Bot(config.token, proxy=config.PROXY_URL, loop=loop, proxy_auth=PROXY_AUTH)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=["start"])
async def process_start_command(msg):
    try:
        await dp.throttle('start', rate=1)
    except Throttled:
        pass
    else:
        await bot.send_message(msg.from_user.id, config.start.format(msg.from_user.first_name), disable_notification=True)

@dp.message_handler(lambda msg: msg.reply_to_message and msg.from_user.id in config.admins_id)
async def process_reply(msg):
    await bot.send_message(msg.reply_to_message.forward_from.id, msg.text)

@dp.message_handler()
async def process_send(msg):
    try:
        await dp.throttle('start', rate=1)
    except Throttled:
        pass
    else:
        for id in config.admins_id:
            await bot.forward_message(id, msg.from_user.id, msg.message_id)
        await bot.send_message(msg.from_user.id, config.repl, reply_to_message_id=msg.message_id, disable_notification=True)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, loop=loop)
