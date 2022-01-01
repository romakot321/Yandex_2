import pygame
from random import randrange, choices

from config import BLOCK_SIZE, WIDTH, HEIGHT


# --- Вспомогательные функции
# --- База данных
def do_action(string: str, hero):
    from DBHandler import Handler
    from character import Hero
    keywords = Handler.get_keywords()
    act = None
    for act, words in keywords.items():
        words, add_words = words
        if any([w in string for w in words]) \
                and any([w in string for w in add_words]):
            break
        else:
            act = None
    if act == 'loot_structure':
        loot_nearest_structure(hero)
    elif act == 'get_quest':
        get_quest(hero)
    elif act == 'complete_quest':
        complete_quest(hero)
    elif act == 'faster':
        Hero.update_boost = 1
    elif act == 'slower':
        Hero.update_boost = 0
    elif act == 'buy equipment':
        hero_buy_equipment(hero)
    elif act == 'sell items':
        hero_sell_items(hero)
    elif act == 'move to city':
        to_nearest_city(hero)
    elif act == 'move random':
        random_point(hero)


# --- Передвижение


def move_to_point(velocity, point: tuple, rect=None,
                  minc=(0, 0), maxc=(WIDTH * 20, HEIGHT * 20)):
    x, y, xx, yy = *velocity.center, *point
    if velocity.centerx < xx:
        right(velocity, rect, minc, maxc)
    elif velocity.centerx > xx:
        left(velocity, rect, minc, maxc)
    elif velocity.centery > yy:
        up(velocity, rect, minc, maxc)
    elif velocity.centery < yy:
        down(velocity, rect, minc, maxc)


def up(velocity, rect, mincoords=(0, 0), maxcoords=(WIDTH * 20, HEIGHT * 20)):
    if mincoords[0] < 0:
        mincoords = (0, mincoords[1])
    if mincoords[1] < 0:
        mincoords = (mincoords[0], 0)

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
    if mincoords[0] < 0:
        mincoords = (0, mincoords[1])
    if mincoords[1] < 0:
        mincoords = (mincoords[0], 0)

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
    hero.task = 'moving'
    hero.onAction('move random')


def to_nearest_enemy(hero, enemy_name=None):
    min_pos = (99999, None)
    for chrt in hero._curr_loc.characters:
        if chrt.type == 'enemy':
            if enemy_name and chrt.name == enemy_name or enemy_name is None:
                x, y = hero.onWorldPos()
                xx, yy = chrt.onWorldPos()
                dist = ((xx - x) ** 2 + (yy - y) ** 2) ** 0.5
                if dist < min_pos[0]:
                    min_pos = (dist, chrt)
    if min_pos[1]:
        hero.move_to = min_pos[1]
        hero.onAction('move enemy')
        return True
    return False


def loot_nearest_structure(hero):
    from location import Location, Structure
    loc = Location.get_location(*hero.velocity.xy)
    min_pos = (99999, None)
    x, y = hero.onWorldPos()
    for s in loc.structures_list:
        if isinstance(s, Structure) and s.inventory.full():
            dist = ((s.x - x) ** 2 + (s.y - y) ** 2) ** 0.5
            if dist < min_pos[0]:
                min_pos = (dist, s)
    if min_pos[1]:
        hero.move_to = pygame.math.Vector2(min_pos[1].x, min_pos[1].y)
        hero.onAction('move structure')
        return True
    return False


def to_nearest_city(hero):
    from location import Location, City
    loc = Location.get_location(*hero.velocity.xy)
    min_pos = (99999, None)
    x, y = hero.onWorldPos()
    for s in loc.structures_list:
        if isinstance(s, City):
            dist = ((s.x - x) ** 2 + (s.y - y) ** 2) ** 0.5
            if dist < min_pos[0]:
                min_pos = (dist, s)
    if min_pos[1]:
        hero.move_to = pygame.math.Vector2(min_pos[1].x, min_pos[1].y)
        hero.onAction('move city')
        return True
    return False


# --- Квесты


def hero_need_quest(hero, quest) -> bool:
    w_no, w_yes = 0.1, 0.1
    if hero.profile['hero character'] == 'абсолютно добрый':
        if quest.target.typ == 'kill':
            w_no += 2
        else:
            w_yes += 0.5
    elif hero.profile['hero character'] == 'добродушный':
        if quest.target.typ == 'kill':
            w_no += 0.5
        else:
            w_yes += 0.5
    else:
        w_yes += 0.5
    return choices([False, True], weights=[w_no, w_yes])[0]


def complete_quest(hero, q=None):
    if hero.quests or q:
        if q is None:
            q = hero.quests[0]
        if q.target.typ == 'collect':
            if q.target.check_done(hero):
                hero.task = 'pass quest'
                hero.move_to = q.owner
                hero.onAction('move pass quest')
                return True
            if loot_nearest_structure(hero):
                return True
            else:
                return to_nearest_enemy(hero)
        elif q.target.typ == 'kill':
            return to_nearest_enemy(hero, q.target.obj)
        elif q.target.typ == 'sell':
            if q.target.check_done(hero):
                hero.task = 'pass quest'
                hero.move_to = q.owner
                hero.onAction('move pass quest')
                return True
            if hero.inventory.contains(q.target.obj):
                return hero_sell_items(hero)
            else:
                return loot_nearest_structure(hero)
    else:
        if hero.profile.get('main quest'):
            return complete_quest(hero, hero.profile.get('main quest'))
        return get_quest(hero)
    return False


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
        hero.onAction('move get quest')
        return True
    return False


# --- Торговля(предметы)


def hero_need_item_buy(hero, item):
    """Нужен ли предмет герою для покупки"""
    w_yes, w_no = 0.1, 0.1
    if item.for_slot and item.type == 'equipment':
        if hero.equipment(item.for_slot) is None:
            w_yes += 1
        else:
            if item.better_item(item, hero.equipment(item.for_slot)):
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
    q_items, sell_q_items = [], []  # Quest items
    if hero.quests:
        q_items = [(q.target.obj, q.target.count) for q in hero.quests if q.target.typ == 'collect']
        sell_q_items = [q.target.obj for q in hero.quests if q.target.typ == 'sell']
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
        if item in [t.info[1] for t in hero.profile['tendencies'] if t.info[0] == 'like_item']:  # Если привязанность
            w_no += 5
        elif item in [i for i, _ in q_items]:  # Если квестовый предмет
            if [i.name for i in hero.inventory.itemsList(without_none=True)].count(item.name) - 1 <= \
                    [c for i, c in q_items if i.name == item.name][0]:  # и кол-во <= необходимого
                w_no += 2
            else:
                w_yes += 1
        elif item in sell_q_items:
            w_yes += 2
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
        hero.onAction('move trade sell')


def hero_buy_equipment(hero):
    if hero.coins < 50:
        return complete_quest(hero)
    min_pos = (9999999, None)
    x, y = hero.onWorldPos()
    for chrt in hero._curr_loc.characters:
        if 'sell_items' in chrt.__dict__:  # if chrt is NPC
            if chrt.sell_items:
                x2, y2 = chrt.onWorldPos()
                dist = ((x2 - x) ** 2 + (y2 - y) ** 2) ** 0.5
                if dist < min_pos[0]:
                    min_pos = (dist, chrt)
    if min_pos[1]:
        if hero.move_to:
            hero.queue_move_to.append(hero.move_to)
        hero.move_to = min_pos[1]
        hero.task = 'trade buy'
        hero.onAction('move trade buy')
        return True
    return False
