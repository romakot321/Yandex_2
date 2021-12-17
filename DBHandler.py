import sqlite3
from random import choice
from typing import Dict, Any
import xml.etree.ElementTree as ET


class Handler:
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    texts = ET.parse('texts.xml').getroot()

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

    @staticmethod
    def get_dialog(dialog_name):
        a = Handler.cur.execute(f'SELECT * FROM dialog WHERE name = "{dialog_name}"').fetchall()
        if a:
            return a[0]

    @staticmethod
    def get_items(item_name: str = None, typ: str = None, for_slot: str = None):
        from item import Item
        a = None
        if item_name:
            a = Handler.cur.execute(f'SELECT * FROM items WHERE name = "{item_name.lower()}"').fetchall()
        elif typ:
            a = Handler.cur.execute(f'SELECT * FROM items WHERE type = "{typ.lower()}"').fetchall()
        elif for_slot:
            a = Handler.cur.execute(f'SELECT * FROM items WHERE for_slot = "{for_slot.lower()}"').fetchall()
        if a:
            ret = []
            for i in a:
                stats = {
                    'price': i[3],
                    'drop_chance': i[4],
                    'armor': i[5],
                    'damage': i[6]
                }
                ret.append(Item(*i[:3], **stats))
            return ret
        return None

    @staticmethod
    def get_quest(name, init=True, is_main_quest=False):
        from item import Item
        if init:
            from config import Quest, Target
        if is_main_quest:
            result = Handler.cur.execute('SELECT * FROM main_quests').fetchall()
        else:
            result = Handler.cur.execute(f'SELECT * FROM quests WHERE name = "{name.lower()}"').fetchall()
        if result:
            if is_main_quest:
                result = choice(result)
            else:
                result = result[0]
            if result[2] == 'collect' or result[2] == 'sell':
                o = Item.getItem(result[3])
            elif result[2] == 'kill':
                o = result[3]
            if init:
                t = Target(result[2], o, result[4])
            else:
                t = (result[2], o, result[4])
            r = []
            if not is_main_quest:
                for i in result[5].split(','):
                    if 'coins' in i:
                        r.append(i)
                        continue
                    r.append(Item.getItem(i.strip()))
            if init:
                return Quest(result[1], t, r)
            return result[1], t, r

    @staticmethod
    def get_keywords():
        res = Handler.cur.execute('SELECT * FROM keywords').fetchall()
        ret = {}
        for action, words, add_words in res:
            ret[action] = (list(map(lambda i: i.strip(), words.split(','))),
                           list(map(lambda i: i.strip(), add_words.split(','))))
        return ret

    @staticmethod
    def get_journalphrase(action_name) -> str:
        """Получение фраз для журнала действий по названию действия"""
        for action in Handler.texts:
            if action_name == action.attrib['name']:
                return [i.text for i in action]