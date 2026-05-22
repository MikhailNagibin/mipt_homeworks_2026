from src.history import HistoryManager


def test_add_message() -> None:
    h = HistoryManager(limit_message=3, limit_chars=100)
    h.add_message('user', 'Hello')
    assert len(h.messages) == 1
    assert h.messages[0]['role'] == 'user'
    assert h.messages[0]['content'] == 'Hello'


def test_limit_messages() -> None:
    h = HistoryManager(limit_message=2, limit_chars=100)
    h.add_message('user', '1')
    h.add_message('assistant', '2')
    h.add_message('user', '3')
    assert len(h.messages) == 2
    assert h.messages[0]['content'] == '2'
    assert h.messages[1]['content'] == '3'


def test_limit_chars() -> None:
    h = HistoryManager(limit_message=10, limit_chars=20)
    h.add_message('user', '12345')
    h.add_message('assistant', '67890')
    h.add_message('user', 'ABCDE')
    assert len(h.messages) <= 3
    total_chars = sum(len(m['content']) for m in h.messages)
    assert total_chars <= 20


def test_get_messages_for_api_without_system() -> None:
    h = HistoryManager(limit_message=10, limit_chars=1000)
    h.add_message('user', 'Hi')
    h.add_message('assistant', 'Hello')
    result = h.get_messages_for_api(system_prompt=None)
    assert len(result) == 2
    assert result[0]['role'] == 'user'
    assert result[1]['role'] == 'assistant'


def test_get_messages_for_api_with_system() -> None:
    h = HistoryManager(limit_message=10, limit_chars=1000)
    h.add_message('user', 'Hi')
    result = h.get_messages_for_api(system_prompt='You are a bot')
    assert len(result) == 2
    assert result[0]['role'] == 'system'
    assert result[0]['content'] == 'You are a bot'
    assert result[1]['role'] == 'user'


def test_reset() -> None:
    h = HistoryManager(limit_message=10, limit_chars=1000)
    h.add_message('user', 'test')
    h.reset()
    assert len(h.messages) == 0
