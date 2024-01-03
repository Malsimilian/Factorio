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
        self.playing = False  # момент начала игры
        self.click = False  # нажаата ли ЛКМ
        self.facing = "вниз"  # направление модулей

        self.build_object = Conveyor
        self.build_objects = (Conveyor, Mine, Lab)
        self.last_wheel = 200

        self.all = pygame.sprite.LayeredUpdates()  # абсолютно все  !!! добавлять все спрайты !!!
        self.dynamic = pygame.sprite.LayeredUpdates()  # движующиеся по экрану
        self.static = pygame.sprite.LayeredUpdates()  # не движующиеся по экрану
        self.mouse = pygame.sprite.LayeredUpdates()  # для курсора
        self.storage = pygame.sprite.LayeredUpdates()  # для всех классов со внутринем хранилищем
        self.ores = pygame.sprite.LayeredUpdates()

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
        self.right_click = False
        self.left_click = False
        for event in pygame.event.get():
            self.event = event
            if self.event.type == pygame.QUIT:
                self.runnig = False
            if self.event.type == pygame.MOUSEBUTTONDOWN:
                pressed = pygame.mouse.get_pressed()
                if pressed[2]:
                    self.right_click = True
                if pressed[0]:
                    self.left_click = True
                if pressed[1]:
                    self.change_build_object()
                self.click = True

    def change_build_object(self):
        if pygame.time.get_ticks() - self.last_wheel >= 200:
            self.last_wheel = pygame.time.get_ticks()
            index = self.build_objects.index(self.build_object)
            if index != len(self.build_objects) - 1:
                next = index + 1
            else:
                next = 0
            self.build_object = self.build_objects[next]
            print('Текущий обЪект' + str(self.build_object))


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

        Mouse(self)
        for i in range(5):
            for j in range(5):
                Ground(self, j, i)

        for kol in range(128):
            Ore(self, random.randint(0, 127), random.randint(0, 127))

        for sprite in self.all:
            sprite.rect.x -= 2560
            sprite.rect.y -= 2560

        self.playing = True
        Facing(self)
        Player(self)


g = Game()
#g.intro_screen()
g.create_map()
while g.runnig:
    g.main()
pygame.quit()
sys.exit()