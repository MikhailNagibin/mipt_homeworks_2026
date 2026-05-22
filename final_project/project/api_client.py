# mypy: ignore-errors

from typing import Iterator, List, Dict
from openai import OpenAI


def stream_chat_completion(messages: List[Dict[str, str]], api_host: str,
                                api_key: str,temperature: float = 0.7) -> Iterator[str]:
    client = OpenAI(base_url=api_host, api_key=api_key)

    response = client.chat.completions.create(
        model='gemma2:2b',
        messages=messages,
        temperature=temperature,
        stream=True,
    )

    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content