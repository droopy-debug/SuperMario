#音乐

import pygame
from resources import music
class Music:
    def __init__(self):
        pygame.mixer.init()
        self.sound = {}
        self.setup_resource()
        self.state = 1
        self.current_music = None

    def setup_resource(self):
        audio_list = {
            'main_theme': "resources/music/main_theme.ogg",
            'death_wav': "resources/music/death.wav",
            'game_over':'resources/music/game_over.ogg',
            'speed_up' :'resources/music/main_theme_sped_up.ogg',
            'congradulations':'resources/music/world_clear.wav'
        }
        for key, path in audio_list.items():
            self.sound[key] = pygame.mixer.Sound(path)

    def play_music(self, state):
        # 停止当前播放的音乐
        if self.current_music:
            self.current_music.stop()

        # 播放新的音乐
        self.current_music = self.sound.get(state)
        if self.current_music:
            self.current_music.play()

    def update(self,state):
        # print(state)
        self.play_music(state)
