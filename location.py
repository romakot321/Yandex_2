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
            for y in range(CHUNK_SIZE, HEIGHT, CHUNK_SIZE):
                for x in range(CHUNK_SIZE, WIDTH, CHUNK_SIZE):
                    self.blocks_sprites.add(Block(x, y))
            Handler.save_locations_params(**self.__dict__)


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((CHUNK_SIZE, CHUNK_SIZE))
        self.image.fill(DARK_GREEN if randint(0, 1) == 1 else FOREST_GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)