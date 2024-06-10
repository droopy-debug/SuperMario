import pygame.sprite
from .. import  tools,setup
from .. import constants as C


class peach(pygame.sprite.Sprite):
        def __init__(self,name='peach'):
            pygame.sprite.Sprite.__init__(self)

            self.frame_rects = [(0,0,175,253)]

            self.frames = []
            for frame_rect in self.frame_rects:
                self.frames.append(tools.get_image(setup.GRAPHICS['peach'], *frame_rect, (0, 0, 0), 0.2))

            self.frame_index = 0
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect()
            self.rect.left = 8750
            self.rect.bottom = 538
