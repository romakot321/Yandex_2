#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import torch
from torch import nn
from torch.nn import functional as fun
from torch.autograd import Variable
import pandas as pd
import os
from random import randint
from math import sqrt


# In[2]:


width = 16
height = 13


# In[3]:


# Создание карты объектов
def random_map():
    free_map = np.ones((height, width))  # Карта свободных клеток (нунжна только для генерации)
    free_map[(height - 1) // 2][(width - 1) // 2] = 0  # Координата главного персонажа занята
    # print((height - 1) // 2, (width - 1) // 2)

    count_citizen = randint(0, 5)  # Количество жителей
    # Генерация
    citizen_map = np.zeros((height, width))
    for i in range(count_citizen):
        while True:
            coord = randint(0, height - 1), randint(0, width - 1)
            if free_map[coord]:
                free_map[coord] = 0
                citizen_map[coord] = randint(1, 3)  # Дружелюбность жителя
                break

    count_loot = randint(0, 5)  # Количество сундуков
    # Генерация
    x = randint(1, 3)  # Насколько нужен лут
    loot_map = np.zeros((height, width))
    for i in range(count_loot):
        while True:
            coord = randint(0, height - 1), randint(0, width - 1)
            if free_map[coord]:
                free_map[coord] = 0
                loot_map[coord] = x # Количество лута в сундуке не известно персонажу
                break

    count_enemy = randint(0, 5)  # Количество врагов
    # Генерация
    enemy_map = np.zeros((height, width))
    for i in range(count_enemy):
        while True:
            coord = randint(0, height - 1), randint(0, width - 1)
            if free_map[coord]:
                free_map[coord] = 0
                enemy_map[coord] = randint(1, 3)  # Сила врага
                break
    all_map = [['..'] * (width + 1) for _ in range(height + 1)]
    all_map = np.array(all_map)
    def to_two(x):
        x = str(x)
        if len(x) == 1:
            x += ' '
        return x
    all_map[0, :] = tuple(map(to_two, range(0, width + 1)))
    all_map[:, 0] = tuple(map(to_two, range(0, height + 1)))
    all_map[height // 2 + 1][width // 2 + 1] = 'me'
    for i, (c_l, l_l, e_l) in enumerate(zip(citizen_map, loot_map, enemy_map)):
        for j, (c, l, e) in enumerate(zip(c_l, l_l, e_l)):
            if c != 0:
                all_map[i + 1][j + 1] = f'c{int(c)}'
            if l != 0:
                all_map[i + 1][j + 1] = f'l{int(l)}'
            if e != 0:
                all_map[i + 1][j + 1] = f'e{int(e)}'
    # for l in all_map:
    #     print(*l)
    return multi_map(loot_map, citizen_map, enemy_map)


# In[4]:


def multi_map(*maps):
    return np.stack(maps, axis=-1)


# In[52]:


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(3*13*16, 200)
        self.fc2 = nn.Linear(200, 200)
        self.fc3 = nn.Linear(200, 4)

    def forward(self, x):
        x = fun.relu(self.fc1(x))
        x = fun.relu(self.fc2(x))
        x = self.fc3(x)
        return fun.softmax(x, dim=1)
    
    def predict(self, numpy_map):
        torch_map = torch.from_numpy(numpy_map)
        torch_map = torch_map.view(-1, 3*13*16)
        return self(torch_map.float()).view(4)


# In[53]:


class Station:
    def __init__(self, map_, parameters):
        self.map = map_
        self.parameters = np.array(parameters)
    
    def _get_one_value(self, x, y):
        sm = np.zeros((3))
        for i in range(max(x - 1, 0), min(x + 2, self.map.shape[0])):
            for j in range(max(y - 1, 0), min(y + 2, self.map.shape[1])):
                sm += self.map[i, j] / max(sqrt(((i - 1) ** 2 + (j - 1) ** 2)), 1)
        return sm
    
    def calculate(self):
        sm = np.zeros((4, 3))
        to_draw = np.zeros((13, 16))
        sides_sum = (height + width) / 2
        functions = (lambda x, y: x + 1 <= y and x + y < sides_sum - 1,
                     lambda x, y: x >= y and x + y < sides_sum,
                     lambda x, y: x + 1 >= y and x + y > sides_sum,
                     lambda x, y: x + 2 <= y and x + y > sides_sum - 1)
        for i in range(height):
            for j in range(width):
                mask = np.array([f(i, j) for f in functions])
                v, = np.where(mask == 1)
                to_draw[i, j] += v
                sm[mask] += self._get_one_value(i, j)
        sm = np.abs(sm - self.parameters)
        sm[:, 2] *= -1
        sm = np.sum(sm, axis=1)
        return sm
    
    def get(self):
        value = self.calculate()
        value[value < 0] = 0
        sm = np.sum(value)
        normalize_value = value / sm
        return torch.from_numpy(normalize_value)


# In[61]:


def save(net):
    torch.save(net.state_dict(), './NNsave')

def load():
    model = Net()
    model.load_state_dict(torch.load('./NNsave'))
    model.eval()
    return model


# In[62]:


agressive = Net()
calm = Net()
citizen = Net()
enemy = Net()


# In[66]:


def learn(net, parameters):
    learing_rate = 0.2
    optimizer = torch.optim.SGD(net.parameters(), lr=learing_rate, momentum=0.9)
    criterion = nn.NLLLoss()
    for i in range(200):
        optimizer.zero_grad()
        numpy_map = random_map()
        target = Station(numpy_map, parameters).get()
        torch_map = Variable(torch.from_numpy(numpy_map),  requires_grad=True)
        torch_map = torch_map.view(-1, 3*13*16)
        res = net(torch_map.float()).view(4)
        if not i % 20:
            print( i // 2, "%")
        loss = criterion(res, target.long())
        loss.backward()
        optimizer.step()
    print('100%')
    save(net)


# In[67]:


learn(calm, (2, 2, 2))

