import pygame
from config import *
from character import *
from location import *


pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Random Game")
clock = pygame.time.Clock()
font = pygame.font.Font(pygame.font.match_font('arial'), 25)
all_sprites = pygame.sprite.Group()

for locname, params in locations_list.items():
    Location(locname, **params)
hero = Hero()
all_sprites.add(hero)
cam_move = (0, 0)
running = True
show_info = False

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # Прекращение передвижения героя
                hero.is_moving = not hero.is_moving
            elif event.key == pygame.K_i:  # Показ главной информации(инвентарь)
                show_info = not show_info
            elif event.key == pygame.K_LEFT:  # Ручное управление движения(TODO убрать перед релизом)
                cam_move = (-BLOCK_SIZE, cam_move[1])
            elif event.key == pygame.K_RIGHT:
                cam_move = (BLOCK_SIZE, cam_move[1])
            elif event.key == pygame.K_UP:
                cam_move = (cam_move[0], -BLOCK_SIZE)
            elif event.key == pygame.K_DOWN:
                cam_move = (cam_move[0], BLOCK_SIZE)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                cam_move = (0, cam_move[1])
            elif event.key in (pygame.K_UP, pygame.K_DOWN):
                cam_move = (cam_move[0], 0)

    # Обновление
    hero.velocity += cam_move
    all_sprites.update()
    curr_loc = Location.get_location(hero.velocity.x, hero.velocity.y)
    if curr_loc:  # TODO Иначе если вышли за карту?
        for strc in curr_loc.structures_list:  # Проверка на коллизию со структурами
            if strc.rect.collidepoint(hero.velocity.x + WIDTH // 2, hero.velocity.y + (HEIGHT // 2 - 25)):
                # Прибавление т.к. нулевые координаты у камеры смещены
                if strc.inventory == True:  # Не изменять, особенности ООП:)
                    hero.inventory.append(strc.inventory)
                    strc.inventory.clear()

    # Рендеринг
    screen.fill(BLACK)
    for sprite in Location.getSpritesToDraw(hero.velocity):
        screen.blit(sprite.image, sprite.rect.topleft - hero.velocity + (0, 25))
        # Эффект передвижение камеры реализуется за счет вычитания вектора из координат спрайта
    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect.topleft)
    screen.blit(font.render(f"X;Y: {hero.velocity}", True, WHITE), (0, 0))
    if show_info:
        for i in range(len(hero.inventory.slots)):
            s = f'{i + 1}: {hero.inventory(i)}'
            screen.blit(font.render(s, True, WHITE), (0, (i + 1) * 20))

    pygame.display.flip()

pygame.quit()
