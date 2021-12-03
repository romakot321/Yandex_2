# --- Константы
import random
from item import Item

WIDTH = 800
HEIGHT = 650
# нулевые координаты для камеры - WIDTH // 2, HEIGHT // 2 - 25
BLOCK_SIZE = 50
FPS = 15

# --- Цвета
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (160, 160, 164)
DARK_GRAY = (41, 59, 51)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (150, 0, 24)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 71, 49)
FOREST_GREEN = (11, 102, 35)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
SAND = (252, 221, 118)
LIGHT_SAND = (255, 236, 139)
DARK_SAND = (214, 165, 4)
SKINCOLOR = (245, 245, 220)

# --- Данные
locations_list: dict = {
    'болото': {
        'minx': -WIDTH,
        'miny': -HEIGHT,
        'maxx': WIDTH * 10,
        'maxy': HEIGHT * 10,
        'basic_blocks_color': (DARK_GREEN, FOREST_GREEN)
    },
    'горы': {
        'minx': WIDTH * 10,
        'miny': -HEIGHT,
        'maxx': WIDTH * 20,
        'maxy': HEIGHT * 10,
        'basic_blocks_color': (GRAY, LIGHT_GRAY, DARK_GRAY)
    },
    'пустыня': {
        'minx': -WIDTH,
        'miny': HEIGHT * 10,
        'maxx': WIDTH * 20,
        'maxy': HEIGHT * 20,
        'basic_blocks_color': (SAND, LIGHT_SAND, DARK_SAND)
    }
}
# MAP VIEW
# ББББГГГГ
# ББББГГГГ
# ББББГГГГ
# ПППППППП
# ПППППППП
# ПППППППП

structures_list = {
    # 'House': {
    #     'location_name': 'loc1',
    #     'color': (RED,),
    #     'x': random.randrange(100, 500, 50),
    #     'y': random.randrange(100, 200, 50)
    # },
    # 'House2': {
    #     'location_name': 'loc1',
    #     'color': (RED,),
    #     'x': random.randrange(100, 500, 50),
    #     'y': random.randrange(100, 400, 50)
    # },
    # 'House3': {
    #     'location_name': 'loc1',
    #     'color': (RED,),
    #     'x': WIDTH,
    #     'y': HEIGHT // 2 - 25
    # },
    'House4': {
        'location_name': 'loc1',
        'color': (RED,),
        'x': WIDTH // 2,
        'y': HEIGHT // 2 - 25
    }
}
structure_items_list = [
    (3, Item('золото')),
    (1, Item('стеклянный меч', 'equipment', 'hands')),
    (5, Item('кости'))
]  # Вид (weight(для random.choices), Item)


# --- Вспомогательные функции
def up(velocity, rect, mincoords=(0, 0), maxcoords=(WIDTH * 20, HEIGHT * 20)):
    if velocity.y - BLOCK_SIZE >= mincoords[1]:
        velocity.y -= BLOCK_SIZE
    else:
        if rect is not None and rect.centery - BLOCK_SIZE >= 0:
            rect.centery -= BLOCK_SIZE


def down(velocity, rect, mincoords=(0, 0), maxcoords=(WIDTH * 20, HEIGHT * 20)):
    if velocity.y + BLOCK_SIZE <= maxcoords[1]:
        if rect is None or rect.centery == HEIGHT // 2:
            velocity.y += BLOCK_SIZE
    else:
        if rect is not None and rect.centery + BLOCK_SIZE <= HEIGHT // 2:
            rect.centery += BLOCK_SIZE


def left(velocity, rect, mincoords=(0, 0), maxcoords=(WIDTH * 20, HEIGHT * 20)):
    if velocity.x - BLOCK_SIZE >= mincoords[0]:
        velocity.x -= BLOCK_SIZE
    else:
        if rect is not None and rect.centerx - BLOCK_SIZE >= 0:
            rect.centerx -= BLOCK_SIZE


def right(velocity, rect, mincoords=(0, 0), maxcoords=(WIDTH * 20, HEIGHT * 20)):
    if velocity.x + BLOCK_SIZE <= maxcoords[0]:
        if rect is None or rect.centerx == WIDTH // 2:
            velocity.x += BLOCK_SIZE
    else:
        if rect is not None and rect.centerx + BLOCK_SIZE <= WIDTH // 2:
            rect.centerx += BLOCK_SIZE


# --- Вспомогательные классы
class Quest:
    def __init__(self, name, target: 'Target', owner):
        """Конструктор Квеста

        :param name: Название
        :param target: Цель для завершения квеста
        :param owner: Тот, кто выдал квест
        """
        self.name = name
        self.target = target
        self.owner = owner


class Target:
    def __init__(self, typ: str, obj, count: str):
        """Конструктор Цели для квеста

        :param typ: Тип цели(collect, kill)
        :param obj: Обьект для достижения цели (Item, Enemy)
        :param count: Кол-во обьектов для достижения цели
        """
        self.typ = typ
        self.obj = obj
        self.count = count

    def check_done(self, hero):
        """Проверка на выполнение квеста"""
        if self.typ == 'collect':
            if hero.inventory.itemsList().count(self.obj) >= self.count:
                return True
        elif self.typ == 'kill':
            if hero.kills_counter.get(self.obj.name, 0) >= self.count:
                return True
        return False
