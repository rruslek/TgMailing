from pyrogram import Client
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message, InputMediaDocument
from helpers import create_file, delete_file
from config import admin_id


async def parsing(userbot: Client, message: Message, chat_id: int | str, parse_messages=False):
    """Приспособить это под инвайт! (парсинг айдишек членов группы)"""
    if parse_messages:
        messages = userbot.get_chat_history(chat_id, 2999)

        senders = []
        mentions = []

        senders_counter = 0
        mentions_counter = 0

        test_counter = 0
        async for msg in messages:
            # /// TEST
            test_counter += 1
            print(f'message #{test_counter}:')
            print(f'entities: {len(msg.entities) if msg.entities else "None"}')
            print(f'caption_entities: {len(msg.caption_entities) if msg.caption_entities else "None"}')
            print()
            # ///

            username = msg.from_user.username if msg.from_user else None
            entities = msg.entities or msg.caption_entities
            text = msg.text or msg.caption

            if username:
                senders_counter += 1
                senders.append(f'https://t.me/{username}')

            if entities and text:
                for entity in entities:
                    if entity.type == MessageEntityType.MENTION:
                        offset = entity.offset
                        length = entity.length

                        mention = text[offset: offset + length]

                        mentions_counter += 1
                        mentions.append(f'{mention}')

        create_file(
            'senders',
            ['Уникальные отправители сообщений:'] +
            [f'{i}. {s}' for i, s in enumerate(set(senders))]
        )
        create_file(
            'mentions',
            ['Ссылки, начинающиеся на "@", содержащиеся в сообщениях (mentions):'] +
            [f'{i}. {m}' for i, m in enumerate(set(mentions))]
        )

        await userbot.send_media_group(
            chat_id=admin_id,
            media=[
                InputMediaDocument('senders.txt'),
                InputMediaDocument('mentions.txt'),
            ],
        )

        delete_file('senders')
        delete_file('mentions')

    else:
        members = userbot.get_chat_members(chat_id)

        members_ONLINE = ['Онлайн на данный момент:']
        members_OFFLINE = ['Офлайн на данный момент:']
        members_RECENTLY = ['Были в сети "недавно":']
        members_LAST_WEEK = ['Были в сети на прошлой неделе']
        members_LAST_MONTH = ['Были в сети в прошлом месяце']
        members_LONG_AGO = ['Давно не были в сети']
        members_ALL = ['ALL:']

        members_ONLINE_counter = 0
        members_OFFLINE_counter = 0
        members_RECENTLY_counter = 0
        members_LAST_WEEK_counter = 0
        members_LAST_MONTH_counter = 0
        members_LONG_AGO_counter = 0
        members_ALL_counter = 0

        async for member in members:
            user = member.user
            username = user.username
            status = user.status
            if username and status:
                print('successful', username)
                members_ALL_counter += 1
                members_ALL.append(f'{members_ALL_counter}. https://t.me/{username}')

                if status == status.ONLINE:
                    members_ONLINE_counter += 1
                    members_ONLINE.append(f'{members_ONLINE_counter}. https://t.me/{username}')

                elif status == status.OFFLINE:
                    members_OFFLINE_counter += 1
                    members_OFFLINE.append(f'{members_OFFLINE_counter}. https://t.me/{username}')

                elif status == status.RECENTLY:
                    members_RECENTLY_counter += 1
                    members_RECENTLY.append(f'{members_RECENTLY_counter}. https://t.me/{username}')

                elif status == status.LAST_WEEK:
                    members_LAST_WEEK_counter += 1
                    members_LAST_WEEK.append(f'{members_LAST_WEEK_counter}. https://t.me/{username}')

                elif status == status.LAST_MONTH:
                    members_LAST_MONTH_counter += 1
                    members_LAST_MONTH.append(f'{members_LAST_MONTH_counter}. https://t.me/{username}')

                elif status == status.LONG_AGO:
                    members_LONG_AGO_counter += 1
                    members_LONG_AGO.append(f'{members_LONG_AGO_counter}. https://t.me/{username}')

                else:
                    print('unsuccessful')
                    print(user)

        create_file('members_ALL', members_ALL)
        create_file('members_ONLINE', members_ONLINE)
        create_file('members_OFFLINE', members_OFFLINE)
        create_file('members_RECENTLY', members_RECENTLY)
        create_file('members_LAST_WEEK', members_RECENTLY)
        create_file('members_LAST_MONTH', members_RECENTLY)
        create_file('members_LONG_AGO', members_RECENTLY)

        await userbot.send_media_group(
            chat_id=admin_id,
            media=[
                InputMediaDocument('members_ALL.txt'),
                InputMediaDocument('members_ONLINE.txt'),
                InputMediaDocument('members_OFFLINE.txt'),
                InputMediaDocument('members_RECENTLY.txt'),
                InputMediaDocument('members_LAST_WEEK.txt'),
                InputMediaDocument('members_LAST_MONTH.txt'),
                InputMediaDocument('members_LONG_AGO.txt'),
            ],
        )
        delete_file('members_ALL')
        delete_file('members_ONLINE')
        delete_file('members_OFFLINE')
        delete_file('members_RECENTLY')
