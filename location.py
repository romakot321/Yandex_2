from DBHandler import Handler
import pygame
from config import *
from random import choices, random, randrange, choice, randint
from typing import List
from character import Hero, Enemy, NPC
from item import Inventory, Item

# Для pygame.image.convert (ускорение прорисовки спрайтов)
pygame.display.init()
pygame.display.set_mode((WIDTH, HEIGHT))


class Location:
    locations_objects: List['Location'] = []

    def __init__(self, name, minx=0, miny=0, maxx=0, maxy=0,
                 basic_blocks_spritename=(DARK_GREEN, FOREST_GREEN),
                 structures=None, cities=None, app=None):
        if Handler.get_locations_params(name) is not None:  # Если такая локация существует...
            for param_name, val in Handler.get_locations_params(name):
                self.__dict__[param_name] = val
        else:
            self.maxx, self.maxy = maxx, maxy
            self.minx, self.miny = minx, miny
            self.name = name
            self.characters: List[Union['Hero', 'Enemy', 'NPC']] = []
            self.structures_list = []
            self.blocks_sprites = pygame.sprite.Group()
            sminx, sminy = minx, miny
            if minx < 0:
                sminx = 0
            if miny < 0:
                sminy = 0
            if structures:
                for name, count in structures.items():
                    for _ in range(count):
                        x, y = randrange(sminx, maxx, 50), randrange(sminy, maxy, 50)
                        self.structures_list.append(Structure(x, y, name, name,
                                                              structure_items_list.get(name, None)))
                        if structures_list[name].get('npcs') is not None:
                            for _ in range(structures_list[name]['npcs']):
                                npc = [i for i in npcs_list.keys() if npcs_list[i]['loc_name'] == self.name]
                                npc = choices(npc)[0]
                                self.characters.append(NPC(x, y, npc, self, app, self.structures_list[-1]))
                                self.characters[-1].sell_items = npcs_list[npc].get('sell_items', [])
                                self.characters[-1].quests = npcs_list[npc].get('quests', [])
                                for i in range(len(self.characters[-1].quests)):
                                    self.characters[-1].quests[i] = self.characters[-1].quests[i].copy()
                                    self.characters[-1].quests[i].owner = self.characters[-1]
            if cities:
                for name in cities:
                    x, y = randrange(sminx, maxx, 50), randrange(sminy, maxy, 50)
                    self.structures_list.append(City(x, y, name))
            for y in range(miny, maxy, BLOCK_SIZE):
                for x in range(minx, maxx, BLOCK_SIZE):
                    if (x, y) in [(s.x, s.y) for s in self.structures_list]:
                        s = [s for s in self.structures_list if (x, y) == (s.x, s.y)][0]
                        self.blocks_sprites.add(s)
                        continue
                    else:
                        self.blocks_sprites.add(Block(x, y, image_name=basic_blocks_spritename))
            Handler.save_locations_params(**self.__dict__)
        Location.locations_objects.append(self)

    @staticmethod
    def get_location(*coords, name=None) -> 'Location':
        loc = None
        for lc in Location.locations_objects:
            if coords and coords[0] in range(lc.minx, lc.maxx + 1) \
                    and coords[1] in range(lc.miny, lc.maxy + 1) \
                    or name is not None and lc.name == name:
                loc = lc
        return loc

    @staticmethod
    def getSpritesToUpdate(chr_coords) -> list:
        """Получение списка спрайтов для вызова метода update()

        :param chr_coords: Hero.velocity
        """
        if isinstance(chr_coords, pygame.math.Vector2):
            chr_coords = (chr_coords.x, chr_coords.y)
        x, y = int(chr_coords[0]), int(chr_coords[1])
        loc = Location.get_location(*chr_coords)
        sprites = loc.characters
        ret = []
        if sprites:
            if WIDTH * 18 > x + WIDTH > loc.maxx:
                sprites = sprites + Location.get_location(x + WIDTH, y).characters
            if HEIGHT * 18 > y + HEIGHT > loc.maxy:
                sprites = sprites + Location.get_location(x, y + HEIGHT).characters
            for s in sprites:
                if s.onWorldPos()[0] in range(x - WIDTH, x + WIDTH) \
                        and s.onWorldPos()[1] in range(y - HEIGHT, y + HEIGHT):
                    ret.append(s)
        return ret

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
            if WIDTH * 18 > x + WIDTH > loc.maxx:
                sprites = sprites + list(Location.get_location(x + 2 * WIDTH,
                                                               y).blocks_sprites)
            if HEIGHT * 18 > y + HEIGHT + 25 > loc.maxy:
                sprites = sprites + list(Location.get_location(x,
                                                               y + 2 * HEIGHT).blocks_sprites)
            for s in sprites:
                if s.rect.x in range(x - WIDTH, x + WIDTH) \
                        and s.rect.y in range(y - BLOCK_SIZE,
                                              y + HEIGHT):
                    ret.append(s)
        return ret

    def spawnEnemy(self):
        """Спавн противника с некоторым шансом"""
        if 0.102 < round(random(), 3) < 0.200:
            en = choices([i for i in enemy_list.keys() if enemy_list[i]['loc_name'] == self.name])[0]
            x, y = Hero.hero_object.onWorldPos()
            enemy = Enemy(randrange(x - BLOCK_SIZE * 10, x + BLOCK_SIZE * 10, BLOCK_SIZE),
                          randrange(y - BLOCK_SIZE * 10, y + BLOCK_SIZE * 10, BLOCK_SIZE),
                          en, Location.get_location(name=enemy_list[en]['loc_name']))
            enemy.inventory.append([Item.getItem(i) for i in enemy_list[en].get('equipment', [])])
            enemy.inventory.append([Item.getItem(i) for i in enemy_list[en].get('inventory', [])])
            self.characters.append(enemy)
            return enemy
        return None


class Block(pygame.sprite.Sprite):
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

    def __init__(self, x, y, colors=(), image_name=None):
        pygame.sprite.Sprite.__init__(self)
        self._image_name = image_name
        self.im_index = choices(range(0, len(Block.images[image_name])),
                                weights=[w for w, _ in Block.images[image_name]])[0] \
            if image_name else None
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    @property
    def image(self):
        return self._image_name

    @image.getter
    def image(self):
        if self._image_name is None:
            return Block.basic_image
        return Block.images[self._image_name][self.im_index][1]


class Structure(Block):
    def __init__(self, x: int, y: int, name: str, image_name: str,
                 items_list: list = None):
        super().__init__(x, y, image_name=image_name.lower())
        self.image.set_colorkey((255, 255, 255))
        self.x, self.y = x, y
        self.name = name
        if items_list:
            weights = [w for w, _ in items_list]
            items = [i for _, i in items_list]
            self.inventory = Inventory(self, 3, slots_items=choices(items, weights=weights, k=3))


class City(Block):
    def __init__(self, x, y, name):
        super().__init__(x, y, (BROWN,))
        self.x, self.y = x, y
        self.name = name
