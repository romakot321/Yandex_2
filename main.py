import pygame
from config import *
from character import *
from location import *


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Random Game")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
chr = Character()
loc1 = Location('location')
all_sprites.add(chr)

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Обновление
    all_sprites.update()

    # Рендеринг
    screen.fill(BLACK)
    for sprite in loc1.blocks_sprites:
        screen.blit(sprite.image, sprite.rect.topleft + chr.velocity)
    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect.topleft)
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()