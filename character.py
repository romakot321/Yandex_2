from config import *
import pygame
from datetime import datetime
from random import choice
from item import Inventory


class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, color=SKINCOLOR):
        """Конструктор класса персонаж. Персонаж это НПС, враг и герой"""
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 40))
        self.image.fill(SKINCOLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.health = 100
        self.inventory = Inventory(self, 3)  # У каждого персонажа есть инвентарь


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
        self.equipment = Inventory(self, 5, ('head', 'body', 'legs', 'boots', 'hands'))

        self.kills_counter = {}

    def update(self):
        if (datetime.now() - self.lasttime).seconds > 0.5 and self.is_moving:
            # Совершение случайного действия раз в 3 секунды
            self.lasttime = datetime.now()
            choice(self.ACTIONS)(self.velocity, self.rect)


class NPC(Character):
    def __init__(self, x, y, loc, structure=None):
        """Конструктор класса НПС(мирный)

        :param loc: Прикрепление к локации
        :param structure: Прикрепление к структуре(необяз)
        """
        Character.__init__(self, x, y)
        self.loc = loc
        self.structure = structure
        self.quests = []
        self.sell_items = []
        # TODO Диалог с героем для квестов и торговли


class Enemy(Character):
    def __init__(self, x, y, name, loc, structure=None):
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

    def death(self, killer):
        if isinstance(killer, Hero):
            killer.kills_counter[self.name] = killer.kills_counter.get(self.name, 0) + 1