from config import *
import pygame
from datetime import datetime
from random import choice


class Character(pygame.sprite.Sprite):
    ACTIONS = (up, right, left, down)  # кортеж действий, хранящий функции(из config)

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 40))
        self.image.fill(DARK_RED)
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300)
        self.lasttime = datetime.now()

    def update(self):
        if (datetime.now() - self.lasttime).seconds > 3:  # Совершение случайного действия раз в 3 секунды
            self.lasttime = datetime.now()
            choice(Character.ACTIONS)(self.rect)