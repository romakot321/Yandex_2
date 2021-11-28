from config import *
import pygame
from datetime import datetime
from random import choice
from item import Inventory


class Character(pygame.sprite.Sprite):
    ACTIONS = (right, down)  # кортеж действий, хранящий функции(из config)

    def __init__(self):
        """Конструктор класса Герой

        :param velocity: Param for camera
        :param is_moving: Может ли герой идти
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 40))
        self.image.fill(DARK_RED)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.velocity = pygame.math.Vector2(0, 0)
        self.lasttime = datetime.now()
        self.is_moving = True
        self.inventory = Inventory(self, 6)
        self.equipment = Inventory(self, 5, ('head', 'body', 'legs', 'boots', 'hands'))

    def update(self):
        if (datetime.now() - self.lasttime).seconds > 0.5 and self.is_moving:
            # Совершение случайного действия раз в 3 секунды
            self.lasttime = datetime.now()
            choice(self.ACTIONS)(self.velocity, self.rect)
