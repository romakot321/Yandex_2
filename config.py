# --- Константы
import random

WIDTH = 800
HEIGHT = 650
BLOCK_SIZE = 50
FPS = 10

# --- Цвета
WHITE = (255, 255, 255)
GRAY = (127, 127, 127)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (150, 0, 24)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 71, 49)
FOREST_GREEN = (11, 102, 35)
BLUE = (0, 0, 255)

# --- Данные
locations_list: dict = {
    'loc1': {
        'minx': -WIDTH,
        'miny': -HEIGHT,
        'maxx': WIDTH * 10,
        'maxy': HEIGHT * 10
    }
}
structures_list = {
    'House': {
        'location_name': 'loc1',
        'color': RED,
        'x': random.randrange(100, 500, 50),
        'y': random.randrange(100, 200, 50)
    },
    'House2': {
        'location_name': 'loc1',
        'color': RED,
        'x': random.randrange(100, 500, 50),
        'y': random.randrange(100, 400, 50)
    }
}


# --- Вспомогательные функции
def up(velocity, rect):
    if velocity.y - BLOCK_SIZE >= 0:
        velocity.y -= BLOCK_SIZE
    else:
        if rect.centery - BLOCK_SIZE >= 0:
            rect.centery -= BLOCK_SIZE


def down(velocity, rect):
    if velocity.y + BLOCK_SIZE <= HEIGHT and rect.centery == HEIGHT // 2 - 25:
        velocity.y += BLOCK_SIZE
    else:
        if rect.centery + BLOCK_SIZE <= HEIGHT // 2 - 25:  # Height // 2 - 25
            rect.centery += BLOCK_SIZE


def left(velocity, rect):
    if velocity.x - BLOCK_SIZE >= 0:
        velocity.x -= BLOCK_SIZE
    else:
        if rect.centerx - BLOCK_SIZE >= 0:
            rect.centerx -= BLOCK_SIZE


def right(velocity, rect):
    if velocity.x + BLOCK_SIZE <= WIDTH and rect.centerx == WIDTH // 2:
        velocity.x += BLOCK_SIZE
    else:
        if rect.centerx + BLOCK_SIZE <= WIDTH // 2:
            rect.centerx += BLOCK_SIZE
