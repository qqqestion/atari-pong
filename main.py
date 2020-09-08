import pygame

import json

import constants

import abc

pygame.init()
pygame.font.init()
pygame.display.init()


class Cfg:

    def __init__(self, filename=None):
        if filename:
            self.filename = filename
            with open(filename, 'r') as fp:
                self._items = json.load(fp)
        else:
            self.filename = 'cfg.json'
            self._items = []

    def get(self, item):
        if item in self._items:
            return self._items[item]
        return None

    def values(self):
        return self._items

    def __getitem__(self, item):
        for setting in self._items:
            if setting['name'] == item:
                return setting
        raise KeyError

    def dump(self):
        with open(self.filename, 'w') as fp:
            json.dump(self._items, fp)


class Scene(abc.ABC):

    def __init__(self, player):
        self.player = player

    @abc.abstractmethod
    def handle_keydown(self, event):
        pass

    @abc.abstractmethod
    def draw(self, surface):
        pass

    def handle_keyup(self, event):
        pass


class BaseTennisRacket(abc.ABC):
    pass


class PlayerTennisRacket(BaseTennisRacket):
    pass


class AITennisRacket(BaseTennisRacket):
    pass


class GameBall:
    pass


class SoloScene(Scene):
    def handle_keydown(self, event):
        pass

    def draw(self, surface):
        pass


class TwoPlayerScene(Scene):

    def __init__(self, player):
        super().__init__(player)
        self.first_racket = PlayerTennisRacket(self.player)
        self.second_racket = PlayerTennisRacket(self.player)
        self.ball = GameBall(self.player)
        self.score = [0, 0]

    def handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            self.player.set_scene(MenuScene(self.player))

        # First player keys
        if event.key == pygame.K_w:
            self.first_racket.hold_up = True
        if event.key == pygame.K_s:
            self.first_racket.hold_down = True

        # Second player keys
        if event.key == pygame.K_UP:
            self.first_racket.hold_up = True
        if event.key == pygame.K_DOWN:
            self.first_racket.hold_down = True

    def handle_keyup(self, event):
        # First player keys
        if event.key == pygame.K_w:
            self.first_racket.hold_up = False
        if event.key == pygame.K_s:
            self.first_racket.hold_down = False

        # Second player keys
        if event.key == pygame.K_UP:
            self.first_racket.hold_up = False
        if event.key == pygame.K_DOWN:
            self.first_racket.hold_down = False

    def draw(self, surface: pygame.Surface):
        # if self.hold_down:
        #     self.first_player_pos += 10
        surface.fill(constants.black)


class SettingsScene(Scene):

    def __init__(self, player):
        super().__init__(player)
        self.settings = self.player.cfg.values()
        self._current_setting = 0

    def handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            self.player.set_scene(MenuScene(self.player))
        if event.key == pygame.K_DOWN:
            self._current_setting = min(len(self.settings) - 1, self._current_setting + 1)
        if event.key == pygame.K_UP:
            self._current_setting = max(0, self._current_setting - 1)
        if event.key == pygame.K_LEFT:
            setting = self.settings[self._current_setting]
            setting['current_choice'] = (setting['current_choice'] - 1 if setting['current_choice'] > 0
                                         else len(setting['available_choices']) - 1)
        if event.key == pygame.K_RIGHT:
            setting = self.settings[self._current_setting]
            setting['current_choice'] = (setting['current_choice'] + 1
                                         if setting['current_choice'] < len(setting['available_choices']) - 1
                                         else 0)
        if event.key == pygame.K_RETURN:
            self.player.cfg.dump()
            old_screen = self.player.screen
            self.player.screen = self.player.create_window()
            self.player.screen.blit(old_screen, (0, 0))
            del old_screen
            self.player.set_scene(MenuScene(self.player))

    def draw(self, surface):
        surface.fill(constants.black)
        font = pygame.font.SysFont('courier', 34)
        for i, setting in enumerate(self.settings):
            if i == self._current_setting:
                color = constants.silver
            else:
                color = constants.gray
            text = f'{setting["name"]}: << {setting["available_choices"][setting["current_choice"]]} >>'
            surface.blit(font.render(text, True, color),
                         (10, i * 25))
        info_text = 'To save settings press Enter'
        surface.blit(font.render(info_text, True, constants.gray),
                     (10, 300))


class MenuScene(Scene):
    menu_items = [('Play: Solo', SoloScene),
                  ('Play: Two', TwoPlayerScene),
                  ('Settings', SettingsScene)]
    _current_item = 0

    def handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            self.player.running = False
        if event.key == pygame.K_UP:
            self._current_item = max(0, self._current_item - 1)
        if event.key == pygame.K_DOWN:
            self._current_item = min(len(self.menu_items) - 1,
                                     self._current_item + 1)
        if event.key == pygame.K_RETURN:
            new_scene = self.menu_items[self._current_item][1](self.player)
            self.player.set_scene(new_scene)

    def draw(self, surface):
        screen_size = self.player.cfg['screen_size']
        width, height = map(int, screen_size['available_choices'][screen_size['current_choice']].split('x'))
        button_width = max(width / 10, 160)
        button_height = max(height / 10, 90)

        x_cor = width // 2 - button_width // 2
        y_cor = height // 2 - button_height - 20
        # print(f'Width {button_width}, height {button_height}, x_cor {x_cor}, y_cor {y_cor}')
        surface.fill(constants.black)
        font = pygame.font.SysFont('courier', 24)
        for i in range(len(self.menu_items)):
            r = pygame.Rect((x_cor, y_cor + i * (button_height + 10), button_width, button_height))

            if i == self._current_item:
                color = constants.blue_gray
            else:
                color = constants.gray
            pygame.draw.rect(surface, color, r)
            surface.blit(font.render(self.menu_items[i][0], True, constants.white),
                         (x_cor + 40, y_cor + i * (button_height + 10) + button_height // 2 - 8))


class Player:
    running = True

    def __init__(self, cfg=None):
        self.scene = MenuScene(self)
        self.cfg = cfg or Cfg()
        self.screen = self.create_window()

    def create_window(self):
        screen_size = self.cfg['screen_size']
        size = tuple(map(int, screen_size['available_choices'][screen_size['current_choice']].split('x')))
        return pygame.display.set_mode(size)

    def handle_keydown(self, event):
        self.scene.handle_keydown(event)

    def handle_keyup(self, event):
        self.scene.handle_keyup(event)

    def draw_scene(self):
        self.scene.draw(self.screen)

    def set_scene(self, new_scene: Scene):
        self.scene = new_scene


def main():
    cfg = Cfg('cfg.json')
    player = Player(cfg)
    pygame.display.set_caption('Holy sheet')
    while player.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                player.running = False
            if event.type == pygame.KEYDOWN:
                player.handle_keydown(event)
            if event.type == pygame.KEYUP:
                player.handle_keyup(event)
        player.draw_scene()
        pygame.display.update()
    pygame.quit()


if __name__ == '__main__':
    main()
