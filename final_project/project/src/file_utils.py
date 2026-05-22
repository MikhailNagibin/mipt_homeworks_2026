import os
import re
from typing import List, Iterator

MAX_FILE_SIZE = 5 * 1024 * 1024


def extract_file_paths(text: str) -> List[str]:
    pattern = r'@::(.*?)::'
    return re.findall(pattern, text)


def load_file_content(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f'Файл не найден: {path}')
    if os.path.getsize(path) > MAX_FILE_SIZE:
        raise ValueError(f'Файл {path} превышает максимальный размер (5 МБ)')
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def replace_file_contents(text: str) -> str:
    paths = extract_file_paths(text)
    for path in paths:
        try:
            content = load_file_content(path)
        except (FileNotFoundError, ValueError) as e:
            content = f'[Ошибка загрузки файла: {e}]'
        text = text.replace(f'@::{path}::', content)
    return text

def chunk_by_paragraphs(content: str, paragraphs_per_chunk: int = 1) -> Iterator[str]:
    paragraphs = content.split('\n\n')
    for i in range(0, len(paragraphs), paragraphs_per_chunk):
        yield '\n\n'.join(paragraphs[i:i + paragraphs_per_chunk])


def chunk_by_len(content: str, chunk_size: int) -> Iterator[str]:
    for i in range(0, len(content), chunk_size):
        yield content[i:i + chunk_size]


def chunk_file(file_path: str, method: str, param: int = 1) -> Iterator[str]:
    content = load_file_content(file_path)
    if method == 'paragraph':
        return chunk_by_paragraphs(content, param)
    elif method == 'len':
        return chunk_by_len(content, param)
    else:
        raise ValueError(f'Неизвестный метод чанкинга: {method}')
