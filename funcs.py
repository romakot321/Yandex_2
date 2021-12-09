import pygame
from random import randrange, choices

from config import BLOCK_SIZE, WIDTH, HEIGHT

# --- Вспомогательные функции
# --- Передвижение


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
        elif rect is not None and rect.centery + BLOCK_SIZE <= HEIGHT // 2:
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
        elif rect is not None and rect.centerx + BLOCK_SIZE <= WIDTH // 2:
            rect.centerx += BLOCK_SIZE


def random_point(hero):
    hero.move_to = pygame.math.Vector2(randrange(0, WIDTH * 19, 50),
                                       randrange(0, HEIGHT * 19, 50))


# --- Квесты

def complete_quest(hero):
    from location import Location
    if hero.quests:
        q = hero.quests[0]
        if q.target.typ == 'collect':
            if q.target.check_done(hero):
                hero.move_to = q.owner
                return True
            loc = Location.get_location(*hero.velocity.xy)
            min_pos = (99999, None)
            for s in loc.structures_list:
                if s.inventory.full():
                    x, y = hero.onWorldPos()
                    dist = ((s.x - x) ** 2 + (s.y - y) ** 2) ** 0.5
                    if dist < min_pos[0]:
                        min_pos = (dist, s)
                    # hero.move_to = pygame.math.Vector2(s.x, s.y)
            if min_pos[1]:
                hero.move_to = pygame.math.Vector2(min_pos[1].x, min_pos[1].y)
            else:
                hero.move_to = q.owner
                hero.task = 'pass quest'
            return True
    else:
        return get_quest(hero)


def get_quest(hero):
    min_pos = (9999999, None)
    for chrt in hero._curr_loc.characters:
        if 'quests' in chrt.__dict__ and chrt.quests:
            x2, y2 = chrt.onWorldPos()
            x, y = hero.onWorldPos()
            dist = ((x2 - x) ** 2 + (y2 - y) ** 2) ** 0.5
            if dist < min_pos[0]:
                min_pos = (dist, chrt)
    if min_pos[1]:
        hero.move_to = min_pos[1]
        hero.task = 'get quest'
        return True
    return False


# --- Торговля


def hero_need_item_buy(hero, item):
    """Нужен ли предмет герою для покупки"""
    w_yes, w_no = 0.1, 0.1
    if item.for_slot and item.type == 'equipment':
        if hero.equipment(item.for_slot) is None:
            w_yes += 1
        else:
            i = hero.equipment(item.for_slot)
            if i.damage < item.damage or i.armor < item.armor:
                w_yes += 1
            else:
                w_no += 0.5
    elif item.type == 'collectable':
        if item.price > 30:
            w_yes += 0.5
        else:
            w_no += 0.5
    return choices([True, False], weights=[w_yes, w_no])[0]


def hero_need_item_sell(hero, item):
    """Нужен ли предмет герою для продажи"""
    w_yes, w_no = 0.1, 0.1
    q_items = []  # Quest items
    if hero.quests:
        q_items = [q.target.obj for q in hero.quests if q.target.typ == 'collect']
    if item.for_slot and item.type == 'equipment':
        if hero.equipment(item.for_slot) is None:
            w_no += 1
        else:
            i = hero.equipment(item.for_slot)
            if i == item:
                w_no += 1
            elif i.damage < item.damage or i.armor < item.armor:
                w_no += 1
            else:
                w_yes += 0.5
    elif item.type == 'collectable':
        if item in q_items:
            w_no += 2
        else:
            w_yes += 1
    f = choices([True, False], weights=[w_yes, w_no])[0]
    return f


def hero_sell_items(hero):
    min_pos = (9999999, None)
    for chrt in hero._curr_loc.characters:
        if 'quests' in chrt.__dict__:  # if chrt is NPC
            x2, y2 = chrt.onWorldPos()
            x, y = hero.onWorldPos()
            dist = ((x2 - x) ** 2 + (y2 - y) ** 2) ** 0.5
            if dist < min_pos[0]:
                min_pos = (dist, chrt)
    if min_pos[1]:
        if hero.move_to:
            hero.queue_move_to.append(hero.move_to)
        hero.move_to = min_pos[1]
        hero.task = 'trade sell'