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
        self.info2 = ''
        self.mod_item_kill = False
        self.electricity = 0
        self.facings = ["вправо", "вниз", "влево", "вверх"]
        self.facing_id = 0

        self.build_object = Conveyor
        self.build_objects = (Conveyor, Mine, Lab, PullConveyor, Furnaсe, SolarPanel, Foundry,
                              TrashBox, Level1AssemblyMachine, Level2AssemblyMachine, LabAssemblyMachine)
        self.info_build_object = 'Conveyor'
        self.info_build_objects = ('Conveyor', 'Mine', 'Lab', 'PullConveyor', 'Furnace', 'SolarPanel', 'Foundry',
                                   'TrashBox', 'Level1AssemblyMachine', 'Level2AssemblyMachine', 'LabAssemblyMachine')
        self.last_wheel = 200

        self.right_click = False
        self.left_click = False

        self.gamemode = 'creative'
        self.can_use_foundry = False

        self.all = pygame.sprite.LayeredUpdates()  # абсолютно все  !!! добавлять все спрайты !!!
        self.dynamic = pygame.sprite.LayeredUpdates()  # движующиеся по экрану
        self.static = pygame.sprite.LayeredUpdates()  # не движующиеся по экрану
        self.storage = pygame.sprite.LayeredUpdates()  # для всех классов со внутринем хранилищем
        self.ores = pygame.sprite.LayeredUpdates()
        self.builds = pygame.sprite.LayeredUpdates()  # для всех построек
        self.interface = pygame.sprite.LayeredUpdates()  # для всего интерфейса
        self.items = pygame.sprite.LayeredUpdates()  # для всех предметов
        self.player = pygame.sprite.LayeredUpdates()
        self.assemblers = pygame.sprite.LayeredUpdates()

    def update(self):
        self.all.update()

    def draw(self):
        self.screen.fill(BLACK)
        self.all.draw(self.screen)

        self.clock.tick(FPS)
        pygame.display.update()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.runnig = False
            if event.type == pygame.KEYDOWN:
                self.key_event_react(event)

    def key_event_react(self, event):
        if event.key == pygame.K_f:
            if self.mod_item_kill:
                self.mod_item_kill = False
            else:
                self.mod_item_kill = True
        if event.key == pygame.K_g:
            self.change_receipt()
        if event.key == pygame.K_1:
            self.build_object = Conveyor
            self.info_build_object = 'Conveyor'
        if event.key == pygame.K_2:
            self.build_object = PullConveyor
            self.info_build_object = 'PullConveyor'
        if event.key == pygame.K_3:
            self.build_object = Mine
            self.info_build_object = 'Mine'
        if event.key == pygame.K_4:
            self.build_object = Furnaсe
            self.info_build_object = 'Furnaсe'
        if event.key == pygame.K_5:
            self.build_object = Foundry
            self.info_build_object = 'Foundry'
        if event.key == pygame.K_6:
            self.build_object = Level1AssemblyMachine
            self.info_build_object = 'Level1AssemblyMachine'
        if event.key == pygame.K_7:
            self.build_object = Level2AssemblyMachine
            self.info_build_object = 'Level2AssemblyMachine'
        if event.key == pygame.K_8:
            self.build_object = LabAssemblyMachine
            self.info_build_object = 'LabAssemblyMachine'
        if event.key == pygame.K_9:
            self.build_object = Lab
            self.info_build_object = 'Lab'
        if event.key == pygame.K_0:
            self.build_object = TrashBox
            self.info_build_object = 'TrashBox'
        if event.key == pygame.K_e:
            self.rotate_clockwise()
        if event.key == pygame.K_q:
            self.rotate_anticlockwise()
        if event.key == pygame.K_r:
            self.change_build_object()
        if event.key == pygame.K_o:
            self.exp += 1000

    def rotate_clockwise(self):
        self.facing_id += 1
        if self.facing_id >= 4:
            self.facing_id = 0
        self.facing = self.facings[self.facing_id]

    def rotate_anticlockwise(self):
        self.facing_id -= 1
        if self.facing_id <= -1:
            self.facing_id = 3
        self.facing = self.facings[self.facing_id]

    def change_build_object(self):
        if pygame.time.get_ticks() - self.last_wheel >= 200:
            self.last_wheel = pygame.time.get_ticks()
            index = self.build_objects.index(self.build_object)
            if index != len(self.build_objects) - 1:
                next = index + 1
            else:
                next = 0
            self.build_object = self.build_objects[next]
            self.info_build_object = self.info_build_objects[next]

    def change_receipt(self):
        assemblers = pygame.sprite.spritecollide(self.mouse, self.assemblers, False)
        if len(assemblers) == 0:
            return
        assembler = assemblers[0]
        assembler.change_receipt()

    def main(self): #игровой цикл
        while self.runnig:
            self.events()
            self.draw()
            self.update()
            self.check_exp()
            self.react_mouse_click()

        self.runnig = False

    def react_mouse_click(self):
        self.right_click = False
        self.left_click = False
        pressed = pygame.mouse.get_pressed()
        if pressed[2]:
            self.right_click = True
        if pressed[0]:
            self.left_click = True
        self.click = True

    def check_exp(self):
        if not self.can_use_foundry:
            if self.exp >= WIN:
                self.can_use_foundry = True
                self.exp = 0
                self.electricity = 0
                self.create_map()

    def intro_screen(self):
        Button(self, 500, 500, self.create_map)
        Mouse(self)

    def create_map(self):
        self.screen.fill('black')
        for sprite in self.all:
            sprite.kill()

        self.mouse = Mouse(self)
        for i in range(2, 5):
            for j in range(2, 5):
                Ground(self, j, i)

        for kol in range(63):
            self.create_field1(random.randint(-127, 127), random.randint(-127, 127), IronOre)
            self.create_field1(random.randint(-127, 127), random.randint(-127, 127), CopperOre)
            self.create_field1(random.randint(-127, 127), random.randint(-127, 127), Coal)
            self.create_field1(random.randint(-127, 127), random.randint(-127, 127), Gold)
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

