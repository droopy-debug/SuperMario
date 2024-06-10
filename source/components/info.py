#游戏信息

import pygame
from .. import constants as C
from . import coins
from .. import setup,tools
pygame.font.init()

class Info:
    def __init__(self,state,game_info):
        self.state = state
        self.game_info = game_info
        self.create_state_lables()
        self.create_info_labels()
        self.flash_coin = coins.FlashingCoin()

    def create_state_lables(self):                    #阶段特有信息
        self.state_lables = []
        if self.state == 'main_menu':
            self.state_lables.append((self.create_lable('1 PLAYER GAME'),(272,360)))
            self.state_lables.append((self.create_lable('2 PLAYER GAME'), (272, 405)))
            self.state_lables.append((self.create_lable('TOP - '), (290, 465)))
            self.state_lables.append((self.create_lable('00000'), (400, 465)))
        elif self.state == 'load_screen':
            self.state_lables.append((self.create_lable('WORLD'), (280, 200)))
            self.state_lables.append((self.create_lable('1-1'), (430, 200)))
            self.state_lables.append((self.create_lable('x   {} '.format(self.game_info['lives'])), (380, 280)))
            self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'],178,32,12,16,(0,0,0),C.BG_MULTI)
        elif self.state == 'game_over':
            self.state_lables.append((self.create_lable('GAME OVER'), (280,300)))
        elif self.state == 'congradulations':
            self.state_lables.append((self.create_lable('Congradulations !'), (260, 300)))


    def create_info_labels(self):                     #通用信息
        self.info_lables = []
        self.info_lables.append((self.create_lable('MARIO'), (75,30)))
        self.info_lables.append((self.create_lable('WORLD'), (450, 30)))
        self.info_lables.append((self.create_lable('TIME'), (625, 30)))
        self.info_lables.append((self.create_lable('000000'), (75, 55)))
        self.info_lables.append((self.create_lable('x00'), (300, 45)))
        self.info_lables.append((self.create_lable('1 - 1'), (480, 55)))

    def create_lable(self,lable, size =40,width_scale = 1.25,height_scale = 1):           #将文字渲染成图片
        font = pygame.font.SysFont(C.FONT, size)
        lable_image = font.render(lable, True, (255,255,255))
        rect = lable_image.get_rect()
        lable_image = pygame.transform.scale(lable_image, (int(width_scale*rect.width), int(height_scale*rect.height)))

        return lable_image

    def update(self):
        self.flash_coin.update()

    def draw(self,surface):
        for lable in self.state_lables:
            surface.blit(lable[0],lable[1])
        for lable in self.info_lables:
            surface.blit(lable[0],lable[1])
        surface.blit(self.flash_coin.image,self.flash_coin.rect)
        if self.state == 'load_screen':
            surface.blit(self.player_image,(300,270))
