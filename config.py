# --- Константы
WIDTH = 800
HEIGHT = 650
CHUNK_SIZE = 50
FPS = 30

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


# --- Вспомогательные функции
def up(rect):
    rect.y -= CHUNK_SIZE
def down(rect):
    rect.y += CHUNK_SIZE
def left(rect):
    rect.x -= CHUNK_SIZE
def right(rect):
    rect.x += CHUNK_SIZE