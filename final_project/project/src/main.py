import sys
import signal
from .config import load_config
from typing import Any
from .history import HistoryManager
from .api_client import stream_chat_completion
from .file_utils import replace_file_contents
from .commands import cmd_reset, cmd_file_chunk


def custom_input() -> str:
    print('>>>', end=' ', flush=True)
    try:
        raw_line = sys.stdin.buffer.readline()
        if not raw_line:
            return ''
        return raw_line.decode('utf-8', errors='replace').strip()
    except KeyboardInterrupt:
        raise
    except Exception:
        return ''


def interrupt_handler(signum: Any, frame: Any) -> Exception:
    raise KeyboardInterrupt()


config = load_config()
api_host = config['api_host']
api_key = config['api_key']
limit_message = config.get('limit_message')
limit_chars = config.get('limit_chars')
temperature = config['temperature']
system_prompt = config.get('system_prompt')

history = HistoryManager(limit_message, limit_chars)

print('Добро пожаловать в GigaVibeMiptCode Чат!')
print(r'Команды: \q - выход, /reset - очистить историю, /file_chunk - обработка файла по частям.')
print('Вставляйте файлы через @::путь::\n')

while True:
    try:
        user_input = custom_input()
    except KeyboardInterrupt:
        print('\nДо свидания!')
        sys.exit(0)

    if not user_input:
        continue

    if user_input == r'\q':
        print('До свидания!')
        sys.exit(0)

    if user_input == '/reset':
        cmd_reset(history)
        continue

    if user_input.startswith('/file_chunk'):
        args = user_input[len('/file_chunk'):].strip()
        cmd_file_chunk(history, api_host, api_key, temperature, system_prompt, args)
        continue

    processed_input = replace_file_contents(user_input)

    history.add_message('user', processed_input)

    messages_for_api = history.get_messages_for_api(system_prompt)

    print('Ассистент: ', end='', flush=True)
    assistant_reply = ''
    try:
        old_handler = signal.signal(signal.SIGINT, interrupt_handler)

        for token in stream_chat_completion(
                messages_for_api, api_host, api_key, temperature
        ):
            print(token, end='', flush=True)
            assistant_reply += token

        signal.signal(signal.SIGINT, old_handler)
        print()

    except KeyboardInterrupt:
        print('\n[Прервано пользователем]')
        continue
    except Exception as e:
        print(f'\nОшибка при запросе к LLM: {e}')
        continue

    if assistant_reply:
        history.add_message('assistant', assistant_reply)
