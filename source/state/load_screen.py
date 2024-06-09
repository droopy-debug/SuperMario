#各个关卡之间的加载界面
from ..components import info
import pygame
class load_Screen:

    def __init__(self):
        self.music_state = 'death_wav'

    def start(self,game_info):                                    #调用在tools.update()
        self.game_info = game_info
        self.finished = False
        self.next = 'level'
        self.duration = 2000                              #持续时间
        self.timer = 0
        self.info = info.Info('load_screen',self.game_info)

    def update(self, surface ,keys):
        self.draw(surface)
        self.info.update()
        if self.timer == 0:
            self.timer = pygame.time.get_ticks()
        elif pygame.time.get_ticks() - self.timer > 2000:
            self.finished = True
            self.timer = 0
            self.music_state = 'main_theme'
    def draw(self, surface):
        surface.fill((0,0,0))
        self.info.draw(surface)

class GameOver(load_Screen):
    def start(self,game_info):                             #调用在tools.update()
        self.game_info = game_info
        load_Screen.__init__(self)
        self.finished = False
        self.next = 'main_menu'
        self.next = 'main_menu'
        self.duration = 4000
        self.timer = 0
        self.info = info.Info('game_over',self.game_info)