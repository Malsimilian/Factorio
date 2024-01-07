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
        self.facing = "вправо"  # направление модулей
        self.exp = 0
        self.info = ''
        self.mod_item_kill = False

        self.build_object = Conveyor
        self.build_objects = (Conveyor, Mine, Lab, PullConveyor, AssemblyMachine, Furnaсe)
        self.info_build_object = 'Conveyor'
        self.info_build_objects = ('Conveyor', 'Mine', 'Lab', 'PullConveyor', 'AssemblyMachine', 'Furnace')
        self.last_wheel = 200

        self.receipt = IronStick
        self.receipts = [IronStick, IronGeer]
        self.info_receipt = 'IronStick'
        self.info_receipts = ['IronStick', 'IronGeer']
        self.last_wheel_receipt = 200

        self.all = pygame.sprite.LayeredUpdates()  # абсолютно все  !!! добавлять все спрайты !!!
        self.dynamic = pygame.sprite.LayeredUpdates()  # движующиеся по экрану
        self.static = pygame.sprite.LayeredUpdates()  # не движующиеся по экрану
        self.mouse = pygame.sprite.LayeredUpdates()  # для курсора
        self.storage = pygame.sprite.LayeredUpdates()  # для всех классов со внутринем хранилищем
        self.ores = pygame.sprite.LayeredUpdates()
        self.builds = pygame.sprite.LayeredUpdates()  # для всех построек
        self.interface = pygame.sprite.LayeredUpdates()  # для всего интерфейса
        self.items = pygame.sprite.LayeredUpdates()  # для всех предметов
        self.player = pygame.sprite.LayeredUpdates()

    def update(self):
        self.all.update()

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
            if event.type == pygame.QUIT:
                self.runnig = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pressed = pygame.mouse.get_pressed()
                if pressed[2]:
                    self.right_click = True
                if pressed[0]:
                    self.left_click = True
                if pressed[1]:
                    self.change_build_object()
                self.click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    if self.mod_item_kill:
                        self.mod_item_kill = False
                    else:
                        self.mod_item_kill = True
                if event.key == pygame.K_g:
                    self.change_receipt()

    def change_build_object(self):
        if pygame.time.get_ticks() - self.last_wheel >= 200:
            self.last_wheel = pygame.time.get_ticks()
            index = self.build_objects.index(self.build_object)
            if index != len(self.build_objects) - 1:
                next = index + 1
            else:
                next = 0
            self.build_object = self.build_objects[next]

            index = self.info_build_objects.index(self.info_build_object)
            if index != len(self.info_build_objects) - 1:
                next = index + 1
            else:
                next = 0
            self.info_build_object = self.info_build_objects[next]

    def change_receipt(self):
        if pygame.time.get_ticks() - self.last_wheel_receipt >= 200:
            self.last_wheel = pygame.time.get_ticks()
            index = self.receipts.index(self.receipt)
            if index != len(self.receipts) - 1:
                next = index + 1
            else:
                next = 0
            self.receipt = self.receipts[next]

            index = self.info_receipts.index(self.info_receipt)
            if index != len(self.info_receipts) - 1:
                next = index + 1
            else:
                next = 0
            self.info_receipt = self.info_receipts[next]

    def main(self): #игровой цикл
        while self.runnig:
            self.events()
            self.draw()
            self.update()
            self.check_win()
            self.update_info()

        self.runnig = False

    def check_win(self):
        if self.exp >= WIN:
            self.is_win = True
        else:
            self.is_win = False

    def intro_screen(self):
        Button(self, 500, 500, self.create_map)
        Mouse(self)

    def update_info(self, info=''):
        if self.is_win:
            self.info = self.info_build_object + ' ' + self.info_receipt + f' {self.exp} ' + info + 'WIN'
        else:
            self.info = self.info_build_object + ' ' + self.info_receipt + f' {self.exp} ' + info

    def create_map(self):
        for sprite in self.all:
            sprite.kill()

        Mouse(self)
        for i in range(5):
            for j in range(5):
                Ground(self, j, i)

        for kol in range(63):
            self.create_field1(random.randint(0, 127), random.randint(0, 127), IronOre)
            self.create_field1(random.randint(0, 127), random.randint(0, 127), CopperOre)
        for ore1 in self.ores:
            for ore2 in self.ores:
                if ore1 != ore2 and ore1.rect == ore2.rect:
                    ore2.kill()

        for sprite in self.all:
            sprite.rect.x -= 2560
            sprite.rect.y -= 2560

        self.playing = True
        Facing(self)
        Info(self)
        Player(self)

    def create_field1(self, x, y, ore):
        for i in range(random.randint(5, 10)):
            for j in range(random.randint(5, 10)):
                if random.random() > 0.5:
                    ore(self, x + i, y + j)


g = Game()
#g.intro_screen()
g.create_map()
while g.runnig:
    g.main()
pygame.quit()
sys.exit()