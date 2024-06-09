#游戏主要入口
import pygame
from source.state import main_menu,load_screen,level
from source import tools

def main():
    #game = tools.Game()

    state_dict = {
        'main_menu': main_menu.MainMenu(),
        'load_screen': load_screen.load_Screen(),
        'level': level.level(),
        'game_over':load_screen.GameOver()
    }

    game = tools.Game(state_dict,'main_menu')       #让主控类来决定状态之间的变化


    #state = main_menu.MainMenu()
    #state = load_screen.LoadScreen()
    #state = level.level()
    game.run()

if __name__ == '__main__':             #代码被当做脚本执行的时候才运行里面的main
    main()
