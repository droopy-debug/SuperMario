#游戏关卡
import json
import os

from .. import tools,setup
from .. import constants as C
from .. components import info,player,stuff,brick,box,enemy,peach

import pygame
class level:
    def start(self,game_info):
        self.game_info = game_info
        self.finished = False
        self.next = 'game_over'
        self.info = info.Info('level',self.game_info)
        self.load_map_data()
        self.setup_start_positions()

        self.setup_background()
        self.setup_player()
        self.setup_ground_items()
        self.setup_bricks_and_boxes()
        self.setup_enemies()
        self.setup_checkpoint()


    def load_map_data(self):
        file_name = 'level_1.json'
        file_path = os.path.join('source/data/maps', file_name)
        with open(file_path) as f:
            self.map_data = json.load(f)

    def setup_background(self):                                               #设置关卡背景
        self.image_name = self.map_data['image_name']
        self.background = setup.GRAPHICS[self.image_name]

        # self.background = setup.GRAPHICS['level_1']
        rect = self.background.get_rect()
        self.background = pygame.transform.scale(self.background, (int(rect.width* C.BG_MULTI), int(rect.height * C.BG_MULTI)))

        self.background_rect = self.background.get_rect()
        self.game_window = setup.SCREEN.get_rect()

        self.game_ground = pygame.Surface((self.background_rect.width,self.background_rect.height))               #新图层

    def setup_start_positions(self):                               #开始位置
        self.posisions = []
        for data in self.map_data['maps']:
            self.posisions.append((data['start_x'],data['end_x'],data['player_x'],data['player_y']))
        self.start_x,self.end_x,self.player_x,self.player_y = self.posisions[0]

    def setup_player(self):
        self.player = player.player('mario')
        self.player.rect.x = self.game_window.x + self.player_x
        self.player.rect.bottom = self.player_y                            #底部


    def setup_ground_items(self):
        self.ground_items_group = pygame.sprite.Group()           #精灵组  可以存放多个精灵
        for name in ['ground' , 'pipe' , 'step']:                                #将json文件里存的方块、水管以及地图边界（包括深坑）导入精灵组
            for item in self.map_data[name]:
                self.ground_items_group.add(stuff.Item(item['x'],item['y'],item['width'],item['height'],name))

    def setup_bricks_and_boxes(self):
        self.brick_group = pygame.sprite.Group()
        self.boxes_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()

        if 'brick' in self.map_data:                         #如果砖块在地图的json文件里
            for brick_data in self.map_data['brick']:
                x , y = brick_data['x'] , brick_data['y']
                brick_type = brick_data['type']
                if brick_type == 0:
                    if 'brick_num' in brick_data:  # 如果有brick_num，则是批量处理
                        # TODO batch brick
                        pass
                    else:
                        self.brick_group.add(brick.Brick(x, y, brick_type,None));
                elif brick_type == 1:
                    self.brick_group.add(brick.Brick(x,y,brick_type,self.coin_group))
                else:
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.powerup_group))
        self.brick_group.add(peach.peach())



        if 'box' in self.map_data:  # 如果砖块在地图的json文件里
            for box_data in self.map_data['box']:
                x, y = box_data['x'], box_data['y']
                box_type = box_data['type']
                if box_type == 1:
                    self.boxes_group.add(box.Box(x,y,box_type,self.coin_group))
                else:
                    self.boxes_group.add(box.Box(x,y,box_type,self.powerup_group))                     #将装东西的篮子一起传进去

    def setup_enemies(self):
        self.dying_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.shell_group = pygame.sprite.Group()
        self.enemy_group_dict = {}                                        #按组数将每组敌人存入
        for enemy_group_data in self.map_data['enemy']:
            group = pygame.sprite.Group()
            for enemy_group_id, enemy_list in enemy_group_data.items():
                for enemy_data in enemy_list:
                    group.add(enemy.create_enemy(enemy_data))
                self.enemy_group_dict[enemy_group_id] = group
                #group.empty()

    def setup_checkpoint(self):
        self.checkpoint_group = pygame.sprite.Group()
        for item in self.map_data['checkpoint']:
            x,y,w,h = item['x'],item['y'],item['width'],item['height']
            checkpoint_type = item['type']
            enemy_groupid = item.get('enemy_groupid')
            self.checkpoint_group.add(stuff.Checkpoint(x,y,w,h,checkpoint_type,enemy_groupid))


    def update(self, surface ,keys):

        if self.player.rect.right > 8749:
            self.finished = True
            self.next = 'congradulations'
            self.game_info['sound'] = 'congradulations'

        #print(self.player.rect.x)

        self.current_time = pygame.time.get_ticks()
        self.player.update(keys,self)

        if self.player.dead:
            if self.current_time - self.player.death_timer > 3000:
                self.finished = True
                self.update_game_info()
        elif self.is_frozen():
            pass
        else:
            self.update_player_posision()
            self.check_checkpoint()
            self.check_if_go_die()
            self.update_game_window()
            self.info.update()
            self.brick_group.update()
            self.boxes_group.update()

            self.enemy_group.update(self)
            self.dying_group.update(self)
            self.shell_group.update(self)
            self.coin_group.update()
            self.powerup_group.update(self)

        self.draw(surface)

    def is_frozen(self):                            #在形态改变时冻结地图
        return self.player.state in ['small2big','big2small','big2fire','fire2samll']
    def update_player_posision(self):                     #mario移动

        # if self.player.x_velocity > 5:
        #     self.game_info['sound'] = 'speed_up'
        # else:
        #     self.game_info['sound'] = 'main_theme'

        #x方向
        self.player.rect.x += self.player.x_velocity
        if self.player.rect.x < self.start_x:
            self.player.rect.x = self.start_x
        elif self.player.rect.x > self.end_x:
            self.player.rect.x = self.end_x
        self.check_x_collisions()

        #y方向
        if not self.player.dead:
            self.player.rect.y += self.player.y_velocity
            self.check_y_collisions()

    def check_x_collisions(self):
        check_group = pygame.sprite.Group(self.ground_items_group,self.brick_group,self.boxes_group)
        collided_sprite = pygame.sprite.spritecollideany(self.player, check_group)       #检查一个精灵是否与精灵组里的任意一个精灵有碰撞||返回第一个与mario碰撞的精灵
        if collided_sprite:
            self.adjust_player_x(collided_sprite)

        if self.player.hurt_immune:
            return

        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)
        if enemy:

            if self.player.big:
                # 变大的马里奥撞到敌人会变小
                self.player.state = 'big2small'
                self.player.hurt_immune = True  # 由大变小的时候有一段时间的伤害免疫
                #print(self.player.hurt_immune)
            else:
                # 小马里奥撞到敌人会直接狗带
                self.player.go_die()
                self.game_info['sound'] = 'death_wav'

        shell = pygame.sprite.spritecollideany(self.player,self.shell_group)
        if shell:
            #print(shell.state)
            if shell.state == 'slide':
                if self.player.big:
                    # 变大的马里奥撞到敌人会变小
                    self.player.state = 'big2small'
                    self.player.hurt_immune = True  # 由大变小的时候有一段时间的伤害免疫
                    # print(self.player.hurt_immune)
                else:
                    # 小马里奥撞到敌人会直接狗带
                    self.player.go_die()
                    self.game_info['sound'] = 'death_wav'
            else:
                if self.player.rect.x < shell.rect.x:
                    shell.x_vel = 10
                    shell.rect.x += 40
                    shell.direction = 1
                else:
                    shell.x_vel = -10
                    shell.rect.x -= 14
                    shell.direction = 0
                shell.state = 'slide'
        powerup = pygame.sprite.spritecollideany(self.player,self.powerup_group)
        if powerup:
            if powerup.name == 'mushroom':
                # 蘑菇让玩家变大
                self.player.state = 'small2big'
                powerup.kill()
            elif powerup.name == 'fireball':
                pass
            elif powerup.name == 'fireflower':
                # 火焰花让玩家能够发射子弹
                self.player.state = 'big2fire'
                powerup.kill()


    def check_y_collisions(self):

        ground_item = pygame.sprite.spritecollideany(self.player,self.ground_items_group)
        brick = pygame.sprite.spritecollideany(self.player, self.brick_group)
        box = pygame.sprite.spritecollideany(self.player, self.boxes_group)
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)

        if brick and box:
            to_brick = abs(self.player.rect.centerx - brick.rect.centerx)
            to_box = abs(self.player.rect.centerx - box.rect.centerx)
            if to_brick > to_box:
                brick = None
            else:
                box = None

        if ground_item:
            self.adjust_player_y(ground_item)
        elif brick:
            self.adjust_player_y(brick)
        elif box:
            self.adjust_player_y(box)
        elif enemy:
            if self.player.hurt_immune:
                return
            self.enemy_group.remove(enemy)
            if enemy.name == 'koopa':
                self.shell_group.add(enemy)
            else:
                self.dying_group.add(enemy)
            if self.player.y_velocity < 0:            #从下往上顶
                how = 'bumped'
                enemy.go_die(how, 1 if self.player.face_right else -1)
            elif self.player.y_velocity > 0:                                    #从上往下，踩死
                how = 'trampled'
                self.player.state = 'jump'
                self.player.rect.bottom = enemy.rect.top
                self.player.y_velocity = self.player.jump_vel * 0.8            #一个小跳
                enemy.go_die(how,1 if self.player.face_right else -1)
            #print("猜到了")

        self.check_will_fall(self.player)
        #print(self.player.state)


    def check_will_fall(self,sprite):
        sprite.rect.y += 1                                                   #试探性下落一个像素，如果没有碰撞则修改状态为下落
        check_group = pygame.sprite.Group(self.ground_items_group,self.brick_group,self.boxes_group)
        collided = pygame.sprite.spritecollideany(sprite,check_group)
        if not collided and sprite.state != 'jump' and not self.is_frozen():
            sprite.state = 'fall'
        sprite.rect.y -= 1                                                  #还原


    def adjust_player_x(self,sprite):
        if self.player.rect.x < sprite.rect.x:
            self.player.rect.right = sprite.rect.left
        else:
            self.player.rect.left = sprite.rect.right
        self.player.x_velocity = 0

    def adjust_player_y(self,sprite):

        #向下
        if self.player.rect.y < sprite.rect.y:
            self.player.y_velocity = 0
            self.player.rect.bottom = sprite.rect.top
            self.player.state = 'walk'
        #向上顶到了
        else:
            self.player.y_velocity = 7
            self.player.rect.top = sprite.rect.bottom
            self.player.state = 'fall'

            self.is_enemy_on(sprite)                 #是否上方有敌人

            if sprite.name == 'box':
                if sprite.state == 'rest':
                    sprite.go_bumped()
            if sprite.name == 'brick':
                if self.player.big and sprite.brick_type == 0:                #mario处于变大状态并且砖块里面没东西
                    sprite.smashed(self.dying_group)
                else:
                    sprite.go_bumped()

    def is_enemy_on(self, sprite):
        # 试探性地向上一个像素，并和敌人组进行碰撞检测
        sprite.rect.y -= 1
        enemy = pygame.sprite.spritecollideany(sprite, self.enemy_group)
        if enemy:
            self.enemy_group.remove(enemy)
            self.dying_group.add(enemy)
            if sprite.rect.centerx > enemy.rect.centerx:                                   #enemy被顶飞的方向
                enemy.go_die('bumped',-1)
            else:
                enemy.go_die('bumped',1)
        sprite.rect.y += 1

    def update_game_window(self):                                 #窗口跟随

        third = self.game_window.x + self.game_window.width / 3            #计算窗口的1/3位置
        if self.player.x_velocity > 0 and self.player.rect.centerx > third and self.game_window.right< self.end_x:
            self.start_x = self.game_window.x                              #不能走回头路
            self.game_window.x += self.player.x_velocity




    def draw(self, surface):
        #surface.fill((0,255,0))
        #surface.blit(self.background, (0,0),self.game_window)             #将game_window所在位置画到屏幕上
        self.game_ground.blit(self.background,self.game_window,self.game_window)
        self.game_ground.blit(self.player.image,self.player.rect)
        self.powerup_group.draw(self.game_ground)
        self.brick_group.draw(self.game_ground)
        self.boxes_group.draw(self.game_ground)

        self.enemy_group.draw(self.game_ground)
        self.dying_group.draw(self.game_ground)
        self.shell_group.draw(self.game_ground)
        self.coin_group.draw(self.game_ground)


        surface.blit(self.game_ground,(0,0),self.game_window)
        #surface.blit(self.brick.image)
        self.info.draw(surface)
        # surface.blit(self.player.image,self.player.rect)

    def check_checkpoint(self):
        checkpoint = pygame.sprite.spritecollideany(self.player,self.checkpoint_group)               #检查点被mario碰到
        if checkpoint:
            if checkpoint.checkpoint_type == 0 :
                self.enemy_group.add(self.enemy_group_dict[str(checkpoint.enemy_groupid)])
            checkpoint.kill()

    def check_if_go_die(self):
        if self.player.rect.y > C.SCREEN_H:                        #下落到边界以外，触发死亡
            self.player.go_die()
            self.game_info['sound'] = 'death_wav'


    def update_game_info(self):                         #死亡后更新数据
        if self.player.dead:
            self.game_info['lives'] -= 1
        if self.game_info['lives'] == 0:                          #死亡后选择结束还是重生
            self.next = 'game_over'
        else:
            self.next = 'load_screen'

