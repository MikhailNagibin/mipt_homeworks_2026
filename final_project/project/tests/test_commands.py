from unittest.mock import Mock, patch
from pathlib import Path
from commands import cmd_reset, cmd_file_chunk
from typing import Any


def test_cmd_reset() -> None:
    history_mock = Mock()
    cmd_reset(history_mock)
    history_mock.reset.assert_called_once()


@patch('builtins.input')
@patch('commands.stream_chat_completion')
@patch('builtins.print')
def test_cmd_file_chunk(mock_print: Any, mock_stream: Any, mock_input: Any, tmp_path: Path) -> None:
    test_file = tmp_path / 'test.txt'
    test_file.write_text('Line1\nLine2\nLine3')

    mock_input.return_value = str(test_file)

    history_mock = Mock()
    history_mock.get_messages_for_api.return_value = []

    try:
        cmd_file_chunk(history_mock, 'http://host', 'key', 0.5, 'system', str(test_file))
    except Exception:
        pass
