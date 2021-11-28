# --- Константы
import random
from item import Item

WIDTH = 800
HEIGHT = 650
# нулевые координаты для камеры - WIDTH // 2, HEIGHT // 2 - 25
BLOCK_SIZE = 50
FPS = 10

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
def up(velocity, rect):
    if velocity.y - BLOCK_SIZE >= 0:
        velocity.y -= BLOCK_SIZE
    else:
        if rect.centery - BLOCK_SIZE >= 0:
            rect.centery -= BLOCK_SIZE


def down(velocity, rect):
    if velocity.y + BLOCK_SIZE <= HEIGHT * 20 and rect.centery == HEIGHT // 2:
        velocity.y += BLOCK_SIZE
    else:
        if rect.centery + BLOCK_SIZE <= HEIGHT // 2:
            rect.centery += BLOCK_SIZE


def left(velocity, rect):
    if velocity.x - BLOCK_SIZE >= 0:
        velocity.x -= BLOCK_SIZE
    else:
        if rect.centerx - BLOCK_SIZE >= 0:
            rect.centerx -= BLOCK_SIZE


def right(velocity, rect):
    if velocity.x + BLOCK_SIZE <= WIDTH * 20 and rect.centerx == WIDTH // 2:
        velocity.x += BLOCK_SIZE
    else:
        if rect.centerx + BLOCK_SIZE <= WIDTH // 2:
            rect.centerx += BLOCK_SIZE
