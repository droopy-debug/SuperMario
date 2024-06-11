#玩家
import pygame
from . import powerup
from .. import setup,tools
from .. import constants as C
#from ..state import level
import json
import os


class player(pygame.sprite.Sprite):
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.load_data()
        self.setup_state()
        self.setup_velocities()
        self.setup_timers()
        self.loadimages()


    def load_data(self):                          #导入json文件
        file_name = self.name + '.json'
        file_path = os.path.join('source/data/player', file_name)              #文件路径
        with open(file_path) as f:
            self.player_data = json.load(f)

    def setup_state(self):                    #主角状态
        self.state = 'stand'
        self.face_right = True                #是否朝向右边
        self.dead = False                      #是否死亡
        self.big = False                        #是否变大
        self.can_jump = True                   #短时间内只能跳一次
        self.hurt_immune = False                #无敌帧
        self.fire = False                       #火焰状态
        self.can_shoot  = True                       #是否能够发射子弹

    def setup_velocities(self):                      #速度设置
        speed = self.player_data['speed']
        self.x_velocity = 0
        self.y_velocity = 0                                #各方向上的速度

        self.max_walk_vel = speed['max_walk_speed']
        self.max_run_vel = speed['max_run_speed']
        self.max_y_vel = speed['max_y_velocity']
        self.walk_accel = speed['walk_accel']                   #走路加速度
        self.run_accel = speed['run_accel']                    #跑步加速度
        self.turn_accel = speed['turn_accel']                 #转身加速度
        self.gravity = C.GRAVITY                                  #重力加速度
        self.anti_gravity = C.ANTI_GRAVITY                         #逆转重力加速度（起跳加速度）
        self.jump_vel = speed['jump_velocity']                     #起跳初速度

        self.max_x_vel = self.max_walk_vel                         #初始的最大速度为最大的步行速度
        self.x_accel = self.walk_accel                              #初始加速度为步行加速度


    def setup_timers(self):                               #创建各种各样的计时器
        self.walk_timer = 0
        self.transision_timer = 0
        self.death_timer = 0                               #记录死亡时间
        self.hurt_immune_timer = 0
        self.last_fireball_timer = 0

    def loadimages(self):                            #主角的各种帧造型
        sheet = setup.GRAPHICS['mario_bros']
        frame_rects = self.player_data['image_frames']

        self.right_small_normal_frames = []
        self.left_small_normal_frames = []
        self.right_big_normal_frames = []
        self.left_big_normal_frames = []
        self.right_big_fire_frames = []
        self.left_big_fire_frames = []

        self.small_normal_frames = [self.right_small_normal_frames,self.left_small_normal_frames]
        self.big_normal_frames = [self.right_big_normal_frames,self.left_big_normal_frames]
        self.big_fire_frames = [self.right_big_fire_frames,self.left_big_fire_frames]

        self.all_frames = [
            self.right_small_normal_frames,self.left_small_normal_frames,
            self.right_big_normal_frames,self.left_big_normal_frames,
            self.right_big_fire_frames,self.left_big_fire_frames,
        ]

        self.right_frames = self.right_small_normal_frames
        self.left_frames = self.left_small_normal_frames                  #默认状态

        # for frame_rect in frame_rects:
        #     right_image = tools.get_image(sheet, *frame_rect ,(0,0,0), C.PLAYER_MULTI)                #向右的直接获得
        #     left_iamge = pygame.transform.flip(right_image, True , False)                     #向左的翻转
        #     up_image = pygame.transform.rotate(right_image, 90)                                  #向上的逆时针旋转九十度
        #     down_image = pygame.transform.rotate(right_image, -90)                                      #向下的顺时针旋转九十度
        #     self.right_frames.append(right_image)
        #     self.left_frames.append(left_iamge)
        #     self.up_frames.append(up_image)
        #     self.down_frames.append(down_image)                                                  #添加到列表里面

        #frame_rects.items() 是 Python 中的一个方法，用于返回字典 frame_rects 中的键值对
        for group, group_frame_rects  in frame_rects.items():                       #将数据添加到合理的帧库
            for frame_rect in group_frame_rects:
                right_image = tools.get_image(sheet,frame_rect['x'],frame_rect['y'],frame_rect['width'],frame_rect['height'],(0,0,0),C.PLAYER_MULTI)
                left_image = pygame.transform.flip(right_image,True,False)
                if group == 'right_small_normal':
                    self.right_small_normal_frames.append(right_image)
                    self.left_small_normal_frames.append(left_image)
                if group == 'right_big_normal':
                    self.right_big_normal_frames.append(right_image)
                    self.left_big_normal_frames.append(left_image)
                if group == 'right_big_fire':
                    self.right_big_fire_frames.append(right_image)
                    self.left_big_fire_frames.append(left_image)
        # self.frames.append(tools.get_image(sheet, 178,32,12,16,(0,0,0),C.PLAYER_MULTI))

        self.frame_index = 0                                     #当前帧
        self.frames = self.right_frames                           #初始状态向右
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()

    def update(self,keys,level):
        #print(self.state)
        self.current_time = pygame.time.get_ticks()
        self.handle_states(keys,level)
        self.is_hurt_immune()                                      #无敌状态

    def handle_states(self, keys,level):                          #状态机

        #print(self.state)
        self.can_jump_or_not(keys)
        self.can_shoot_or_not(keys)
        if self.state == 'stand':
            self.stand(keys,level)
        elif self.state == 'walk':
            self.walk(keys,level)
        elif self.state == 'jump':
            self.jump(keys,level)
        elif self.state == 'fall' :
            self.fall(keys,level)
        elif self.state == 'die':
            self.die(keys)
        elif self.state == 'small2big':
            self.small2big(keys)
        elif self.state == 'big2small':
            self.big2small(keys)
        elif self.state == 'big2fire':
            self.big2fire(keys)


        if self.face_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def can_shoot_or_not(self,keys):
        if not keys[pygame.K_s]:
            self.can_shoot = True

    def can_jump_or_not(self,keys):
        if not keys[pygame.K_a]:
            self.can_jump = True

    def small2big(self,keys):
        self.fire = False
        frame_dur = 65
        sizes = [1,0,1,0,1,2,0,1,2,0,2]            #0 小 1 中 2 大
        frames_and_idx = [(self.small_normal_frames,0),(self.small_normal_frames,7),(self.big_normal_frames,0)]        #取帧组里的第几帧
        if self.transision_timer == 0:
            self.big = True
            self.transision_timer = self.current_time
            self.changing_idx = 0                                                                             #变身帧造型序号
        elif self.current_time - self.transision_timer > frame_dur:
            self.transision_timer = self.current_time
            #print(self.changing_idx)
            self.changing_idx %= 11
            frames, idx = frames_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1

            if self.changing_idx == len(sizes):
                self.transision_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames
    def big2small(self,keys):
        #print("666")
        frame_dur = 65
        sizes = [2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        frames_and_idx = [(self.small_normal_frames, 8), (self.big_normal_frames, 8), (self.big_normal_frames, 4)]
        if self.transision_timer == 0:
            self.big = False
            self.fire = False
            self.transision_timer = self.current_time
            self.changing_idx = 0
        elif self.current_time - self.transision_timer > frame_dur:
            self.transision_timer = self.current_time
            frames, idx = frames_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):
                self.transision_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_small_normal_frames
                self.left_frames = self.left_small_normal_frames

    def big2fire(self, keys):              #抄small2big

        frame_dur = 65                                       #换帧造型
        sizes = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]                        #0 大火 1 普大
        frames_and_idx = [(self.big_fire_frames, 3), (self.big_normal_frames, 3)]
        if self.transision_timer == 0:
            self.fire = True
            self.transision_timer = self.current_time
            self.changing_idx = 0
        elif self.current_time - self.transision_timer > frame_dur:
            self.transision_timer = self.current_time
            frames, idx = frames_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_big_fire_frames
                self.left_frames = self.left_big_fire_frames


    def change_player_image(self,frames,idx):                  #换肤 改成对应的帧组的对应序号帧
        self.frame_index = idx
        if self.face_right:
            self.right_frames = frames[0]
            self.image =  self.right_frames[self.frame_index]
        else:
            self.left_frames = frames[1]
            self.image = frames[1]
            self.image = self.left_frames[self.frame_index]
        last_frame_bottom = self.rect.bottom
        last_frame_centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = last_frame_bottom
        self.rect.centerx = last_frame_centerx             #前后帧的底部和中心位置与之统一



    def stand(self,keys,level):
        self.frame_index = 0
        self.x_velocity = 0
        self.y_velocity = 0
        if keys[pygame.K_RIGHT]:
            self.face_right = True
            self.state = 'walk'
        elif keys[pygame.K_LEFT]:
            self.face_right = False
            self.state = 'walk'
        elif keys[pygame.K_a] and self.can_jump:
            self.state = 'jump'
            self.y_velocity = self.jump_vel
        elif keys[pygame.K_s] and self.fire and self.can_shoot:
            self.shoot_fireball(level)

    def walk(self,keys,level):
        self.max_x_vel = self.max_walk_vel
        self.x_accel = self.walk_accel

        if keys[pygame.K_s]:                             #s键，按下后最大速度和加速度都变大
            self.max_x_vel = self.max_run_vel
            self.x_accel = self.run_accel
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)
        else:
            self.max_x_vel = self.max_walk_vel
            self.x_accel = self.walk_accel

        if keys[pygame.K_a] and self.can_jump:
            self.state = 'jump'
            self.y_velocity = self.jump_vel

        if self.current_time - self.walk_timer > self.calc_frame_duration():
            self.frame_index += 1;
            self.frame_index = (self.frame_index % 3 + 1 )
            self.walk_timer = self.current_time
        if keys[pygame.K_RIGHT]:
            #print('sssssssssssssss')
            self.face_right = True
            if self.x_velocity < 0:
                self.frame_index  = 5                            #刹车帧
                self.x_accel = self.turn_accel
            self.x_velocity = self.calc_val(self.x_velocity,self.x_accel,self.max_x_vel,True)       #右加速
        elif keys[pygame.K_LEFT]:
            self.face_right = False
            if self.x_velocity > 0:
                self.frame_index = 5
                self.x_accel = self.turn_accel
            self.x_velocity = self.calc_val(self.x_velocity,self.x_accel,self.max_x_vel,False)          #左加速
        else:
            if self.face_right:
                self.x_velocity -= self.walk_accel
                if self.x_velocity < 0:
                    self.x_velocity = 0
                    self.state = 'stand'
            else:
                self.x_velocity += self.walk_accel
                if self.x_velocity > 0:
                    self.x_velocity = 0
                    self.state = 'stand'


    def jump(self,keys,level):                     #跳跃在行走和站立时需要都能处理
        self.frame_index = 4                             #起跳使用第四帧
        self.y_velocity += self.anti_gravity
        self.can_jump = False                     #按下a以后不能再跳

        if self.y_velocity >= 0:
            self.state = 'fall'                             #y方向速度为0，开始下落

        if not keys[pygame.K_a]:                                     #没按跳就进入下落状态
            self.state = 'fall'
        elif keys[pygame.K_s] and self.fire and self.can_shoot:
            self.shoot_fireball(level)

        #空中左右动
        if keys[pygame.K_RIGHT]:
            self.x_velocity = self.calc_val(self.x_velocity,self.x_accel,self.max_x_vel,True)       #右加速
        elif keys[pygame.K_LEFT]:
            self.x_velocity = self.calc_val(self.x_velocity,self.x_accel,self.max_x_vel,False)          #左加速

    def fall(self,keys,level):
        self.y_velocity = self.calc_val(self.y_velocity,self.gravity,self.max_y_vel,True)

         # 空中左右动
        if keys[pygame.K_RIGHT]:
             self.x_velocity = self.calc_val(self.x_velocity, self.x_accel, self.max_x_vel, True)  # 右加速
        elif keys[pygame.K_LEFT]:
            self.x_velocity = self.calc_val(self.x_velocity, self.x_accel, self.max_x_vel, False)  # 左加速
        elif keys[pygame.K_s] and self.fire:
            self.shoot_fireball(level)


    def go_die(self):
        self.dead = True
        self.y_velocity = self.jump_vel
        #print(self.y_velocity)
        self.frame_index = 6                  #死亡造型
        self.state = 'die'
        #print(self.anti_gravity)
        self.death_timer = self.current_time

    def die(self,keys):

        self.rect.y += self.y_velocity                                #避开死亡碰撞检测,当下落到边界以外，触发死亡
        #print(self.y_velocity)
        self.y_velocity += self.anti_gravity


    def calc_val(self,vel ,accel, max_val, is_positive = True):
        if is_positive:
            return min(vel + accel, max_val)                 #达到最大速度之前一直加速
        else:
            return max(vel - accel, -max_val)                 #达到反向最大速度之前一直减速


    def calc_frame_duration(self):                          #帧持久计算，对应速度下动画帧的刷新速度
        durantion = -60 / self.max_run_vel * abs(self.x_velocity) + 80
        return durantion

    def is_hurt_immune(self):
        if self.hurt_immune:
            if self.hurt_immune_timer == 0:
                self.hurt_immune_timer = self.current_time
                self.black_image = pygame.Surface((1,1))
            elif self.current_time - self.hurt_immune_timer < 2000:
                if (self.current_time - self.hurt_immune_timer) % 100 < 50:                           #前50ms显示空白帧，后五十ms正常显示
                    self.image = self.black_image
            else:
                self.hurt_immune = False
                self.hurt_immune_timer = 0

    def shoot_fireball(self, level):                                           #为了传入powerup_group加入level参数
        if self.current_time - self.last_fireball_timer > 300:  # 控制发射频率
            self.frame_index = 6  # 发射姿势
            fireball = powerup.Fireball(self.rect.centerx, self.rect.centery, self.face_right)
            level.powerup_group.add(fireball)
            self.can_shoot = False
            self.last_fireball_timer = self.current_time

