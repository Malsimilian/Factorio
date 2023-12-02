import pygame
import sys
from sprite import *
from config import *

class Game:
    def __init__(self):
        #иниацилизация
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.runnig = True

    def new(self):
        self.playing = True


g = Game()
g.new()
while g.runnig:
    pass
pygame.quit()
sys.exit()
