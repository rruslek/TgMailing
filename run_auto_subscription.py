from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types import Message, Chat
from pyrogram.errors import UserBannedInChannel, Forbidden, ChatWriteForbidden, InviteRequestSent
import asyncio
import random
from helpers import get_chats, update_chats, update_mailing_count, get_delta, stop_running
from config import admin_id


async def auto_subscription(userbot: Client, links: set[str]):
    """Авто-подписка.
    1. Получаем список чатов usernames, на которые бот уже подписан
    2. Если юзернейм чата из множества links содержится в usernames,
    то скипаем его"""
    dialogs = userbot.get_dialogs()
    usernames = []
    async for dialog in dialogs:
        chat = dialog.chat
        if chat.type == ChatType.GROUP or chat.type == ChatType.SUPERGROUP:
            usernames.append(chat.username)

    successful_count = 0
    unsuccessful_links = []
    for link in links:
        if link in usernames:
            print(f'Чат {link} уже добавлен!')
            continue
        else:
            try:
                await userbot.join_chat(link)
                successful_count += 1
                print(f'Подписка на {link}')
            except InviteRequestSent:
                successful_count += 1
                print(f'Подана заявка {link}')
            except Exception as e:
                unsuccessful_links.append(link)
                await userbot.send_message(admin_id, f'https://t.me/{link}\n{e}')
                print(f'ERROR!!! {e}')
            finally:
                waiting = (5 + 2 * random.random()) * 60
                await asyncio.sleep(waiting)

    un_str = '\n'.join([f'https://t.me/{link}' for link in unsuccessful_links])

    report = f'✅ **Подписка на чаты завершена!**\n' \
             f'Удачно: {successful_count}\n' \
             f'Неудачно:\n{un_str}'

    await userbot.send_message(
        admin_id,
        report,
        disable_web_page_preview=True
    )
