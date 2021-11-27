from DBHandler import Handler
import pygame
from config import *
from random import randint
from typing import List


class Location:
    locations_objects: List['Location'] = []

    def __init__(self, name, minx=0, miny=0, maxx=0, maxy=0):
        if Handler.get_locations_params(name) is not None:  # Если такая локация существует...
            for param_name, val in Handler.get_locations_params(name):
                self.__dict__[param_name] = val
        else:
            self.maxx, self.maxy = maxx, maxy
            self.minx, self.miny = minx, miny
            self.name = name
            self.characters = []
            self.structures_list = []
            self.blocks_sprites = pygame.sprite.Group()
            for y in range(0, maxy, BLOCK_SIZE):
                for x in range(0, maxx, BLOCK_SIZE):
                    if (x, y) in [(i['x'], i['y']) for i in structures_list.values()]:
                        s = Structure(x, y,
                                      [i for i, j in structures_list.items() if (j['x'], j['y']) == (x, y)][0])
                        self.structures_list.append(s)
                        self.blocks_sprites.add(s)
                        continue
                    else:
                        self.blocks_sprites.add(Block(x, y))
            Handler.save_locations_params(**self.__dict__)
        Location.locations_objects.append(self)

    @staticmethod
    def get_location(*coords) -> 'Location':
        for loc in Location.locations_objects:
            if coords[0] in range(loc.minx, loc.maxx + 1) and coords[1] in range(loc.miny, loc.maxy + 1):
                return loc
        return None


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
        self.image.fill(BLUE if randint(0, 1) == 1 else RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x, self.y = x, y
        self.name = name