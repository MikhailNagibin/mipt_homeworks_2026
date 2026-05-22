import os
from typing import Any, Dict
from pathlib import Path
import yaml


def load_config() -> Dict[str, Any]:
    config: Dict[str, Any] = {}
    script_dir = Path(__file__).parent
    yaml_path = script_dir / 'config.yaml'
    with open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_config = yaml.safe_load(f)
        if yaml_config:
            config.update(yaml_config)
    env_map = {
        'API_KEY': 'api_key',
        'API_HOST': 'api_host',
        'LIMIT_MESSAGE': 'limit_message',
        'LIMIT_CHARS': 'limit_chars',
        'TEMPERATURE': 'temperature',
    }
    for env_var, cfg_key in env_map.items():
        value = os.environ.get(env_var)
        if value is not None:
            if cfg_key in ('limit_message', 'limit_chars'):
                config[cfg_key] = int(value)
            elif cfg_key == 'temperature':
                config[cfg_key] = float(value)
            else:
                config[cfg_key] = value

    if 'api_key' not in config or 'api_host' not in config:
        raise ValueError(
            'Не заданы обязательные параметры: api_key и api_host. '
            'Укажите их в config.yaml или переменных окружения API_KEY/API_HOST.'
        )

    config.setdefault('limit_message', None)
    config.setdefault('limit_chars', None)
    config.setdefault('temperature', 0.7)
    config.setdefault('system_prompt', None)

    if config['temperature'] < 0 or config['temperature'] > 1:
        raise ValueError('temperature должна быть в диапазоне [0, 1]')

    if config['limit_message'] is not None and config['limit_message'] <= 0:
        raise ValueError('limit_message должен быть положительным')

    if config['limit_chars'] is not None and config['limit_chars'] <= 0:
        raise ValueError('limit_chars должен быть положительным')

    return config
