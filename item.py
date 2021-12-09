import copy
from typing import List, Union


available_itemstats = '''
    damage(0...),
    armor(0...),
    drop_chance(0.01...1.00)\tШанс выпадения после смерти,
    price(0...) Цена для продажи,
'''


class Inventory:
    def __init__(self, owner, slots_count, slots_name=None, slots_items=None,
                 linked_inv=None):
        """Конструктор класса Инвентарь

        :param owner: Владелец инвентаря(обьект)
        :param slots_count: Кол-во слотов
        :param slots_name: Названия слотов в виде (slot0_name, slot1_name...), необяз
        :param slots_items: Список предметов в слотах
        :param linked_inv: Связанный с этим инвентарь(для авто перекладывания вещей)
        При его указания вещи сначала ложатся в связанный, а затем в основной инвентарь
        """
        self.owner = owner
        self.slots = [Slot(None, str(i)) for i in range(slots_count)]
        self.linked_inv = linked_inv
        if slots_name is not None:
            for i, name in enumerate(slots_name):
                self.slots[i].name = name
        if slots_items is not None:
            for i, item in enumerate(slots_items):
                self.slots[i].item = item

    def getSlotItem(self, slot_name):
        slot_name = str(slot_name)
        try:
            return [i.item for i in self.slots if i.name == slot_name][0]
        except IndexError:
            pass

    def setSlotItem(self, slot_name, item):
        slot_name = str(slot_name)
        if self.linked_inv:
            slot = [i for i in self.linked_inv.slots if i.name == slot_name][0]
            slot.item = item
            return
        try:
            slot = [i for i in self.slots if i.name == slot_name][0]
            slot.item = item
        except IndexError:
            pass

    def append(self, other_inv: Union['Inventory', list]):
        """Добавление предметов из другого инвенторя"""
        if isinstance(other_inv, Inventory):
            items = other_inv.itemsList(without_none=True)
        else:
            items = other_inv
        if len([i for i in self.slots if i.item is None]) < len(items):
            self.clear(trash=True)
        if self.linked_inv:
            for s in self.linked_inv.slots:
                if s.item is None:
                    for i in items:
                        if i.for_slot is not None and i.for_slot == s.name:
                            s.item = items.pop(items.index(i)).copy()
                            break
                    if len(items) == 0:
                        return
        for s in self.slots:
            if s.item is None:
                for i in items:
                    if i.for_slot is None or i.for_slot == s.name:
                        s.item = items.pop(items.index(i)).copy()
                        break
                if len(items) == 0:
                    break

    def clear(self, item=None, count=1, trash=False):
        """Отчистка всех слотов
        item, count - Определенный предмет в опр кол-ве
        trash=True - Мусор"""
        if trash:
            q_items = []  # Quest items
            if 'move_to' in self.owner.__dict__:
                q_items = [q.target.obj for q in self.owner.quests if q.target.typ == 'collect']
            t = []
            for i in self.itemsList(without_none=True):
                if i.price in range(0, 6) and i not in q_items:
                    t.append(i)
            if 'move_to' in self.owner.__dict__ and self.full():
                self.owner.SUBACTIONS[0](self.owner)
        for s in self.slots:
            if item:
                if s.item == item and count > 0:
                    s.item = None
                    count -= 1
                elif count == 0:
                    break
            elif trash:
                if s.item in t:
                    s.item = None
            else:
                s.item = None

    def itemsList(self, without_none=False) -> List['Item']:
        if without_none:
            return [s.item for s in self.slots if s.item]
        return [s.item for s in self.slots]

    def full(self):
        """Проверка на полный инвентарь"""
        return all([s.item is not None for s in self.slots])

    def contains(self, item):
        return item in self.itemsList()

    def __eq__(self, other):
        if isinstance(other, bool):  # Пустой ли инвентарь
            if all([s.item is None for s in self.slots]):
                return False
            else:
                return True

    def __call__(self, slot_name, item=None):
        """Получение предмета из слота ИЛИ вставка предмета в слот
        Чтобы получить предмет: item=None"""
        if item is None:
            return self.getSlotItem(slot_name)
        else:
            self.setSlotItem(slot_name, item)

    def __str__(self):
        s = ''
        for slot in self.slots:
            s += f'{slot.name}) {slot.item}\n'
        return s


class Slot(Inventory):
    def __init__(self, item: 'Item', name: str):
        self.item = item
        self.name = name


class Item:
    def __init__(self, name, type='collectable', for_slot=None, **stats):
        """
        :param name:
        :param type: collectable or equipment
        :param stats: Словарь статов предмета(например {'damage': 5}
        :param for_slot: Для слота с определнным названием
        """
        if stats is None:
            stats = {}
        self.name = name
        self.type = type
        self.for_slot = for_slot
        self.stats = stats

    def copy(self):
        return Item(self.name, self.type, self.for_slot, **self.stats)

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        return self.stats.get(item, 0)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.name == other.name and self.type == other.type \
                   and self.stats == other.stats