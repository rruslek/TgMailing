import asyncio
import os


# Состояния работы основных функций бота
def is_running(name: str) -> bool:
    for task in asyncio.all_tasks():
        if task.get_coro().__qualname__ == f'{name}':
            print(f'is_running: найдена задача {name}')
            return True
    print(f'is_running: НЕ найдена задача {name}')
    return False


def stop_running(name: str) -> bool:
    for task in asyncio.all_tasks():
        if task.get_coro().__qualname__ == f'{name}':
            print(f'stop_running: завершена задача {name}')
            task.cancel()
            return True
    else:
        return False


# Интервал рассылки
def get_delta() -> int:
    with open("delta.txt", "r") as file:
        delta = int(file.read())
    return delta


def set_delta(delta: int) -> None:
    with open("delta.txt", "w") as file:
        file.write(f'{delta}')


# Чаты
def get_chats(chat_category: str) -> list[int]:
    with open(f"{chat_category}.txt", "r") as file:
        chat_ids = [int(line.strip()) for line in file.readlines() if line != '\n']
    return chat_ids


def update_chats(chat_category: str, chat_ids: list[int | str]) -> None:
    with open(f"{chat_category}.txt", "w") as file:
        for chat_id in chat_ids:
            file.write(f'{chat_id}\n')


# Создание/удаление текстовых файлов
def create_file(file_name: str, elements: list) -> None:
    with open(f"{file_name}.txt", "w") as file:
        for element in elements:
            file.write(f'{element}\n')


def delete_file(file_name: str) -> None:
    if os.path.isfile(f'{file_name}.txt'):
        os.remove(f'{file_name}.txt')


# Счётчик рассылок
def update_mailing_count() -> int:
    with open('mailing_counter.txt', 'r+') as file:
        mailing_counter = int(file.read() or 0)
        mailing_counter += 1
        file.seek(0)
        file.write(str(mailing_counter))
    return mailing_counter
