from config import *
import pygame
from datetime import datetime
from random import choice
from item import Inventory
from typing import Tuple, List, Set


class Character(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, color: Tuple[int, int, int] = SKINCOLOR):
        """Конструктор класса персонаж. Персонаж это НПС, враг и герой"""
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.health = 100
        self.inventory = Inventory(self, 3)  # У каждого персонажа есть инвентарь

    def onDeath(self, *args, **kwargs):
        pass

    def fullDescription(self):
        return f'{self.health}'

    def getFightStats(self): pass

    def onWindowPos(self):
        return self.rect.topleft - Hero.hero_object.velocity + (0, 25)

    def __str__(self):
        return f'{self.health}'


class Hero(Character):
    ACTIONS = (right, down, left, up)  # кортеж действий, хранящий функции(из config)
    hero_object: 'Hero' = None

    def __init__(self):
        """Конструктор класса Герой

        :param velocity: Param for camera
        :param is_moving: Может ли герой идти
        """
        Character.__init__(self, WIDTH // 2, HEIGHT // 2, DARK_RED)
        self.name = 'Герой'
        self.velocity = pygame.math.Vector2(0, 0)
        self.lasttime = datetime.now()
        self.is_moving = True
        self.equipment = Inventory(self, 5, ('head', 'body', 'legs', 
                                             'boots', 'hands'))
        self.inventory = Inventory(self, 6, linked_inv=self.equipment)

        self.kills_counter = {}
        self.curr_fight = None
        Hero.hero_object = self

    def update(self):
        if (datetime.now() - self.lasttime).seconds > 0.5 and self.is_moving and self.curr_fight is None:
            # Совершение случайного действия раз в 3 секунды
            self.lasttime = datetime.now()
            choice(self.ACTIONS)(self.velocity, self.rect)

    def add_velocity(self, value: tuple):
        self.velocity += value
    
    def set_velocity(self, *args):
        if isinstance(args[0], tuple):
            value = args[0]
        else:
            value = args
        assert len(value) == 2
        self.velocity = pygame.math.Vector2(value)

    def getFightStats(self):
        stats = {}
        for i in [i for i in self.equipment.itemsList() if i is not None]:
            for stat, value in i.stats.items():
                stats[stat] = stats.get(stat, 0) + value
        return {'damage': stats.get('damage', 0), 'armor': stats.get('armor', 0)}

    def onWindowPos(self):
        return self.rect.topleft

    def onDeath(self, *args):
        self.velocity = pygame.math.Vector2(0, 0)
        self.rect.center = (WIDTH // 2, HEIGHT // 2)


class NPC(Character):
    ACTIONS = (up, left, right, down)

    def __init__(self, x: int, y: int, name: str, loc, structure=None):
        """Конструктор класса НПС(мирный)

        :param loc: Прикрепление к локации
        :param structure: Прикрепление к структуре(необяз)
        """
        Character.__init__(self, x, y, SKINCOLOR)
        self.loc = loc
        self.name = name
        self.structure = structure
        self.quests = []
        self.sell_items = []
        self.lasttime = datetime.now()
        self.loc.characters.append(self)
        # TODO Диалог с героем для квестов и торговли

    def update(self):
        if (datetime.now() - self.lasttime).seconds > 0.5:
            self.lasttime = datetime.now()
            if self.structure:
                choice(self.ACTIONS)(self.rect, None,
                                     (self.structure.x - BLOCK_SIZE * 4, self.structure.y - BLOCK_SIZE * 4),
                                     (self.structure.x + BLOCK_SIZE * 4, self.structure.y + BLOCK_SIZE * 4))
            else:
                choice(self.ACTIONS)(self.rect, None,
                                     (self.loc.minx, self.loc.miny),
                                     (self.loc.maxx, self.loc.maxy))

    def fullDescription(self):
        s = f'Имя: {self.name}\nТип: NPC\n{"Есть квесты" if self.quests else ""}\n'
        s += f'{"Есть предметы на продажу" if self.sell_items else ""}'
        return s

    def __str__(self):
        return f'{self.name}(HP: {self.health})'


class Enemy(Character):
    ACTIONS = (up, left, right, down)

    def __init__(self, x: int, y: int, name: str, loc, structure=None):
        """Конструктор класса Враг

        :param loc: Прикрепление к локации
        :param structure: Прикрепление к структуре(необяз)
        """
        Character.__init__(self, x, y)
        self.loc = loc
        self.name = name
        self.structure = structure
        self.equipment = Inventory(self, 5, ('head', 'body', 'legs', 'boots', 'hands'))
        self.inventory = Inventory(self, 3, linked_inv=self.equipment)
        self.lasttime = datetime.now()
        self.loc.characters.append(self)

        self.curr_fight = None

    def onDeath(self, killer):
        if isinstance(killer, Hero):
            killer.kills_counter[self.name] = killer.kills_counter.get(self.name, 0) + 1
        try:
            self.loc.characters.remove(self)
        except ValueError:
            pass
        del self

    def update(self):
        if (datetime.now() - self.lasttime).seconds > 3 and self.curr_fight is None:
            self.lasttime = datetime.now()
            if self.structure:
                choice(self.ACTIONS)(self.rect, None,
                                     (self.structure.x - BLOCK_SIZE * 4, self.structure.y - BLOCK_SIZE * 4),
                                     (self.structure.x + BLOCK_SIZE * 4, self.structure.y + BLOCK_SIZE * 4))
            else:
                choice(self.ACTIONS)(self.rect, None,
                                     (self.loc.minx, self.loc.miny),
                                     (self.loc.maxx, self.loc.maxy))
            # --- Проверка на коллизию с героем
            if self.rect.collidepoint(Hero.hero_object.velocity.x + WIDTH // 2,
                                      Hero.hero_object.velocity.y + (HEIGHT // 2 - 25)):
                if Hero.hero_object.curr_fight is None \
                        and self.curr_fight is None:  # Создание сражения
                    Hero.hero_object.curr_fight = Fight(self, Hero.hero_object)
                    self.curr_fight = Hero.hero_object.curr_fight
                    right(Hero.hero_object.velocity, Hero.hero_object.rect)

    def getFightStats(self):
        stats = {}
        for i in [i for i in self.equipment.itemsList() if i is not None]:
            for stat, value in i.stats.items():
                stats[stat] = stats.get(stat, 0) + value
        return {'damage': stats.get('damage', 0), 'armor': stats.get('armor', 0)}

    def fullDescription(self):
        s = f'Имя: {self.name}\nТип: Enemy\n{str(self.equipment)}'
        return s

    def __str__(self):
        return f'{self.name}(HP: {self.health})'