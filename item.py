class Inventory:
    def __init__(self, owner, slots_count, slots_name=None, slots_items=None):
        """Конструктор класса Инвентарь

        :param owner: Владелец инвентаря(обьект)
        :param slots_count: Кол-во слотов
        :param slots_name: Названия слотов в виде (slot0_name, slot1_name...), необяз
        :param slots_items: Список предметов в слотах
        """
        self.owner = owner
        self.slots = [Slot(None, str(i)) for i in range(slots_count)]
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
        try:
            slot = [i for i in self.slots if i.name == slot_name][0]
            slot.item = item
        except IndexError:
            pass

    def append(self, other_inv):
        """Добавление предметов из другого инвенторя"""
        i = 0
        for s in self.slots:
            if s.item is None:
                s.item = other_inv.slots[i].item
                i += 1
                if i > len(other_inv.slots) - 1:
                    break

    def clear(self):
        """Отчистка всех слотов"""
        for s in self.slots:
            s.item = None

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
        self.name = name
        self.type = type
        self.for_slot = for_slot
        self.stats = stats

    def __str__(self):
        return self.name