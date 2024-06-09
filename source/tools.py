#工具和游戏主控
import os
import pygame
import random

#定义工厂类
class Game:
    def __init__(self, state_dict , start_state):
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.keys = pygame.key.get_pressed()
        self.state_dict = state_dict
        self.state = self.state_dict[start_state]

    def update(self):
        if self.state.finished:                      #如果当前阶段已经结束，就换成下一个阶段
            game_info = self.state.game_info                          #信息传递在此实现，每次转换状态都将现时的游戏数据传入
            next_state = self.state.next
            self.state.finished = False
            self.state = self.state_dict[next_state]
            self.state.start(game_info)
        self.state.update(self.screen,self.keys)

    def run(self):
        while True:
            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         running = False
            #
            #     # 检查其他事件类型，例如按键按下和释放事件
            #     if event.type == pygame.KEYDOWN:
            #         print("Key pressed:", event.key)
            #     if event.type == pygame.KEYUP:
            #         print("Key released:", event.key)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:                          #接收键盘信息
                    self.keys = pygame.key.get_pressed()
                elif event.type == pygame.KEYUP:
                    self.keys = pygame.key.get_pressed()
                # if self.keys[pygame.K_s]:
                #     print("S key is pressed")
                # if self.keys[pygame.K_RIGHT]:
                #     print("Right key is pressed")
                # if self.keys[pygame.K_LEFT]:
                #     print("Left key is pressed")
            self.update()
            pygame.display.update()
            self.clock.tick(60)

def load_graphics(path , accept=('.jpg','.png','bmp','.gif')):     #接收文件路径  并且限制了接收文件的类型
    graphics = {}                                                    #创建空字典用于存储加载的图形文件
    for pic in os.listdir(path):                                      #遍历文件夹
        name, ext = os.path.splitext(pic)                              #拆分出后缀名并且只接收合法后缀
        if ext.lower() in accept:
            img = pygame.image.load(os.path.join(path, pic))
            if img.get_alpha():                                         #检查图像是否具有 alpha 通道（即图像是否是透明的），有则转换成支持alpha通道的格式，无则转成不支持
                img = img.convert_alpha()
            else:
                img = img.convert()                                      #可以提高性能，减少内存占用
            graphics[name] = img
    return graphics


#从加载好的图片里获取某部分图片
def get_image(sheet,x,y,width,height,colorkey,scale):  #图片  左上角坐标  宽  高   设置颜色透明的颜色值  放大倍数
    # print(f"宽度: {width}, 高度: {height}")
    # print(f"宽度的类型: {type(width)}, 高度的类型: {type(height)}")
    image = pygame.Surface((width,height))                       #创建一个和界面一样大的空图层
    image.blit(sheet,(0,0),(x,y,width,height))     #0,0代表要画到哪个位置，x,y,w,h代表取sheet哪个区域
    if not colorkey:
        colorkey = image.get_at((0, 0))  # 获取图片底色
    image.set_colorkey(colorkey)
    image = pygame.transform.scale(image,(int(width*scale),int(height*scale)))       #缩放图片
    return image