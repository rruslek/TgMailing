from pyrogram import Client, idle

from handlers import register_handlers
from documentation import register_doc_handlers
from config import api_id, api_hash
import asyncio


async def main():
    userbot = Client('me_client', api_id=api_id, api_hash=api_hash)
    register_handlers(userbot)
    register_doc_handlers(userbot)

    await userbot.start()
    await idle()
    await userbot.stop()


if __name__ == '__main__':
    asyncio.run(main())
