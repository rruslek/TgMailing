from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message, InputMediaDocument
from pyrogram.enums import ChatType, MessageEntityType

from config import admin_id
import asyncio
from helpers import set_delta, get_delta, stop_running, is_running, create_file, delete_file

from run_default_mailing import default_mailing
from run_auto_subscription import auto_subscription
from run_parsing import parsing


async def cmd_delta(userbot: Client, message: Message):
    """Выбор интервала рассылки"""
    print('! Запуск функции cmd_delta')
    if not is_running('default_mailing'):
        delta = message.text.split()[-1]
        if delta.isdigit():
            delta = int(delta)
            if 89 < delta < 1441:
                set_delta(delta)
                await userbot.send_message(
                    admin_id,
                    f'⏱ **Установлен временной интервал {delta} минут.**'
                )
            else:
                await userbot.send_message(
                    admin_id,
                    '❗️**Введите время от 90 до 1440 минут!**'
                )
        else:
            await userbot.send_message(
                admin_id,
                '❗️**Введите команду в нужном формате! Например, команда `/delta 120`'
                ' установит интервал между рассылками в 120 минут.**'
            )

    else:
        await userbot.send_message(
            admin_id,
            '❗️**Остановите рассылку, чтобы изменить временной интервал.**'
        )


async def cmd_start(userbot: Client, message: Message):
    """
    Обработчик для рассылки.
    1-ый if: корректно ли введена команда
    2-й if: соответствует ли число постов условию 0 < post_count < 11
    Если данные условия соблюдены, то бот получает данные,
    необходимые для начала рассылки: количество рассылаемых
    сообщений уже есть, осталось найти чаты. После того,
    как чаты получены начинаем рассылку вызвав функцию default_mailing
    3-й if: запущена ли функция рассылки/анализа/парсинга/авто-подписки
    """
    print('! Запуск функции cmd_start')
    post_count = '1' if message.text == '/start' else message.text.split()[-1]
    if post_count.isdigit():
        post_count = int(post_count)
        if 0 < post_count < 11:
            if \
                    not is_running('default_mailing') \
                    and not is_running('auto_subscription') \
                    and not is_running('analysis') \
                    and not is_running('parsing'):
                # Получим список чатов для рассылки, заодно укажем их количество
                dialogs = userbot.get_dialogs()
                chats = []
                chat_count = 0
                async for dialog in dialogs:
                    chat = dialog.chat
                    if chat.type == ChatType.GROUP or chat.type == ChatType.SUPERGROUP:
                        chat_count += 1
                        chats.append(chat)

                # Сообщаем пользователю о начале рассылки. Указываем её параметры
                await userbot.send_message(
                    admin_id,
                    f'✅ **Рассылка началась!**\n'
                    f'Интервал: {get_delta()} мин.\n'
                    f'Сообщений рассылается: {post_count}\n'
                    f'Чатов: {chat_count}'
                )

                # Итак, у нас есть чаты для рассылки (chats) и число рассылаемых сообщений (post_count).
                # Теперь можно начать рассылку, передав нашей функции default_mailing соответствующие аргументы
                # await default_mailing(userbot, message, chats, post_count)
                asyncio.create_task(default_mailing(userbot, message, chats, post_count))
            else:
                await userbot.send_message(
                    admin_id,
                    '❗️**Бот уже работает!**\n\n'
                    '💡 Чтобы начать рассылку, остановите текущую задачу командой `/stop`.'
                )
        else:
            await userbot.send_message(
                admin_id,
                '❗️**Введите число рассылаемых сообщений от 1 до 10.**'
            )
    else:
        await userbot.send_message(
            admin_id,
            '💡 **Чтобы начать рассылку одного сообщения, введите `/start` или `/start 1`.**\n'
            'Если же вы хотите рассылать несколько рекламных сообщений, то введите `/start N`, '
            'где N - число сообщений для рассылки (от 1 до 10). При такой рассылке последние '
            'N сообщений в **избранном** на аккаунте бота и будут рассылаться!'
        )


async def cmd_subscribe(userbot: Client, message: Message):
    """
    Авто-подписка на чаты по ссылкам.
    Выделяем все сущности из сообщения,
    оставляем только ссылки на чаты,
    передаём их в функцию авто-подписки
    """
    text = message.text
    entities = message.entities
    if entities:
        if \
                not is_running('default_mailing') \
                and not is_running('auto_subscription') \
                and not is_running('analysis') \
                and not is_running('parsing'):
            links = []
            for entity in entities:
                if entity.type == MessageEntityType.MENTION:
                    offset = entity.offset
                    length = entity.length
                    link = text[offset: offset + length]
                    link = link.replace('@', '')
                    links.append(link)

                if entity.type == MessageEntityType.URL:
                    offset = entity.offset
                    length = entity.length
                    link = text[offset: offset + length]
                    link = link.split('/')[-1]
                    links.append(link)

                if entity.type == MessageEntityType.TEXT_LINK:
                    link = entity.url
                    link = link.split('/')[-1]
                    links.append(link)

            links = set(links)
            await userbot.send_message(
                admin_id,
                f'⌛️ **Авто-подписка запущена! Среднее время между'
                f' двумя последовательными подписками - 6 минут.**\n'
                f'Уникальных ссылок: {len(links)}\n'
                f'Оставшееся время: около {round(len(links) * 6 / 60, 1)} ч.\n\n'
                f'💡 Когда я закончу подписываться на чаты, пришлю уведомление! '
                f'Так же вы можете в любой момент остановить авто-подписку командой `/stop`.\n'
                f'P.S. Уже добавленные чаты пропускаются.')

            asyncio.create_task(auto_subscription(userbot, links))

        else:
            await userbot.send_message(
                admin_id,
                '❗️**Бот уже работает!**\n\n'
                '💡 Чтобы начать авто-подписку, остановите текущую задачу командой `/stop`.'
            )

    else:
        await userbot.send_message(
            admin_id,
            '❗️В вашем сообщении нет ссылок на чаты!\n\n'
            '💡 Чтобы начать авто-подписку, сообщение должно начинаться '
            'с команды `/subscribe`, а так же содержать ссылки на чаты. '
            'Причём не важно указаны ссылки в строку/столбец или зашиты в текст.'
        )


async def cmd_parse(userbot: Client, message: Message):
    """
    Парсер чатов.
    1-ый if: Запущены ли другие задачи. Если всё ок,
    2-ой if: пользователь ввёл айди группы
    Если второй if не выполнен, то ищем ссылки в сообщении.
    """
    if \
            not is_running('default_mailing') \
            and not is_running('auto_subscription') \
            and not is_running('analysis') \
            and not is_running('parsing'):
        text = message.text
        chat_id = text.split()[-1]

        if chat_id.replace('-', '').isdigit():
            chat_id = int(chat_id)
            pass
        elif 't.me/' in chat_id:
            chat_id = chat_id.split('t.me/')[-1]
            pass
        elif '@' in chat_id:
            chat_id = chat_id.replace('@', '')
            pass
        else:
            chat_id = False

        print(chat_id)
        if chat_id:
            await userbot.send_message(
                admin_id,
                '👥 Парсинг запущен! Ожидайте.'
            )
            if '!' in text:
                asyncio.create_task(parsing(userbot, message, chat_id, parse_messages=True))
            else:
                asyncio.create_task(parsing(userbot, message, chat_id))
        else:
            await userbot.send_message(
                admin_id,
                '❗️**Некорректный идентификатор чата!**\n\n'
                '💡 Чтобы осуществить парсинг группы, введите команду `/parse`. '
                'Через пробел укажите либо id группы (число в ссылке на чат в web версии telegram. '
                'Начинается на "-100"), либо ссылку на группу (содержащую @ или t.me/)'
            )

    else:
        await userbot.send_message(
            admin_id,
            '❗️**Бот уже работает!**\n\n'
            '💡 Чтобы осуществить парсинг группы, остановите текущую задачу командой `/stop`.'
        )


async def cmd_get_chats(userbot: Client, message: Message):
    """Получить все чаты в текстовом файле"""
    if \
            not is_running('default_mailing') \
            and not is_running('auto_subscription') \
            and not is_running('analysis') \
            and not is_running('parsing'):
        dialogs = userbot.get_dialogs()
        chat_ids = []
        chat_count = 0
        async for dialog in dialogs:
            chat = dialog.chat
            if chat.type == ChatType.GROUP or chat.type == ChatType.SUPERGROUP:
                chat_count += 1
                chat_username = chat.username
                if chat_username:
                    chat_ids.append(f'{chat_count}. https://t.me/{chat_username}')
                else:
                    chat_ids.append(f'{chat_count}. https://t.me/{chat.invite_link}')

        create_file('chats_copy', chat_ids)
        text = f'✅ Готово! Текстовый документ содержит {chat_count} чатов.'
        await userbot.send_document(chat_id=admin_id, document='chats_copy.txt', caption=text)
        delete_file('chats_copy')

    else:
        await userbot.send_message(
            admin_id,
            '❗️**Бот уже работает!**\n\n'
            '💡 Чтобы сделать резервную копию чатов, остановите текущую задачу командой `/stop`.'
        )


async def cmd_stop(userbot: Client, message: Message):
    """Остановка рассылки"""
    print('! Запуск функции cmd_stop')
    stopped_default_mailing = stop_running('default_mailing')
    stopped_auto_subscription = stop_running('auto_subscription')
    stopped_analysis = stop_running('analysis')
    stopped_parsing = stop_running('parsing')

    if stopped_default_mailing:
        await userbot.send_message(
            admin_id,
            '✅ Рассылка остановлена!\n\n'
            '💡 Если вы хотите начать новую рассылку, '
            'Запускайте ее **минимум через час**, '
            'считая от конца предыдущей!'
        )
    elif stopped_auto_subscription:
        await userbot.send_message(
            admin_id,
            '✅ Авто-подписка остановлена!\n\n'
            '💡 Если вы хотите начать рассылку, '
            'Запускайте ее **минимум через час** с этого момента!'
        )
    elif stopped_analysis:
        pass
    elif stopped_parsing:
        pass
    else:
        await userbot.send_message(
            admin_id,
            '✅ У бота нет активных задач!'
        )


async def test(userbot: Client, message: Message):
    print(message.text)
    print('!' in message.text)


def register_handlers(userbot: Client):
    # userbot.add_handler(MessageHandler(cmd_help, filters=filters.command(['help', 'doc']) & filters.chat(admin_id)))
    userbot.add_handler(MessageHandler(cmd_delta, filters=filters.command('delta') & filters.chat(admin_id)))
    userbot.add_handler(MessageHandler(cmd_start, filters=filters.command('start') & filters.chat(admin_id)))
    userbot.add_handler(MessageHandler(cmd_subscribe, filters=filters.command('subscribe') & filters.chat(admin_id)))
    userbot.add_handler(MessageHandler(cmd_get_chats, filters=filters.command('get_chats') & filters.chat(admin_id)))
    userbot.add_handler(MessageHandler(cmd_parse, filters=filters.command(['parse', 'parse!']) & filters.chat(admin_id)))
    userbot.add_handler(MessageHandler(cmd_stop, filters=filters.command('stop') & filters.chat(admin_id)))

    userbot.add_handler(MessageHandler(test, filters=filters.command(['test', 'test!']) & filters.chat(admin_id)))
