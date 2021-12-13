# --- Константы
import datetime
import random
from typing import List, Union

from item import Item
from DBHandler import Handler

WIDTH = 800
HEIGHT = 650
# нулевые координаты для камеры - WIDTH // 2, HEIGHT // 2 - 25
BLOCK_SIZE = 50
FPS = 15

# --- Цвета
WHITE = (255, 255, 255)
FONT_TEXT = (10, 10, 10)
GRAY = (128, 128, 128)
LIGHT_GRAY = (160, 160, 164)
DARK_GRAY = (41, 59, 51)
STONE = (173, 165, 135)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (150, 0, 24)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 71, 49)
FOREST_GREEN = (11, 102, 35)
BLUE = (0, 0, 255)
BROWN = (115, 66, 23)
SAND = (252, 221, 118)
LIGHT_SAND = (255, 236, 139)
DARK_SAND = (214, 165, 4)
SKINCOLOR = (245, 245, 220)


# --- Вспомогательные классы
class Quest:
    def __init__(self, name, target: Union['Target', tuple], reward: List['Item'],
                 owner=None):
        """Конструктор Квеста

        :param name: Название
        :param target: Цель для завершения квеста
        :param reward: Вознаграждение за выполнение
        """
        self.name = name
        self.target = Target(*target) if isinstance(target, tuple) else target
        self.reward = reward
        self.owner = None

    def pass_quest(self, hero):
        if self.target.check_done(hero):
            for i in self.reward:
                if isinstance(i, str) and 'coins' in i:
                    hero.coins += int(i.replace('coins', '').strip())
                    self.reward.remove(i)
                    break
            hero.inventory.append(self.reward)
            if self.target.typ == 'collect':
                hero.inventory.clear(self.target.obj, self.target.count)
            hero.quests.remove(self)
            return True
        return False

    def text(self):
        return str(self.target)

    def copy(self):
        return Quest(self.name, self.target.copy(), self.reward, self.owner)


class Target:
    def __init__(self, typ: str, obj, count: int):
        """Конструктор Цели для квеста

        :param typ: Тип цели(collect, kill)
        :param obj: Обьект для достижения цели (Item, enemy_name)
        :param count: Кол-во обьектов для достижения цели
        """
        self.typ = typ
        self.obj = obj
        self.count = int(count)

    def check_done(self, hero):
        """Проверка на выполнение квеста"""
        if self.typ == 'collect':
            if hero.inventory.itemsList().count(self.obj) >= self.count:
                return True
        elif self.typ == 'kill':
            if hero.kills_counter.get(self.obj, 0) >= self.count:
                return True
        return False

    def copy(self):
        return Target(self.typ, self.obj, self.count)

    def __str__(self):
        s = ''
        if self.typ == 'collect':
            s += f'Собери {self.count} {self.obj}'
        elif self.typ == 'kill':
            s += f'Убей {self.count} {self.obj}'
        return s


class Fight:
    def __init__(self, attacker, target):
        """Конструктор класса Сражение

        :param attacker: Атакующий, начавший атаку
        :param target: Цель, подвергшийся атаке
        """
        self.attacker = attacker
        self.target = target
        self.attacker_turn = True
        self.lasttime = datetime.datetime.now()
        self.journal = ''

    def _turn(self):
        """Выполнение хода
        :return: damage_turn"""
        a_stats = self.attacker.getFightStats()
        t_stats = self.target.getFightStats()
        if self.attacker_turn:
            self.target.health -= max([0, a_stats['damage'] - t_stats['armor']])
        else:
            self.attacker.health -= max([0, t_stats['damage'] - a_stats['armor']])

        return max([0, a_stats['damage'] - t_stats['armor']]) if self.attacker_turn else \
            max([0, t_stats['damage'] - a_stats['armor']])

    def _end(self):
        winner = self.attacker if self.target.health <= 0 else self.target if self.attacker.health <= 0 else None
        loser = self.target if self.target.health <= 0 else self.attacker if self.attacker.health <= 0 else None
        if winner:
            items = []
            for item in loser.inventory.itemsList(without_none=True) + loser.equipment.itemsList(without_none=True):
                if item.drop_chance in list(map(lambda i: i / 100.0,
                                                range(int(round(random.random(), 2) * 100), 100))):
                    items.append(item)
            winner.inventory.append(items)
            winner.curr_fight = None
            loser.curr_fight = None

    def next(self):
        """Следующий шаг

        :return: Позицию и текст для рендера
        """
        dmg = self._turn()
        if self.attacker.health < 1:
            self._end()
            self.attacker.onDeath(self.target)
            self.attacker.onDeath(None)
        elif self.target.health < 1:
            self._end()
            self.target.onDeath(self.attacker)
            self.target.onDeath(None)
        self.attacker_turn = not self.attacker_turn
        if self.attacker_turn:
            x, y = self.attacker.onWindowPos()
            self.journal += f'{self.target.name} бьет {self.attacker.name} на {dmg}HP\n'
        else:
            x, y = self.target.onWindowPos()
            self.journal += f'{self.attacker.name} бьет {self.target.name} на {dmg}HP\n'
        self.journal = '\n'.join(self.journal.split('\n')[:5])
        return x, y, f'-{dmg}HP'


class Dialog:
    def __init__(self, hero, character, text: list):
        self.hero = hero
        self.character = character
        self.text = text
        self.character_say = True  # Очередь говорить
        self.lasttime = datetime.datetime.now()

    def __iter__(self):
        return self

    def __next__(self):
        if self.text:
            t = self.text.pop(0)
            if isinstance(t, list):
                t = t[0]
            t = t.split('$')
            if self.character_say:
                x, y = self.character.onWindowPos()
            else:
                x, y = self.hero.onWindowPos()
            self.character_say = not self.character_say
            y -= BLOCK_SIZE // 2 * len(t)
            return x, y, t


# --- Данные
locations_list: dict = {
    'болото': {
        'minx': -WIDTH,
        'miny': -HEIGHT,
        'maxx': WIDTH * 10,
        'maxy': HEIGHT * 10,
        'basic_blocks_spritename': 'grass',
        'structures': {
            'House': 20
        },
        'cities': [
            'Middletown'
        ]
    },
    'горы': {
        'minx': WIDTH * 10,
        'miny': -HEIGHT,
        'maxx': WIDTH * 20,
        'maxy': HEIGHT * 10,
        'basic_blocks_spritename': 'mountain',
        'structures': {
            'Holy ruins': 10
        },
        'cities': ['Hightown']
    },
    'пустыня': {
        'minx': -WIDTH,
        'miny': HEIGHT * 10,
        'maxx': WIDTH * 20,
        'maxy': HEIGHT * 20,
        'basic_blocks_spritename': 'sand',
        'structures': {
            'Ruins': 30
        },
        'cities': ["Первый поселок", "Вторчинск", "Третьяковка"]
    }
}
# MAP VIEW
# ББББГГГГ
# ББББГГГГ
# ББББГГГГ
# ПППППППП
# ПППППППП
# ПППППППП

structures_list = {
    'House': {
        'location_name': 'болото',
        'color': (RED,),
        'npcs': 1
    },
    'Holy ruins': {
        'location_name': 'горы',
        'color': (STONE,)
    },
    'Ruins': {
        'location_name': 'пустыня',
        'color': (RED,)
    },
    'Sand house': {
        'location_name': 'пустыня',
        'color': (RED,),
        'npcs': 1
    }
}
structure_items_list = {
    'House': [
        (3, Item.getItem('золото')),
        (1, Item.getItem('стеклянный меч')),
        (5, Item.getItem('кости')),
        (5, Item.getItem('кирпич пыли')),
        (3, Item.getItem('Топорик'))
    ],
    'Holy ruins': [
        (1, Item.getItem('Белое золото')),
        (3, Item.getItem('Церковная ткань')),
        (5, Item.getItem('Камень')),
        (4, Item.getItem('кости'))
    ],
    'Ruins': [
        (1, Item.getItem('золото')),
        (4, Item.getItem('Красивый камень')),
        (3, Item.getItem('Металлолом')),
        (4, Item.getItem('кости'))
    ],
    'Sand house': []
}  # Вид (weight(для random.choices), Item)

npcs_list = {
    'trader': {
        'loc_name': 'болото',
        'sell_items': [
            Item.getItem('Кожаная куртка'),
            Item.getItem('Булава'),
            Item.getItem('Топорик'),
            Item.getItem('Ботинки')
        ]
    },
    'Странствующий торговец': {
        'loc_name': 'пустыня',
        'sell_items': [
            Item.getItem('Ткань'),
            Item.getItem('Стеклянный меч'),
            Item.getItem('Штаны'),
            Item.getItem('Ботинки')
        ]
    },
    'quester': {
        'loc_name': 'болото',
        'quests': [
            Quest(*Handler.get_quest('А', init=False)),
            Quest(*Handler.get_quest('Б', init=False))
        ]
    }
}
enemy_list = {
    'Монстр': {
        'loc_name': 'болото',
        'inventory': [
            'шняга'
        ],
        'equipment': [
            'Кулак',
            'Рваная футболка'
        ]
    },
    'Защитник гор': {
        'loc_name': 'горы',
        'inventory': [
            'шняга'
        ],
        'equipment': [
            'Доспехи(штаны)',
            'Доспехи(тело)',
            'Булава'
        ]
    },
    'Обезумевший': {
        'loc_name': 'пустыня',
        'inventory': [
            'шняга'
        ],
        'equipment': [
            'Ткань'
        ]
    }
}