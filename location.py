from DBHandler import Handler
import pygame
from config import *
from random import randint, choices
from typing import List
from character import Character
from item import Inventory, Item


class Location:
    locations_objects: List['Location'] = []

    def __init__(self, name, minx=0, miny=0, maxx=0, maxy=0,
                 basic_blocks_color=(DARK_GREEN, FOREST_GREEN)):
        if Handler.get_locations_params(name) is not None:  # Если такая локация существует...
            for param_name, val in Handler.get_locations_params(name):
                self.__dict__[param_name] = val
        else:
            self.maxx, self.maxy = maxx, maxy
            self.minx, self.miny = minx, miny
            self.name = name
            self.characters: List['Character'] = []
            self.structures_list = []
            self.blocks_sprites = pygame.sprite.Group()
            for y in range(miny, maxy, BLOCK_SIZE):
                for x in range(minx, maxx, BLOCK_SIZE):
                    if (x, y) in [(i['x'], i['y']) for i in structures_list.values()]:
                        name, color = \
                            [(i, j['color']) for i, j in structures_list.items() if (j['x'], j['y']) == (x, y)][0]
                        s = Structure(x, y, name, color)
                        self.structures_list.append(s)
                        self.blocks_sprites.add(s)
                        continue
                    else:
                        self.blocks_sprites.add(Block(x, y, colors=basic_blocks_color))
            Handler.save_locations_params(**self.__dict__)
        Location.locations_objects.append(self)

    @staticmethod
    def get_location(*coords) -> 'Location':
        loc = None
        for lc in Location.locations_objects:
            if coords[0] in range(lc.minx, lc.maxx + 1) and coords[1] in range(lc.miny, lc.maxy + 1):
                loc = lc
        return loc

    @staticmethod
    def getSpritesToDraw(chr_coords) -> list:
        """Получение списка спрайтов для отрисовки по координатам камеры

        :param chr_coords: Character.velocity
        """
        if isinstance(chr_coords, pygame.math.Vector2):
            chr_coords = (chr_coords.x, chr_coords.y)
        loc = Location.get_location(chr_coords[0], chr_coords[1])
        x, y = int(chr_coords[0]), int(chr_coords[1])
        ret = []
        if loc is not None:
            sprites = list(loc.blocks_sprites)
            if x + WIDTH > loc.maxx:
                sprites = sprites + list(Location.get_location(x + 2 * WIDTH,
                                                               y).blocks_sprites)
            if y + HEIGHT + 25 > loc.maxy:
                sprites = sprites + list(Location.get_location(x,
                                                               y + 2 * HEIGHT).blocks_sprites)
            for s in sprites:
                if s.rect.x in range(x - WIDTH, x + WIDTH) \
                        and s.rect.y in range(y - BLOCK_SIZE,
                                              y + HEIGHT):
                    ret.append(s)
        return ret


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, colors=()):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.fill(colors[randint(0, len(colors) - 1)])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Structure(Block):
    def __init__(self, x, y, name, colors=(BLUE, RED)):
        super().__init__(x, y, colors=colors)
        self.x, self.y = x, y
        self.name = name
        weights = [w for w, _ in structure_items_list]
        items = [i for _, i in structure_items_list]
        self.inventory = Inventory(self, 3, slots_items=choices(items, weights=weights, k=3))


class City(Block):
    def __init__(self, x, y, name):
        super().__init__(x, y, (BROWN,))
        self.x, self.y = x, y
        self.name = name