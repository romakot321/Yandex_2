from config import *
import pygame
from datetime import datetime
from random import choice
from item import Inventory
from typing import Tuple, List, Set


class Character(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]=SKINCOLOR):
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

    def __str__(self):
        return f'{self.health}'


class Hero(Character):
    ACTIONS = (up, left, right, down)  # кортеж действий, хранящий функции(из config)

    def __init__(self):
        """Конструктор класса Герой

        :param velocity: Param for camera
        :param is_moving: Может ли герой идти
        """
        Character.__init__(self, WIDTH // 2, HEIGHT // 2, DARK_RED)
        self.velocity = pygame.math.Vector2(0, 0)
        self.lasttime = datetime.now()
        self.is_moving = True
        self.inventory = Inventory(self, 6)
        self.equipment = Inventory(self, 5, ('head', 'body', 'legs', 
                                             'boots', 'hands'))

        self.kills_counter = {}

    def update(self):
        if (datetime.now() - self.lasttime).seconds > 0.5 and self.is_moving:
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
        # TODO Система боя с героем (получение характеристик)

    def onDeath(self, killer):
        if isinstance(killer, Hero):
            killer.kills_counter[self.name] = killer.kills_counter.get(self.name, 0) + 1
