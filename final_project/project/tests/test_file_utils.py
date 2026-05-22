import os
import tempfile
from src.file_utils import replace_file_contents


def test_replace_file_contents_single() -> None:
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('File content')
        path = f.name

    try:
        text = f'Hello @::{path}:: world'
        result = replace_file_contents(text)
        assert 'File content' in result
        assert '@::' not in result
    finally:
        os.unlink(path)


def test_replace_file_contents_multiple() -> None:
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f1:
        f1.write('First file')
        path1 = f1.name
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f2:
        f2.write('Second file')
        path2 = f2.name

    try:
        text = f'First: @::{path1}:: and second: @::{path2}::'
        result = replace_file_contents(text)
        assert 'First file' in result
        assert 'Second file' in result
        assert '@::' not in result
    finally:
        os.unlink(path1)
        os.unlink(path2)


def test_replace_file_contents_no_match() -> None:
    text = 'No file markers here'
    assert replace_file_contents(text) == text


def test_replace_file_contents_nonexistent_file() -> None:
    text = 'File @::/nonexistent/path::'
    result = replace_file_contents(text)
    assert 'Ошибка' in result or result == text
