from pyrogram import Client
from pyrogram.types import Message, Chat
from pyrogram.errors import UserBannedInChannel, Forbidden, ChatWriteForbidden
import asyncio
import random
from helpers import get_chats, update_chats, update_mailing_count, get_delta, stop_running
from config import admin_id


async def default_mailing(userbot: Client, message: Message, chats: list[Chat], post_count: int):
    i = 0   # Индекс списка posts
    while True:
        # /// ПОДГОТОВКА ДАННЫХ///
        # 1. Получаем рекламные сообщения (posts) и конкретный пост, который будем рассылать
        # и предупреждаем о превью
        posts = []
        async for post in userbot.get_chat_history('self', post_count):
            posts.append(post)
            if post.web_page:
                await userbot.send_message(
                    chat_id=admin_id,
                    text='⚠️ **Ваш рекламный пост содержит превью ссылки!**\n'
                         'Во многих чатах запрещена отправка сообщений с превью. '
                         'Чтобы рассылка охватила наибольшее количество чатов, '
                         'уберите превью из поста.',
                    disable_web_page_preview=True
                )
        post = posts[i]

        # 2. Перемешиваем список чатов
        random.shuffle(chats)

        # 3. Получаем списки id-шек чатов с баном и чатов без медиа
        chat_ids_ban = get_chats('chats_ban')
        chat_ids_not_media = get_chats('chats_not_media')

        # 4. Генерируем 2 временных параметра:
        # ПАРАМЕТР variation [сек] - разброс временного интервала между двумя
        # последовательными итерациями рассылки.
        # ПАРАМЕТР dt [сек] - средний временной интервал между двумя
        # последовательными отправками рекламного сообщения в пределах одной
        # итерации.
        variation = random.randint(-20, 20) * 60
        dt = random.randint(3, 5)

        # /// РАССЫЛКА ///
        successful_count = 0        # Счётчик удачных отправок
        unsuccessful_send = []      # Неудачные отправки (список строк chat_info)
        bans = []                   # Баны               (список строк chat_info)
        chats_count = len(chats)

        await userbot.send_message(admin_id, f'Работаю... жди {int(chats_count * dt / 60)} мин!')
        for k, chat in enumerate(chats):
            chat_id = chat.id
            # Отправка сообщения идёт в чаты без бана
            if chat_id not in chat_ids_ban:
                chat_title = chat.title
                chat_username = chat.username
                chat_info = f'[{chat_title}](https://t.me/{chat_username})'
                try:

                    # Рассматриваются 2 случая: сообщение текстовое или же
                    # содержит caption (будем считать, что это эквивалентно
                    # тому, что сообщение содержит медиа, то есть фото/gif/видео).
                    if post.text:
                        await post.forward(chat_id)
                        print(f'{k}/{chats_count} Успешно! {chat_info}')
                    if post.caption:
                        if chat_id in chat_ids_not_media:
                            caption = post.caption.html
                            await userbot.send_message(chat_id, caption, disable_web_page_preview=True)
                            print(f'{k}/{chats_count} Успешно! (без фото) {chat_info}')
                        else:
                            await post.forward(chat_id)
                            print(f'{k}/{chats_count} Успешно! (с фото) {chat_info}')
                    successful_count += 1

                except ChatWriteForbidden:      # Бан в чате
                    chat_ids_ban.append(chat_id)
                    bans.append(chat_info)
                    print(f'{k}/{chats_count} Отправка не удалась! (бан в чате) {chat_info}')

                except Forbidden:               # Чат без медиа
                    chat_ids_not_media.append(chat_id)
                    print(f'{k}/{chats_count} Отправка не удалась! (добавлено исключение по медиа) {chat_info}')

                except UserBannedInChannel:     # Пойман спам
                    print(f'!!! {k}/{chats_count} Отправка не удалась! (!!!пойман спам!!!) {chat_info}')
                    await userbot.send_message(
                        admin_id,
                        '⚠️ **Рассылка остановлена так как я поймал спам! '
                        'Зайдите на мой аккаунт и напишите боту @SpamBot команду /start 2 раза.**'
                    )
                    stop_running('default_mailing')

                except Exception as e:          # Причина неизвестна
                    unsuccessful_send.append(chat_info)
                    print(f'{k}/{chats_count} Отправка не удалась! ({e}) {chat_info}')

            await asyncio.sleep(2 * dt * random.random())

        # /// ПОДГОТОВКА К СЛЕДУЮЩЕЙ ИТЕРАЦИИ ///
        # Обновляем списки банов и без медиа
        chat_ids_ban = list(set(chat_ids_ban))
        chat_ids_not_media = list(set(chat_ids_not_media))
        update_chats('chats_ban', chat_ids_ban)
        update_chats('chats_not_media', chat_ids_not_media)

        # Формируем отчёт
        mailing_counter = update_mailing_count()
        un_str = '\n'.join(unsuccessful_send)
        ban_str = '\n'.join(bans)


        unsuccessful_report = \
            f'**Неудачно: __{int(len(unsuccessful_send) / chats_count * 100)}%__**\n||{un_str}||' if un_str \
            else ''
        bans_report = \
            f'**Баны: __{int(len(bans) / chats_count * 100)}%__**\n||{ban_str}||' if ban_str \
            else ''
        report = \
            f'☑️ **Готово! [итерация #{mailing_counter}**{f", пост  #{i+1}" if len(posts) != 1 else ""}**]**\n' \
            f'**Удачно: __{int(successful_count / chats_count * 100)}%__** [{successful_count}/{chats_count}]\n' \
            f'{unsuccessful_report}\n' \
            f'{bans_report}'

        # Отправляем отчёт
        await userbot.send_message(admin_id, report, disable_web_page_preview=True)
        i = (i + 1) % post_count

        # Каждые 50 рассылок списки айди чатов без фото и баны сбрасываются (становятся пустыми)
        if mailing_counter % 50 == 0:
            update_chats('chats_ban', [])
            update_chats('chats_not_media', [])
            await userbot.send_message(
                admin_id,
                'ℹ️ Каждые 50 итераций рассылки список чатов без медиа и список чатов, '
                'в которых получен бан сбрасываются.'
            )

        delta = get_delta() * 60
        await asyncio.sleep(delta + variation)
