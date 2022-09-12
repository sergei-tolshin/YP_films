import datetime as dt
import json
from pathlib import Path
from typing import Optional

from state.base import BaseStorage
from config import CONFIG


MIN_TIMESTAMP = dt.datetime(dt.MINYEAR, 1, 1, 0, 0, 0, 0, dt.timezone.utc)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, dt.datetime):
            return o.isoformat()
        return o


def decode_tiemestamp(data_dict):
    if 'timestamp' in data_dict:
        timestamp = data_dict['timestamp']
        data_dict['timestamp'] = dt.datetime.fromisoformat(timestamp)
    return data_dict


class JsonFileStorage(BaseStorage):
    def __init__(self, state_name: str, file_dir: Optional[Path] = CONFIG.state_file_dir):
        file_path = file_dir / f'{state_name}.json'
        self.file_path = file_path

    def check_exists(self) -> bool:
        if self.file_path.exists():
            return True
        return False

    def save_state(self, state: dict) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as json_file:
            json.dump(state, json_file, cls=DateTimeEncoder)

    def retrieve_state(self) -> dict:
        with open(self.file_path, encoding='utf-8') as json_file:
            data = json.load(json_file, object_hook=decode_tiemestamp)
        return data
