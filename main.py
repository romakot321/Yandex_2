import pygame
from datetime import datetime
from config import *
from character import *
from location import *
from DBHandler import *


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

        self.dialog = None
        self.dialog_text, self.dialog_pos = None, None

        self.enter_action = None

        self.init()

    def init(self):
        for locname, params in locations_list.items():
            params['app'] = self
            Location(locname, **params)
        self.hero = Hero()
        Hero.app = self
        self.hero.inventory('hands', Item.getItem('Ban hammer'))
        self.all_sprites.add(self.hero)

    def run(self):
        running = True
        cam_move = (0, 0)
        show_text = ''
        lasttime_showtext = None
        lasttime_spawn = datetime.datetime.now()

        while running:
            self.clock.tick(FPS)
            pygame.display.set_caption(str(self.clock.get_fps()))

            # Обновление
            if self.dialog:
                self.hero.is_moving = False
                self.dialog.character.is_moving = False
            elif not self.hero.is_moving:
                self.hero.is_moving = True

            self.hero.velocity += cam_move
            curr_loc = Location.get_location(self.hero.velocity.x, self.hero.velocity.y)
            self.hero.update()
            for s in curr_loc.getSpritesToUpdate(self.hero.velocity):  # sprites update
                s.update()
            if (datetime.datetime.now() - lasttime_spawn).seconds > 5:  # Spawn enemy
                lasttime_spawn = datetime.datetime.now()
                e = curr_loc.spawnEnemy()
                if e:
                    self.all_sprites.add(e)
            self.hero._curr_loc = curr_loc
            self.hero.in_city = False
            if curr_loc:  # TODO Иначе если вышли за карту?
                for strc in curr_loc.structures_list:  # Проверка на коллизию со структурами
                    if strc.rect.collidepoint(*self.hero.onWorldPos()):
                        # Прибавление т.к. нулевые координаты у камеры смещены
                        if isinstance(strc, City):
                            self.hero.in_city = True
                        else:
                            if strc.inventory == True:  # Не изменять, особенности ООП:)
                                self.hero.inventory.append(strc.inventory)
                                strc.inventory.clear()
                for chrt in curr_loc.characters:  # Проверка на коллизию с персонажами
                    if pygame.rect.Rect(*(chrt.rect.topleft - self.hero.velocity
                                        + (0, 25)), 40, 40).collidepoint(self.hero.rect.x,
                                                                        self.hero.rect.y):
                        if isinstance(chrt, Enemy) and self.hero.curr_fight is None \
                                and chrt.curr_fight is None:  # С врагом
                            self.hero.curr_fight = Fight(self.hero, chrt)
                            chrt.curr_fight = self.hero.curr_fight
                            left(self.hero.velocity, self.hero.rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.enter_action is not None:
                        if event.key == pygame.K_RETURN:
                            do_action(self.enter_action, self.hero)
                            self.enter_action = None
                        elif event.key == pygame.K_BACKSPACE:
                            self.enter_action = self.enter_action[:-1]
                        else:
                            self.enter_action += event.unicode
                    elif event.key == pygame.K_p:  # Прекращение передвижения героя
                        self.hero.is_moving = not self.hero.is_moving
                    elif event.key == pygame.K_a:
                        self.enter_action = ''
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
                                show_text = chrt.fullDescription()
                                lasttime_showtext = datetime.datetime.now()
            if lasttime_showtext is not None and (datetime.datetime.now() - lasttime_showtext).seconds >= 5:
                show_text = ''
                lasttime_showtext = None
            if self.hero.curr_fight:
                if (datetime.datetime.now().now() - self.hero.curr_fight.lasttime).seconds > \
                        3 - 2 * Hero.update_boost:
                    lasttime_showtext = datetime.datetime.now()
                    self.hero.curr_fight.lasttime = datetime.datetime.now()
                    show_text = self.hero.curr_fight.next()
            self.render(show_text)
        pygame.quit()

    def render(self, show_text=''):
        # Рендеринг
        curr_loc = Location.get_location(self.hero.velocity.x, self.hero.velocity.y)
        self.screen.fill(BLACK)

        # --- Render sprites
        for sprite in Location.getSpritesToDraw(self.hero.velocity):
            self.screen.blit(sprite.image, sprite.rect.topleft - self.hero.velocity + (0, 25))
            # Эффект передвижение камеры реализуется за счет вычитания вектора из координат спрайта
        for sprite in curr_loc.characters:
            self.screen.blit(sprite.image, sprite.rect.topleft - self.hero.velocity + (0, 25))
        self.screen.blit(self.hero.image, self.hero.rect.topleft)

        self.screen.blit(self.font.render(f"X,Y: {self.hero.rect.center + self.hero.velocity - (0, 25)}",
                                          True, WHITE), (0, 0))

        # --- Render fight info
        if self.hero.curr_fight:
            s = pygame.Surface((WIDTH, HEIGHT // 2), pygame.SRCALPHA)
            s.set_alpha(200)
            s.fill(GRAY)
            self.screen.blit(s, (0, HEIGHT // 2))
            self.screen.blit(self.font.render(self.hero.curr_fight.attacker.name, True, WHITE),
                             (WIDTH // 4, HEIGHT // 2 + 10))
            self.screen.blit(self.font.render(f'HP: {self.hero.curr_fight.attacker.health}', True, WHITE),
                             (0, HEIGHT // 2 + 35))
            self.screen.blit(self.font.render(self.hero.curr_fight.target.name, True, WHITE),
                             (WIDTH // 4 * 3, HEIGHT // 2 + 10))
            self.screen.blit(self.font.render(f'HP: {self.hero.curr_fight.target.health}', True, WHITE),
                             (WIDTH // 2, HEIGHT // 2 + 35))
            i = 0
            for s in self.hero.curr_fight.journal.split('\n'):
                self.screen.blit(self.font.render(s, True, WHITE),
                                 (WIDTH // 3, HEIGHT // 4 * 3 + i))
                i += 25

        # --- Render dialog
        if self.dialog:
            if (datetime.datetime.now() - self.dialog.lasttime).seconds >= 2 - 1.5 * Hero.update_boost:
                a = next(self.dialog)
                if a:
                    self.dialog_pos, self.dialog_text = (a[0], a[1]), a[2]
                    self.dialog.lasttime = datetime.datetime.now()
                else:
                    self.dialog_pos, self.dialog_text = None, None
                    self.dialog = None
            if self.dialog_pos:
                x, y = self.dialog_pos
                s = pygame.Surface((BLOCK_SIZE * 5, 20 * len(self.dialog_text) + 5),
                                   pygame.SRCALPHA)
                s.set_alpha(200)
                s.fill(GRAY)
                self.screen.blit(s, (x - 20, y - 5))
                for s in self.dialog_text:
                    self.screen.blit(self.small_font.render(s, True, WHITE),
                                     (x, y))
                    y += 20

        if self.show_info:
            s = pygame.Surface((WIDTH // 2 - 25, HEIGHT), pygame.SRCALPHA)
            s.set_alpha(180)
            s.fill((121, 61, 78))
            self.screen.blit(s, (0, 0))
            self.screen.blit(self.font.render(f'Монет: {self.hero.coins}', True, FONT_TEXT),
                             (0, 22))
            self.screen.blit(self.font.render(f'HP: {self.hero.health}', True, FONT_TEXT),
                             (0, 44))
            i = 2
            for s in str(self.hero.equipment).split('\n'):
                self.screen.blit(self.font.render(s, True, FONT_TEXT), (0, (i + 1) * 22))
                i += 1
            self.screen.blit(self.font.render('Квесты:', True, FONT_TEXT), (0, (i + 1) * 22))
            for q in self.hero.quests:
                i += 1
                self.screen.blit(self.font.render(f'{q.name}) {q.target}', True, FONT_TEXT), (0, (i + 1) * 22))
            self.hero.inventory.draw(self.screen)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for chrt in curr_loc.characters:
            if chrt.rect.topleft[0] - self.hero.velocity[0] in range(0, WIDTH + 1) \
                    and chrt.rect.topleft[1] - self.hero.velocity[1] + 25 in range(0, HEIGHT + 1):
                rect = pygame.rect.Rect(*(chrt.rect.topleft - self.hero.velocity + (0, 25)), 40, 40)
                if rect.collidepoint(mouse_x, mouse_y):
                    self.screen.blit(self.small_font.render(str(chrt), True, GRAY),
                                (rect.left, rect.top - BLOCK_SIZE + 25))
        if show_text:
            if isinstance(show_text, str):  # отображение по центру
                y = 25
                for s in show_text.split('\n'):
                    self.screen.blit(self.font.render(s, True, GRAY),
                                     (WIDTH // 2, y))
                    y += 25
            elif isinstance(show_text, tuple):  # Отображение по show_text[0, 1]
                self.screen.blit(self.small_font.render(show_text[2], True, RED),
                                 (show_text[0], show_text[1]))
        if self.enter_action is not None:
            self.screen.blit(self.font.render(self.enter_action, True, FONT_TEXT),
                             (50, HEIGHT - BLOCK_SIZE))

        pygame.display.flip()


if __name__ == '__main__':
    app = App()
    app.run()