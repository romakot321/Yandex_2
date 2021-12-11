from config import *
import pygame
from datetime import datetime
from random import choice, randint
from item import Inventory
from typing import Tuple, List, Set, Union
from DBHandler import Handler
from funcs import *


class Character(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, color: Tuple[int, int, int] = SKINCOLOR):
        """Конструктор класса персонаж. Персонаж это НПС, враг и герой"""
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.health = 100
        self.inventory = Inventory(self, 3)  # У каждого персонажа есть инвентарь
        self.type = 'character'

    def onDeath(self, *args, **kwargs):
        pass

    def fullDescription(self):
        return f'{self.health}'

    def getFightStats(self): pass

    def onWindowPos(self):
        return self.rect.topleft - Hero.hero_object.velocity + (0, 25)

    def onWorldPos(self) -> tuple:
        return tuple(self.rect.center)

    def __str__(self):
        return f'{self.health}'


class Hero(Character):
    ACTIONS = ((1, complete_quest), (2, loot_nearest_structure),
               (1, hero_buy_equipment))  # кортеж действий, хранящий функции(из config)
    # TODO Продать вещи
    SUBACTIONS = (hero_sell_items, to_nearest_enemy)
    hero_object: 'Hero' = None
    app = None
    update_boost = 0

    def __init__(self):
        """Конструктор класса Герой

        :param velocity: Param for camera
        :param is_moving: Может ли герой идти
        """
        Character.__init__(self, WIDTH // 2, HEIGHT // 2, DARK_RED)
        self.name = 'Герой'
        self.velocity = pygame.math.Vector2(0, 0)
        self.lasttime = datetime.now()
        self.is_moving = True
        self.in_city = False
        self.equipment = Inventory(self, 5, ('head', 'body', 'legs',
                                             'boots', 'hands'))
        self.inventory = Inventory(self, 9, linked_inv=self.equipment)
        self.coins = 5
        self._curr_loc = None

        self.kills_counter = {}
        self.curr_fight = None
        Hero.hero_object = self
        self.death_count = 0

        self.quests: List['Quest'] = []
        self.move_to = None
        self.queue_move_to = []
        self.task = ''

    def update(self):
        if (datetime.now() - self.lasttime).seconds > 1 - 0.8 * Hero.update_boost \
                and self.is_moving and self.curr_fight is None:
            # Совершение случайного действия раз в 3 секунды
            self.lasttime = datetime.now()
            if self.in_city:
                if self.health < 100:
                    self.health += randint(5, 20)
                    return
            if self.move_to:
                # TODO Следование по заданному алгоритмом пути
                if isinstance(self.move_to, NPC):  # Проверка на нахождение рядом с целью(НПС)
                    x, y = self.move_to.onWorldPos()
                    # y = self.move_to.rect.center[1] - self.velocity.y
                    # Если на расстоянии 3-ех блоков...
                    if x in range(int(self.rect.centerx + self.velocity.x - 100),
                                  int(self.rect.centerx + self.velocity.x + 100)) \
                            and y in range(int(self.rect.centery + self.velocity.y - 100),
                                           int(self.rect.centery + self.velocity.y + 100)):
                        print(self.task)
                        if self.task.lower() == 'pass quest':
                            if self.quests[0].target.check_done(self):
                                self.move_to.dialog(quest='pass')
                                self.move_to = None
                                print("PASS")
                        elif self.task.lower() == 'get quest':
                            if self.move_to.quests:
                                self.move_to.dialog(quest='get')
                                self.task = ''
                                self.move_to = None
                        elif self.task.lower() == 'trade sell':
                            self.task = ''
                            self.move_to.dialog(trade='sell collectable')
                            self.move_to = None
                        elif self.task.lower() == 'trade buy':
                            if self.move_to.sell_items:
                                self.task = ''
                                self.move_to.dialog(trade='buy equip')
                                self.move_to = None
                elif isinstance(self.move_to, Enemy):
                    x, y = self.onWorldPos()
                else:
                    x, y = self.move_to.x, self.move_to.y
                    if self.task == 'moving' and self.quests:
                        complete_quest(self)
                xx, yy = self.onWorldPos()
                print(x, y, xx, yy)
                if x > xx:
                    right(self.velocity, self.rect)
                elif x < xx:
                    left(self.velocity, self.rect)
                elif y < yy:
                    up(self.velocity, self.rect)
                elif y > yy:
                    down(self.velocity, self.rect)
                else:
                    if isinstance(self.move_to, NPC) and self.task == 'pass quest':
                        self.move_to.dialog(quest='pass')
                    self.move_to = None
            else:
                if self.queue_move_to:
                    self.move_to = self.queue_move_to.pop(0)
                else:
                    if self.health in range(1, 25):
                        to_nearest_city(self)
                    elif not choices([a for _, a in self.ACTIONS],
                                     weights=[w for w, _ in self.ACTIONS])[0](self):
                        random_point(self)

    def add_velocity(self, value: tuple):
        self.velocity += value

    def set_velocity(self, *args):
        if isinstance(args[0], tuple):
            value = args[0]
        else:
            value = args
        assert len(value) == 2
        self.velocity = pygame.math.Vector2(value)

    def getFightStats(self):
        stats = {}
        for i in [i for i in self.equipment.itemsList() if i is not None]:
            for stat, value in i.stats.items():
                stats[stat] = stats.get(stat, 0) + value
        return {'damage': stats.get('damage', 0), 'armor': stats.get('armor', 0)}

    def onWindowPos(self):
        return self.rect.topleft

    def onWorldPos(self) -> tuple:
        return tuple(self.rect.center + self.velocity - (0, 25))

    def onDeath(self, *args):
        self.velocity = pygame.math.Vector2(0, 0)
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.death_count += 1


class NPC(Character):
    ACTIONS = (up, left, right, down)

    def __init__(self, x: int, y: int, name: str, loc, app, structure=None):
        """Конструктор класса НПС(мирный)

        :param loc: Прикрепление к локации
        :param app: class App from main.py
        :param structure: Прикрепление к структуре(необяз)
        """
        Character.__init__(self, x, y, SKINCOLOR)
        self.loc = loc
        self.app = app
        self.name = name
        self.structure = structure
        self.quests: List['Quest'] = []
        self.sell_items: List['Item'] = []
        self.lasttime = datetime.now()
        self.loc.characters.append(self)
        self._x, self._y = self.rect.x, self.rect.y
        self.is_moving = True
        self.type = 'npc'

    def dialog(self, quest=None, trade=None):
        """Получение текста диалога

        :param quest: get - получить квест, pass - сдать квест
        :param trade: buy equip - покупка снаряж, sell collectable - продажа трофеев
        :return: текст
        """
        if quest and self.quests:
            # --- Функциональная часть
            if quest == 'get':
                if not self.quests[0] in Hero.hero_object.quests:
                    Hero.hero_object.quests.append(self.quests[0])
            elif quest == 'pass':
                if self.quests[0].pass_quest(Hero.hero_object):
                    self.quests.pop(0)
                else:
                    return
            # --- Возвращение текста
            i = Handler.get_dialog(f'quest_{quest}')
            params = {}
            for param in i[3].split(','):  # Заполнение из need_params для форматирования text
                if param.strip() == 'quest_text':
                    params['quest_text'] = self.quests[0].text()
            left(Hero.hero_object.velocity, Hero.hero_object.rect)
            self.app.dialog = Dialog(Hero.hero_object, self, [i[2].format(**params)])
        elif trade:
            trade = trade.replace(' ', '_')
            if 'buy' in trade and self.sell_items:
                if 'equip' in trade:
                    item = choice([i for i in self.sell_items if i.type == 'equipment'])
                elif 'collectable' in trade:
                    item = choice([i for i in self.sell_items if i.type == 'collectable'])
                else:
                    item = choice(self.sell_items)
                price = item.price
                if price > 5:
                    price += randint(-4 - price // 5, 4 + price // 5)
                i = Handler.get_dialog(f'trade_{trade}')
                params = {}
                for p in i[3].split(','):
                    if p.strip() == 'item_name':
                        params['item_name'] = item.name
                    elif p.strip() == 'item_price':
                        params['item_price'] = price
                text = [i[2].format(**params)]
                if hero_need_item_buy(Hero.hero_object, item):
                    if Hero.hero_object.coins >= price:
                        item.price = price
                        Hero.hero_object.inventory.append([item])
                        Hero.hero_object.coins -= price
                        text.append('Согласен!')
                    else:
                        text.append('У меня нет на это денег.')
                else:
                    text.append('Не')
                    item = choice([i for i in self.sell_items if i.type == 'equipment'])
                    if hero_need_item_buy(Hero.hero_object, item):
                        if Hero.hero_object.coins >= price:
                            item.price = price
                            Hero.hero_object.inventory.append([item])
                            Hero.hero_object.coins -= price
                            text.append('Согласен!')
                        else:
                            text.append('У меня нет на это денег.')
                    else:
                        text.append('Не')
                left(Hero.hero_object.velocity, Hero.hero_object.rect)
                self.app.dialog = Dialog(Hero.hero_object, self, text)
            elif 'sell' in trade:
                if 'equip' in trade:
                    items = [i for i in Hero.hero_object.inventory.itemsList(without_none=True)
                             if i.type == 'equipment']
                elif 'collectable' in trade:
                    items = [i for i in Hero.hero_object.inventory.itemsList(without_none=True)
                             if i.type == 'collectable']
                else:
                    items = Hero.hero_object.inventory.itemsList()
                text = []
                for item in items:
                    price = item.price
                    if price > 5:
                        price += randint(-4 - price // 5, 4 + price // 5)
                    i = Handler.get_dialog(f'trade_{trade}')
                    params = {}
                    for p in i[3].split(','):
                        if p.strip() == 'item_name':
                            params['item_name'] = item.name
                        elif p.strip() == 'item_price':
                            params['item_price'] = price
                    text.append([i[2].format(**params)])
                    if hero_need_item_sell(Hero.hero_object, item):
                        item.price = price
                        Hero.hero_object.coins += price
                        Hero.hero_object.inventory.clear(item)
                        text.append("Согласен!")
                    else:
                        text.append("Откажусь")
                left(Hero.hero_object.velocity, Hero.hero_object.rect)
                self.app.dialog = Dialog(Hero.hero_object, self, text)

    def update(self):
        if not self.app.dialog:
            self.is_moving = True
        if (datetime.now() - self.lasttime).seconds > 3 - 2.8 * Hero.update_boost and self.is_moving:
            self.lasttime = datetime.now()
            if self.structure:
                choice(self.ACTIONS)(self.rect, None,
                                     (self.structure.x - BLOCK_SIZE * 4, self.structure.y - BLOCK_SIZE * 4),
                                     (self.structure.x + BLOCK_SIZE * 4, self.structure.y + BLOCK_SIZE * 4))
            else:
                choice(self.ACTIONS)(self.rect, None,
                                     (self.loc.minx, self.loc.miny),
                                     (self.loc.maxx, self.loc.maxy))

    def fullDescription(self) -> str:
        s = f'Имя: {self.name}\nТип: NPC\n{"Есть квесты" if self.quests else ""}\n'
        s += f'{"Есть предметы на продажу" if self.sell_items else ""}'
        return s

    def __str__(self):
        return f'{self.name}(HP: {self.health})'


class Enemy(Character):
    ACTIONS = (move_to_point,)

    def __init__(self, x: int, y: int, name: str, loc, structure=None):
        """Конструктор класса Враг

        :param loc: Прикрепление к локации
        :param structure: Прикрепление к структуре(необяз)
        """
        Character.__init__(self, x, y)
        self.loc = loc
        self.name = name
        self.structure = structure
        self.equipment = Inventory(self, 5, ('head', 'body', 'legs', 'boots', 'hands'))
        self.inventory = Inventory(self, 3, linked_inv=self.equipment)
        self.lasttime = datetime.now()
        self.loc.characters.append(self)
        self.type = 'enemy'

        self.move_to = Hero.hero_object
        self.curr_fight = None

    def onDeath(self, killer):
        if isinstance(killer, Hero):
            killer.kills_counter[self.name] = killer.kills_counter.get(self.name, 0) + 1
        try:
            self.loc.characters.remove(self)
        except ValueError:
            pass
        Hero.app.all_sprites.remove(self)
        del self

    def update(self):
        if (datetime.now() - self.lasttime).seconds > 0.2 - 0.15 * Hero.update_boost \
                and self.curr_fight is None:
            self.lasttime = datetime.now()
            choice(self.ACTIONS)(self.rect, self.move_to.onWorldPos(),
                                 minc=(self.loc.minx, self.loc.miny),
                                 maxc=(self.loc.maxx, self.loc.maxy))
            # --- Проверка на коллизию с героем
            if self.rect.collidepoint(Hero.hero_object.velocity.x + WIDTH // 2,
                                      Hero.hero_object.velocity.y + (HEIGHT // 2 - 25)):
                if Hero.hero_object.curr_fight is None \
                        and self.curr_fight is None:  # Создание сражения
                    Hero.hero_object.curr_fight = Fight(self, Hero.hero_object)
                    self.curr_fight = Hero.hero_object.curr_fight
                    right(Hero.hero_object.velocity, Hero.hero_object.rect)
            if self.onWorldPos()[0] < Hero.hero_object.onWorldPos()[0] - BLOCK_SIZE * 20 \
                    or self.onWorldPos()[0] > Hero.hero_object.onWorldPos()[0] + BLOCK_SIZE * 20 \
                    or self.onWorldPos()[1] < Hero.hero_object.onWorldPos()[1] - BLOCK_SIZE * 20 \
                    or self.onWorldPos()[1] > Hero.hero_object.onWorldPos()[1] + BLOCK_SIZE * 20:
                self.onDeath(None)

    def getFightStats(self):
        stats = {}
        for i in [i for i in self.equipment.itemsList() if i is not None]:
            for stat, value in i.stats.items():
                stats[stat] = stats.get(stat, 0) + value
        return {'damage': stats.get('damage', 0), 'armor': stats.get('armor', 0)}

    def fullDescription(self):
        s = f'Имя: {self.name}\nТип: Enemy\n{str(self.equipment)}'
        return s

    def __str__(self):
        return f'{self.name}(HP: {self.health})'
