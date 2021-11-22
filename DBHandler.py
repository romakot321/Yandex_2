import sqlite3
from typing import Dict, Any


class Handler:
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()

    @staticmethod
    def get_locations_params(loc_name) -> tuple:
        # TODO получение всех параметвор локации, вовращает None если такой локации нет
        # Иначе возвращает параметры в виде (param_name, param_value)
        pass

    @staticmethod
    def save_locations_params(**params: Dict[str, Any]):
        """
        :param params: {(param_name, param_value)}
        """
        # TODO сохранение всех параметвор локации
        pass