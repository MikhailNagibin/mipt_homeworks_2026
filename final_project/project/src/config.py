import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv

load_dotenv()

def load_config() -> Dict[str, Any]:
    config: Dict[str, Any] = {}

    yaml_path = Path(__file__).parent.parent / 'config.yaml'
    if yaml_path.exists():
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                config.update(yaml_config)

    env_map = {
        'API_KEY': 'api_key',
        'API_HOST': 'api_host',
        'LIMIT_MESSAGE': 'limit_message',
        'LIMIT_CHARS': 'limit_chars',
        'MODEL_NAME': 'model_name',
        'TEMPERATURE': 'temperature',
    }
    for env_var, cfg_key in env_map.items():
        value = os.getenv(env_var)
        if value is not None:
            if cfg_key in ('limit_message', 'limit_chars'):
                config[cfg_key] = int(value)
            elif cfg_key == 'temperature':
                config[cfg_key] = float(value)
            else:
                config[cfg_key] = value

    if 'api_key' not in config or 'api_host' not in config:
        raise ValueError(
            """Не заданы обязательные параметры api_key и api_host. 
            Укажите их в .env, переменных окружения или config.yaml"""
        )

    config.setdefault('limit_message', None)
    config.setdefault('limit_chars', None)
    config.setdefault('temperature', 0.7)
    config.setdefault('model_name', 'gemma2:2b')
    config.setdefault('system_prompt', None)

    if config['temperature'] < 0 or config['temperature'] > 1:
        raise ValueError('temperature должна быть в [0,1]')

    return config
