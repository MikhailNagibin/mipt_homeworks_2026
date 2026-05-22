from typing import List, Dict, Optional


class HistoryManager:
    def __init__(self, limit_message: Optional[int], limit_chars: Optional[int]):
        self.limit_message = limit_message
        self.limit_chars = limit_chars
        self.messages: List[Dict[str, str]] = []

    def _total_chars(self) -> int:
        return sum(len(m['content']) for m in self.messages)

    def _enforce_limits(self, new_message: Dict[str, str]) -> List[Dict[str, str]]:
        self.messages.append(new_message)
        if self.limit_message is not None and len(self.messages) > self.limit_message:
            excess = len(self.messages) - self.limit_message
            self.messages = self.messages[excess:]

        if self.limit_chars is not None:
            while self._total_chars() > self.limit_chars and len(self.messages) > 1:
                self.messages.pop(0)

            if len(self.messages) == 1 and self._total_chars() > self.limit_chars:
                content = self.messages[0]['content']
                excess_chars = self._total_chars() - self.limit_chars
                self.messages[0]['content'] = content[excess_chars:]

        self.messages.pop()
        temp_messages = self.messages + [new_message]
        if self.limit_message is not None and len(temp_messages) > self.limit_message:
            excess = len(temp_messages) - self.limit_message
            temp_messages = temp_messages[excess:]

        if self.limit_chars is not None:
            while (sum(len(m['content']) for m in temp_messages) > self.limit_chars
                        and len(temp_messages) > 1):
                temp_messages.pop(0)
            if (len(temp_messages) == 1
                        and sum(len(m['content']) for m in temp_messages) > self.limit_chars):
                content = temp_messages[0]['content']
                excess_chars = sum(len(m['content']) for m in temp_messages) - self.limit_chars
                temp_messages[0]['content'] = content[excess_chars:]

        return temp_messages

    def add_message(self, role: str, content: str) -> None:
        new_msg = {'role': role, 'content': content}
        new_history = self._enforce_limits(new_msg)
        self.messages = new_history

    def get_messages_for_api(self, system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        if system_prompt:
            return [{'role': 'system', 'content': system_prompt}] + self.messages
        return self.messages.copy()

    def reset(self) -> None:
        self.messages.clear()

    def get_history_size(self) -> int:
        return len(self.messages)
