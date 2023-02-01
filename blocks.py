from pygame import *
import os
import pyganim

PLATFORM_WIDTH = 32
PLATFORM_HEIGHT = 32
PLATFORM_COLOR = "#000000"
ICON_DIR = os.path.dirname(__file__) #  Полный путь к каталогу с файлами

 
class Platform(sprite.Sprite):
    '''Класс спрайта-платформы'''
    def __init__(self, x, y):
        '''Конструктор класса'''
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image.fill(Color(PLATFORM_COLOR))
        self.image = image.load("%s/blocks/platform.png" % ICON_DIR)
        self.image.set_colorkey(Color(PLATFORM_COLOR))
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        
class BlockDie(Platform):
    '''Класс спрайта-платформы'''
    def __init__(self, x, y):
        '''Конструктор класса'''
        Platform.__init__(self, x, y)
        self.image = image.load("%s/blocks/dieBlock.png" % ICON_DIR)
        self.rect = Rect(x + PLATFORM_WIDTH / 4, y + PLATFORM_HEIGHT / 4, PLATFORM_WIDTH - PLATFORM_WIDTH / 2, PLATFORM_HEIGHT - PLATFORM_HEIGHT / 2)

class Comp(Platform):
    '''Класс спрайта-платформы'''
    def __init__(self, x, y):
        '''Конструктор класса'''
        Platform.__init__(self, x, y)
        self.image = image.load("%s/blocks/Comp.png" % ICON_DIR)

