# --- Константы
import datetime
import random
from typing import List

from item import Item

WIDTH = 800
HEIGHT = 650
# нулевые координаты для камеры - WIDTH // 2, HEIGHT // 2 - 25
BLOCK_SIZE = 50
FPS = 15

# --- Цвета
WHITE = (255, 255, 255)
FONT_TEXT = (68, 68, 68)
GRAY = (128, 128, 128)
LIGHT_GRAY = (160, 160, 164)
DARK_GRAY = (41, 59, 51)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (150, 0, 24)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 71, 49)
FOREST_GREEN = (11, 102, 35)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
SAND = (252, 221, 118)
LIGHT_SAND = (255, 236, 139)
DARK_SAND = (214, 165, 4)
SKINCOLOR = (245, 245, 220)

# --- Данные
locations_list: dict = {
    'болото': {
        'minx': -WIDTH,
        'miny': -HEIGHT,
        'maxx': WIDTH * 10,
        'maxy': HEIGHT * 10,
        'basic_blocks_color': (DARK_GREEN, FOREST_GREEN)
    },
    'горы': {
        'minx': WIDTH * 10,
        'miny': -HEIGHT,
        'maxx': WIDTH * 20,
        'maxy': HEIGHT * 10,
        'basic_blocks_color': (GRAY, LIGHT_GRAY, DARK_GRAY)
    },
    'пустыня': {
        'minx': -WIDTH,
        'miny': HEIGHT * 10,
        'maxx': WIDTH * 20,
        'maxy': HEIGHT * 20,
        'basic_blocks_color': (SAND, LIGHT_SAND, DARK_SAND)
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
        'location_name': 'loc1',
        'color': (RED,),
        'x': WIDTH // 2,
        'y': HEIGHT // 2 - 25
    },
    'House2': {
        'location_name': 'loc1',
        'color': (RED,),
        'x': 1000,
        'y': 1000
    },
    'House3': {
        'location_name': 'loc1',
        'color': (RED,),
        'x': 1200,
        'y': 1000
    },
    'House4': {
        'location_name': 'loc1',
        'color': (RED,),
        'x': 1400,
        'y': 1000
    },
    'House5': {
        'location_name': 'loc1',
        'color': (RED,),
        'x': 1600,
        'y': 1000
    },
    'House21': {
        'location_name': 'loc1',
        'color': (RED,),
        'x': 1000,
        'y': 1100
    },
    'House31': {
        'location_name': 'loc1',
        'color': (RED,),
        'x': 1200,
        'y': 1100
    },
    'House41': {
        'location_name': 'loc1',
        'color': (RED,),
        'x': 1400,
        'y': 1100
    },
    'House51': {
        'location_name': 'loc1',
        'color': (RED,),
        'x': 1600,
        'y': 1100
    },
    'House6': {
        'location_name': 'болото',
        'color': (RED,),
        'x': 3000,
        'y': 800
    }
}
structure_items_list = [
    (10, Item('золото', price=10)),
    (1, Item('стеклянный меч', 'equipment', 'hands', damage=15, drop_chance=0.1, price=50)),
    (5, Item('кости', price=1)),
    (5, Item('кирпич пыли')),
    (3, Item('Топорик', 'equipment', 'hands', damage=5, drop_chance=0.9, price=10))
]  # Вид (weight(для random.choices), Item)
equipment_items_list = [
    Item('Кожаная куртка', 'equipment', 'body', armor=2, drop_chance=0.8, price=5),
    Item('Ботинки', 'equipment', 'boots', armor=1, drop_chance=0.8, price=2),
    Item('Штаны', 'equipment', 'legs', armor=1, drop_chance=0.8, price=3),
    Item('Бита', 'equipment', 'hands', damage=4, drop_chance=0.7, price=2)
]
epic_items_list = [
    Item('Ban hammer', 'equipment', 'hands', damage=100)
]
drop_items_list = [
    Item('кости', price=1)
]


# --- Вспомогательные классы
class Quest:
    def __init__(self, name, target: 'Target', owner, reward: List['Item']):
        """Конструктор Квеста

        :param name: Название
        :param target: Цель для завершения квеста
        :param owner: Тот, кто выдал квест
        :param reward: Вознаграждение за выполнение
        """
        self.name = name
        self.target = target
        self.owner = owner
        self.reward = reward

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


class Target:
    def __init__(self, typ: str, obj, count: int):
        """Конструктор Цели для квеста

        :param typ: Тип цели(collect, kill)
        :param obj: Обьект для достижения цели (Item, Enemy)
        :param count: Кол-во обьектов для достижения цели
        """
        self.typ = typ
        self.obj = obj
        self.count = count

    def check_done(self, hero):
        """Проверка на выполнение квеста"""
        if self.typ == 'collect':
            if hero.inventory.itemsList().count(self.obj) >= self.count:
                return True
        elif self.typ == 'kill':
            if hero.kills_counter.get(self.obj.name, 0) >= self.count:
                return True
        return False

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
        elif self.target.health < 1:
            self._end()
            self.target.onDeath(self.attacker)
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