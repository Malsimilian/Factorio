import pygame
import sys
import random
from sprite import *
from config import *

class Game:
    def __init__(self):
        #иниацилизация
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.runnig = True
        self.click = False  # нажаата ли ЛКМ

        self.all = pygame.sprite.LayeredUpdates()  # абсолютно все  !!! добавлять все спрайты !!!
        self.dynamic = pygame.sprite.LayeredUpdates()  # движующиеся по экрану
        self.static = pygame.sprite.LayeredUpdates()  # не движующиеся по экрану
        self.mouse = pygame.sprite.LayeredUpdates()  # для курсора
        self.storage = pygame.sprite.LayeredUpdates()  # для всех классов со внутринем хранилищем (конвейер, конструктор и т.п)

    def update(self):
        self.all.update()
        for sprite in self.storage:
            sprite.next()

    def draw(self):
        self.screen.fill(BLACK)
        self.all.draw(self.screen)

        self.clock.tick(FPS)
        pygame.display.update()

    def events(self):
        self.click = False
        for event in pygame.event.get():
            self.event = event
            if self.event.type == pygame.QUIT:
                self.runnig = False

            if self.event.type == pygame.MOUSEBUTTONDOWN:
                self.click = True

    def main(self): #игровой цикл
        while self.runnig:
            self.events()
            self.draw()
            self.update()

        self.runnig = False

    def intro_screen(self):
        Button(self, 500, 500, self.create_map)
        Mouse(self)

    def create_map(self):
        for sprite in self.all:
            sprite.kill()

        for i in range(5):
            for j in range(5):
                Ground(self, j, i)

        for kol in range(16):
            Ore(self, random.randint(0, 127), random.randint(0, 127))

        for sprite in self.all:
            sprite.rect.x -= 2560
            sprite.rect.y -= 2560

        Player(self)

g = Game()
g.intro_screen()
#g.create_map()
while g.runnig:
    g.main()
pygame.quit()
sys.exit()