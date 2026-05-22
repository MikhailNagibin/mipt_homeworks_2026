import os
from typing import Optional

from history import HistoryManager
from api_client import stream_chat_completion
from file_utils import chunk_file


def cmd_reset(history: HistoryManager) -> None:
    history.reset()
    os.system('cls' if os.name == 'nt' else 'clear')
    print('История очищена, начинаем новый диалог.\n')


def cmd_file_chunk(history: HistoryManager, api_host: str, api_key: str,
                        temperature: float, system_prompt: Optional[str], args: str) -> None:
    auto_mode = False
    method = 'paragraph'
    param = 1

    parts = args.strip().split()
    for part in parts:
        if part == '-y':
            auto_mode = True
        elif part.startswith('paragraph='):
            method = 'paragraph'
            param = int(part.split('=')[1])
        elif part.startswith('len='):
            method = 'len'
            param = int(part.split('=')[1])

    file_path = input('Введите путь до файла: ').strip()
    if not file_path:
        print('Путь не может быть пустым.')
        return

    user_prompt = input('Что нужно сделать для каждого фрагмента (User Prompt)?\n').strip()
    if not user_prompt:
        print('Prompt не может быть пустым.')
        return

    print('Принято. Начинаю обработку:')

    try:
        chunks = list(chunk_file(file_path, method, param))
    except Exception as e:
        print(f'Ошибка при чтении файла: {e}')
        return

    total = len(chunks)
    for idx, chunk_text in enumerate(chunks, 1):
        print(f'\n--- Чанк {idx}/{total} ---')
        full_message = f'{user_prompt}\n\n{chunk_text}'

        messages_for_api = []
        if system_prompt:
            messages_for_api.append({'role': 'system', 'content': system_prompt})
        messages_for_api.append({'role': 'user', 'content': full_message})

        try:
            response_text = ''
            for token in stream_chat_completion(messages_for_api, api_host, api_key, temperature):
                print(token, end='', flush=True)
                response_text += token
            print()
        except Exception as e:
            print(f'\nОшибка при запросе к LLM: {e}')

        if not auto_mode and idx < total:
            input('Нажмите Enter для следующего чанка...')

    print('\nОбработка файла завершена.')
