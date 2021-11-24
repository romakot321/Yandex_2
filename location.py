from DBHandler import Handler
import pygame
from config import *
from random import randint


class Location:
    def __init__(self, name):
        if Handler.get_locations_params(name) is not None:  # Если такая локация существует...
            for param_name, val in Handler.get_locations_params(name):
                self.__dict__[param_name] = val
        else:
            self.name = name
            self.characters = []
            self.blocks_sprites = pygame.sprite.Group()
            for y in range(0, HEIGHT * 2, BLOCK_SIZE):
                for x in range(0, WIDTH * 2, BLOCK_SIZE):
                    self.blocks_sprites.add(Block(x, y))
            Handler.save_locations_params(**self.__dict__)


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.fill(DARK_GREEN if randint(0, 1) == 1 else FOREST_GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Structure(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.fill(DARK_GREEN if randint(0, 1) == 1 else FOREST_GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
