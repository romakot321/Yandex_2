# --- Константы
import datetime
import random
from typing import List, Union

import pygame

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
            elif self.target.typ == 'kill':
                hero.kills_counter[self.target.obj] = 0
            hero.quests.remove(self)
            return True
        return False

    def progress(self, hero) -> int:
        if self.target.typ == 'collect':
            return int(hero.inventory.itemsList().count(self.target.obj) / self.target.count * 100)
        elif self.target.typ == 'kill':
            return int(hero.kills_counter.get(self.target.obj, 0) / self.target.count * 100)
        elif self.target.typ == 'sell':
            return int(self.target.sell_count / self.target.count * 100)

    def text(self):
        return str(self.target)

    def copy(self):
        return Quest(self.name, self.target.copy(), self.reward, self.owner)


class Target:
    def __init__(self, typ: str, obj, count: int):
        """Конструктор Цели для квеста

        :param typ: Тип цели(collect, kill, sell)
        :param obj: Обьект для достижения цели (Item, enemy_name)
        :param count: Кол-во обьектов для достижения цели
        """
        self.typ = typ
        self.obj = obj
        self.count = int(count)
        if self.typ == 'sell':
            self.sell_count = 0

    def check_done(self, hero):
        """Проверка на выполнение квеста"""
        if self.typ == 'collect':
            return hero.inventory.itemsList().count(self.obj) >= self.count
        elif self.typ == 'kill':
            return hero.kills_counter.get(self.obj, 0) >= self.count
        elif self.typ == 'sell':
            return self.sell_count >= self.count

    def copy(self):
        return Target(self.typ, self.obj, self.count)

    def __str__(self):
        s = ''
        if self.typ == 'collect':
            s += f'Собери {self.count} {self.obj}'
        elif self.typ == 'kill':
            s += f'Убей {self.count} {self.obj}'
        elif self.typ == 'sell':
            s += f'Продай {self.count} {self.obj}'
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
            dmg = max([0, a_stats['damage'] - t_stats['armor'] + random.randint(-int(0.5 * a_stats['damage']),
                                                                                int(0.5 * a_stats['damage']))])
            self.target.health -= dmg
        else:
            dmg = max([0, t_stats['damage'] - a_stats['armor'] + random.randint(-int(0.5 * t_stats['damage']),
                                                                                int(0.5 * t_stats['damage']))])
            self.attacker.health -= dmg

        return dmg

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
        if 0.3 < round(random.random(), 1) < 0.5:
            if self.attacker.name == 'Герой' and self.attacker.health < 30:
                self.target.onDeath(None)
                self.target.onDeath(None)
                self.attacker.curr_fight = None
                self.target.curr_fight = None
            elif self.target.name == 'Герой' and self.target.health < 30:
                self.attacker.onDeath(None)
                self.attacker.onDeath(None)
                self.attacker.curr_fight = None
                self.target.curr_fight = None

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


class Tendency:
    def __init__(self, name, typ: str, info: str):
        self.name = name
        self.type = typ
        if self.type == 'funcs':
            info = info.split()
            self.info = (info[0], float(info[1]))
        elif self.type == 'decision':
            info = info.split()
            if info[0] == 'like_item':
                self.info = (info[0],)

    def text(self):
        if self.type == 'decision':
            if self.info[0] == 'like_item':
                return self.name + ' ' + self.info[1].name
        return self.name


# --- Данные
locations_list: dict = {
    'болото': {
        'minx': -WIDTH,
        'miny': -HEIGHT,
        'maxx': WIDTH * 10,
        'maxy': HEIGHT * 10,
        'basic_blocks_spritename': 'grass',
        'structures': {
            'House': 10
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
            'Ruins': 30,
            'Sand house': 20
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
    'Торговец': {
        'loc_name': 'болото',
        'sell_items': [
            Item.getItem('Кожаная куртка'),
            Item.getItem('Булава'),
            Item.getItem('Топорик'),
            Item.getItem('Ботинки')
        ],
        'image_name': 'sprites/npc.png'
    },
    'Странствующий торговец': {
        'loc_name': 'пустыня',
        'sell_items': [
            Item.getItem('Ткань'),
            Item.getItem('Стеклянный меч'),
            Item.getItem('Штаны'),
            Item.getItem('Ботинки')
        ],
        'image_name': 'sprites/npc.png'
    },
    'Работодатель': {
        'loc_name': 'болото',
        'quests': [
            'А',
            'Б',
            'Продать'
        ],
        'image_name': 'sprites/npc.png'
    },
    'Оружейник': {
        'loc_name': 'болото',
        'sell_items': [Item.getItem('улучшение')],
        'image_name': 'sprites/npc.png'
    },
    'Трейдер': {
        'loc_name': 'пустыня',
        'sell_items': [
            Item.getItem('улучшение'),
            Item.getItem('заклятая кольчуга'),
            Item.getItem('глубинный меч')
        ],
        'image_name': 'sprites/epic_npc.png'
    }
}
enemy_list = {
    'Монстр': {
        'loc_name': 'болото',
        'image_name': 'sprites/swamp_enemy2.png',
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
        'image_name': 'sprites/mountain_enemy2.png',
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
        'image_name': 'sprites/desert_enemy1.png',
        'inventory': [
            'шняга'
        ],
        'equipment': [
            'Ткань'
        ]
    }
}

pygame.display.init()
pygame.display.set_mode((WIDTH, HEIGHT))

images = {
    'house': [(3, pygame.image.load('sprites/structure1.png').convert())],
    'holy ruins': [(3, pygame.image.load('sprites/structure1.png').convert())],
    'ruins': [(3, pygame.image.load('sprites/sand_structure.png').convert())],
    'grass': [
        (3, pygame.image.load('sprites/grass1.png').convert()),
        (3, pygame.image.load('sprites/grass2.png').convert()),
        (3, pygame.image.load('sprites/grass3.png').convert()),
        (2, pygame.image.load('sprites/grass_blue.png').convert()),
        (2, pygame.image.load('sprites/grass_yellow.png').convert()),
        (0.1, pygame.image.load('sprites/grass_rock.png').convert())
    ],
    'mountain': [
        (3, pygame.image.load('sprites/mountain1.png').convert()),
        (3, pygame.image.load('sprites/mountain2.png').convert()),
        (3, pygame.image.load('sprites/mountain3.png').convert()),
        (0.1, pygame.image.load('sprites/mountain_rock1.png').convert()),
        (0.1, pygame.image.load('sprites/mountain_rock2.png').convert())
    ],
    'sand': [
        (1, pygame.image.load('sprites/sand1.png').convert()),
        (3, pygame.image.load('sprites/sand2.png').convert()),
        (3, pygame.image.load('sprites/sand3.png').convert()),
        (0.07, pygame.image.load('sprites/sand_cactus1.png').convert()),
        (0.06, pygame.image.load('sprites/sand_cactus2.png').convert())
    ]
}
basic_image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
basic_image.fill(RED)