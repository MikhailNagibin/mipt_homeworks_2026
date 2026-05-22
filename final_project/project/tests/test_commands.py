import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from src.commands import cmd_reset, cmd_file_chunk


def test_cmd_reset() -> None:
    history_mock = Mock()
    cmd_reset(history_mock)
    history_mock.reset.assert_called_once()


@patch('src.commands.stream_chat_completion')
@patch('builtins.input')
@patch('builtins.print')
def test_cmd_file_chunk(mock_print: Mock, mock_input: Mock,
                            mock_stream: Mock, tmp_path: Path) -> None:
    test_file = tmp_path / 'test.txt'
    test_file.write_text('Line1\nLine2\nLine3')

    mock_input.side_effect = [str(test_file), 'Кратко суммаризируй']

    history_mock = Mock()
    history_mock.get_messages_for_api.return_value = []

    mock_stream.return_value = iter(['Ответ ', 'модели'])

    try:
        cmd_file_chunk(history_mock, 'http://host', 'key', 0.5, 'system', '')
    except Exception as e:
        pytest.fail(f'Функция вызвала исключение: {e}')

    mock_stream.assert_called()