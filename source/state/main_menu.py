#主界面
import pygame
import random
from .. import setup
from .. import tools
from .. import constants as C
from .. components import info

class MainMenu:
    def __init__(self):
        game_info = {
            'score':0,
            'coins':0,
            'lives':3,
            'sound':  'main_theme',
        }
        self.start(game_info)

    def start(self,game_info):                                    #每次重置游戏
        self.game_info = game_info
        self.setup_background()
        self.setup_player()
        self.setup_cursor()                    #设置光标
        self.info = info.Info('main_menu',self.game_info)
        self.finished = False
        self.next = 'load_screen'
        self.cursor.state = '1P'

    def setup_background(self):
        self.background = setup.GRAPHICS['level_1']
        self.background_rect = self.background.get_rect()
        self.background = pygame.transform.scale(self.background,(int(self.background_rect.width * C.BG_MULTI),int(self.background_rect.height * C.BG_MULTI)))

        self.viewport = setup.SCREEN.get_rect()
        self.caption = tools.get_image(setup.GRAPHICS['title_screen'],1,60,  176,88, (255,0,220) ,C.BG_MULTI)

    def setup_player(self):
        self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'],178,32,  12,16, (0,0,0) ,C.PLAYER_MULTI)

    def setup_cursor(self):                              #光标
        self.cursor = pygame.sprite.Sprite()
        self.cursor.image = tools.get_image(setup.GRAPHICS['item_objects'], 24, 160, 8, 8, (0, 0, 0), C.PLAYER_MULTI)
        rect = self.cursor.image.get_rect()
        rect.x,rect.y = (220,360)
        self.cursor.rect = rect

    def update_cursor(self,keys):                              #光标更新
        if keys[pygame.K_UP]:
            self.cursor.state = '1P'
            self.cursor.rect.y = 360
        elif keys[pygame.K_DOWN]:
            self.cursor.state = '2P'
            self.cursor.rect.y = 405
        elif keys[pygame.K_RETURN]:
            self.reset_game_info()
            if self.cursor.state == '1P':
                self.finished = True
            elif self.cursor.state == '2P':
                self.finished = True

    def update(self, surface,keys):
        #surface.fill((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        self.update_cursor(keys)
        surface.blit(self.background,self.viewport)
        surface.blit(self.caption,(170,100))
        surface.blit(self.player_image,(110,491))
        surface.blit(self.cursor.image, self.cursor.rect)

        self.info.update()
        self.info.draw(surface)

    def reset_game_info(self):
        self.game_info.update({
            'score':0,
            'coins':0,
            'lives':3,
            'player_state':'small'
        })