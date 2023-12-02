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

    def new(self):
        self.runnig = True
        self.all = pygame.sprite.LayeredUpdates()

        Player(self, 10, 10)

    def update(self):
        self.all.update()

    def draw(self):
        self.all.draw(self.screen)

        self.clock.tick(FPS)
        pygame.display.update()

    def events(self):
        for event in pygame.event.get():
            self.screen.fill((0, 0, 0))
            self.event = event
            if self.event.type == pygame.QUIT:
                self.runnig = False

    def main(self): #игровой цикл
        while self.runnig:
            self.events()
            self.update()
            self.draw()
        self.runnig = False


g = Game()
g.new()
while g.runnig:
    g.main()
pygame.quit()
sys.exit()
