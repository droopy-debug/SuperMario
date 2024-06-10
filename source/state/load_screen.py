#各个关卡之间的加载界面
from ..components import info
import pygame
class load_Screen:

    def __init__(self):
        pass

    def start(self,game_info):                                    #调用在tools.update()
        self.game_info = game_info
        self.finished = False
        self.next = 'level'
        self.duration = 2000                              #持续时间
        self.timer = 0
        self.info = info.Info('load_screen',self.game_info)

    def update(self, surface ,keys):
        if self.timer == 0:
            self.timer = pygame.time.get_ticks()

        if self.game_info['sound'] != 'congradulations':
            if self.game_info['lives'] == 3:
                self.game_info['sound'] = 'main_theme'
            elif self.game_info['lives'] > 0:
                self.game_info['sound'] = 'death_wav'
            else:
                self.game_info['sound'] = 'game_over'

            if pygame.time.get_ticks() - self.timer > 2500:
                self.finished = True
                self.timer = 0
                self.game_info['sound'] = 'main_theme'


        else:
                if pygame.time.get_ticks() - self.timer > 6000:
                    self.finished = True
                    self.timer = 0
                    self.game_info['sound'] = 'main_theme'


        self.draw(surface)
        self.info.update()

    def draw(self, surface):
        surface.fill((0,0,0))
        self.info.draw(surface)

class GameOver(load_Screen):
    def start(self,game_info):                             #调用在tools.update()
        self.game_info = game_info
        self.game_info['sound'] = 'game_over'
        load_Screen.__init__(self)
        self.finished = False
        self.next = 'main_menu'
        self.next = 'main_menu'
        self.duration = 4000
        self.timer = 0
        self.info = info.Info('game_over',self.game_info)

class Congradulations(load_Screen):
        def start(self, game_info):  # 调用在tools.update()
            self.game_info = game_info
            self.game_info['sound'] = 'congradulations'
            load_Screen.__init__(self)
            self.finished = False
            self.next = 'main_menu'
            self.duration = 4000
            self.timer = 0
            self.info = info.Info('congradulations', self.game_info)