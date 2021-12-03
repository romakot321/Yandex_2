import pygame
from config import *
from character import *
from location import *


class App:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(pygame.font.match_font('arial'), 25)
        self.small_font = pygame.font.Font(pygame.font.match_font('arial'), 14)
        self.all_sprites = pygame.sprite.Group()
        self.running = True
        self.show_info = False
        self.init()

    def init(self):
        for locname, params in locations_list.items():
            Location(locname, **params)
        self.hero = Hero()
        spawn_loc = Location.get_location(self.hero.velocity.x, self.hero.velocity.y)
        npc1 = NPC(spawn_loc.structures_list[0].x, spawn_loc.structures_list[0].y, 'Ben', spawn_loc,
                   spawn_loc.structures_list[0])
        self.all_sprites.add(self.hero)
        self.all_sprites.add(npc1)

    def run(self):
        running = True
        cam_move = (0, 0)

        while running:
            self.clock.tick(FPS)
            pygame.display.set_caption(str(self.clock.get_fps()))

            # Обновление
            self.hero.velocity += cam_move
            self.all_sprites.update()
            curr_loc = Location.get_location(self.hero.velocity.x, self.hero.velocity.y)
            if curr_loc:  # TODO Иначе если вышли за карту?
                for strc in curr_loc.structures_list:  # Проверка на коллизию со структурами
                    if strc.rect.collidepoint(self.hero.velocity.x + WIDTH // 2, self.hero.velocity.y + (HEIGHT // 2 - 25)):
                        # Прибавление т.к. нулевые координаты у камеры смещены
                        if strc.inventory == True:  # Не изменять, особенности ООП:)
                            self.hero.inventory.append(strc.inventory)
                            strc.inventory.clear()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Прекращение передвижения героя
                        self.hero.is_moving = not self.hero.is_moving
                    elif event.key == pygame.K_i:  # Показ главной информации(инвентарь)
                        self.show_info = not self.show_info
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
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for chrt in curr_loc.characters:
                        if chrt.rect.topleft[0] - self.hero.velocity[0] in range(0, WIDTH + 1) \
                                and chrt.rect.topleft[1] - self.hero.velocity[1] + 25 in range(0, HEIGHT + 1):
                            rect = pygame.rect.Rect(*(chrt.rect.topleft - self.hero.velocity + (0, 25)), 40, 40)
                            if rect.collidepoint(mouse_x, mouse_y):
                                self.screen.blit(self.font.render(chrt.fullDescription(), True, GRAY),
                                            (rect.left, rect.top - BLOCK_SIZE + 25))
            self.render()
        pygame.quit()

    def render(self):
        # Рендеринг
        curr_loc = Location.get_location(self.hero.velocity.x, self.hero.velocity.y)
        self.screen.fill(BLACK)
        for sprite in Location.getSpritesToDraw(self.hero.velocity):
            self.screen.blit(sprite.image, sprite.rect.topleft - self.hero.velocity + (0, 25))
            # Эффект передвижение камеры реализуется за счет вычитания вектора из координат спрайта
        for sprite in curr_loc.characters:
            self.screen.blit(sprite.image, sprite.rect.topleft - self.hero.velocity + (0, 25))
        self.screen.blit(self.hero.image, self.hero.rect.topleft)
        self.screen.blit(self.font.render(f"X;Y: {self.hero.velocity}", True, WHITE), (0, 0))
        if self.show_info:
            for i in range(len(self.hero.inventory.slots)):
                s = f'{i + 1}: {self.hero.inventory(i)}'
                self.screen.blit(self.font.render(s, True, WHITE), (0, (i + 1) * 20))
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for chrt in curr_loc.characters:
            if chrt.rect.topleft[0] - self.hero.velocity[0] in range(0, WIDTH + 1) \
                    and chrt.rect.topleft[1] - self.hero.velocity[1] + 25 in range(0, HEIGHT + 1):
                rect = pygame.rect.Rect(*(chrt.rect.topleft - self.hero.velocity + (0, 25)), 40, 40)
                if rect.collidepoint(mouse_x, mouse_y):
                    self.screen.blit(self.small_font.render(str(chrt), True, GRAY),
                                (rect.left, rect.top - BLOCK_SIZE + 25))

        pygame.display.flip()


if __name__ == '__main__':
    app = App()
    app.run()