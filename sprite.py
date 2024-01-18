import pygame
from config import *
import sqlite3


class Interface(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = 5
        self.groups = game.all, game.interface
        super().__init__(self.groups)


class Info(Interface):
    def __init__(self, game):
        super().__init__(game)

        self.image = pygame.Surface([SIDE * 20, SIDE * 4])
        self.image.fill((200, 200, 200))

        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

        self.last = 0

    def update(self):
        if pygame.time.get_ticks() - self.last >= 10:
            self.last = pygame.time.get_ticks()
            self.image.fill((200, 200, 200))
        f1 = pygame.font.Font(None, 60)
        text1 = f1.render('object: ' + str(self.game.info_build_object), True,
                          (0, 0, 0))
        text2 = f1.render('exp: ' + str(self.game.exp), True,
                          (0, 0, 0))
        text3 = f1.render('electricity: ' + str(self.game.electricity), True,
                          (0, 0, 0))
        text4 = f1.render('Вы не можете строить литейную', True,
                          (0, 0, 0))
        text5 = f1.render('Вы можете строить литейную', True,
                          (0, 0, 0))
        self.image.blit(text1, (0, 0, SIDE * 16, SIDE))
        self.image.blit(text2, (0, SIDE, SIDE * 16, SIDE))
        self.image.blit(text3, (0, SIDE * 2, SIDE * 16, SIDE))
        if self.game.can_use_foundry:
            self.image.blit(text5, (0, SIDE * 3, SIDE * 20, SIDE))
        else:
            self.image.blit(text4, (0, SIDE * 3, SIDE * 20, SIDE))


class Facing(Interface):
    def __init__(self, game):
        super().__init__(game)

        self.image = pygame.Surface([SIDE * 2, SIDE * 2])
        self.image.blit(pygame.image.load("img/Направление_вправо.png"), (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = WIN_WIDTH - 80
        self.rect.y = 0

    def update(self):
        self.image.blit(pygame.image.load("img/Направление_" + self.game.facing + ".png"), (0, 0))


class BuildObject(pygame.sprite.Sprite):
    def __init__(self, game, x, y, facing, name, time):
        self.game = game
        self._layer = 2
        if name == 'Level1_Assembling_machine' or name == 'Lab_Assembling_machine' or \
                name == 'Level2_Assembling_machine':
            self.groups = self.game.all, self.game.dynamic, self.game.storage, self.game.builds, self.game.assemblers
        else:
            self.groups = self.game.all, self.game.dynamic, self.game.storage, self.game.builds

        super().__init__(self.groups)

        self.image = pygame.Surface([SIDE, SIDE])
        if facing is not None:
            self.image.blit(pygame.image.load(f"img/{name}_{facing}.png"), (0, 0))
        else:
            self.image.blit(pygame.image.load(f"img/{name}.png"), (0, 0))
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = x * SIDE
        self.rect.y = y * SIDE

        self.name = name

        self.last = 0
        self.facing = facing
        self.item = None
        self.tech_item = TechItem(game, x, y)
        self.last_electricity = 0
        self.time = time
        self.entry_allowed = True

    def update(self):
        self.electricity()

    def electricity(self):
        if pygame.time.get_ticks() - self.last_electricity < self.time:
            return
        if isinstance(self, SolarPanel):
            return
        self.last_electricity = pygame.time.get_ticks()
        self.game.electricity -= ELECTRICITY

    def can_move(self):
        if self.facing == 'вправо':
            for item in self.game.items:
                if item.rect.x - 40 == self.item.rect.x and item.rect.y == self.item.rect.y and not isinstance(item, TechItem):
                    return False
        elif self.facing == 'влево':
            for item in self.game.items:
                if item.rect.x + 40 == self.item.rect.x and item.rect.y == self.item.rect.y and not isinstance(item, TechItem):
                    return False
        elif self.facing == 'вниз':
            for item in self.game.items:
                if item.rect.x == self.item.rect.x and item.rect.y - 40 == self.item.rect.y and not isinstance(item, TechItem):
                    return False
        elif self.facing == 'вверх':
            for item in self.game.items:
                if item.rect.x == self.item.rect.x and item.rect.y + 40 == self.item.rect.y and not isinstance(item, TechItem):
                    return False
        return True

    def find_item(self):
        for item in self.game.items:
            if item.object == self and not isinstance(item, TechItem):
                self.item = item
                break

    def prekill(self):
        pass


class Mine(BuildObject):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, facing, 'Бур', MINE_TIME)
        self.remove(self.game.storage)
        self.item = TechItem(game, x, y)
        self.ore = None
        hits = pygame.sprite.spritecollide(self, self.game.ores, False)
        if hits:
            if isinstance(hits[0], IronOre):
                self.ore = ItemIronOre
            elif isinstance(hits[0], CopperOre):
                self.ore = ItemCopperOre
            elif isinstance(hits[0], Coal):
                self.ore = ItemCoal
            elif isinstance(hits[0], Gold):
                self.ore = ItemGold

    def update(self):
        if not self.can_work():
            return
        super().update()
        self.get_ore()

    def get_ore(self):
        ore = self.ore(self.game, self.rect.x / 40, self.rect.y / 40)
        if self.facing == 'вправо':
            ore.move(SIDE, 0)
        elif self.facing == 'влево':
            ore.move(-SIDE, 0)
        elif self.facing == 'вниз':
            ore.move(0, SIDE)
        elif self.facing == 'вверх':
            ore.move(0, -SIDE)

    def can_work(self):
        if pygame.time.get_ticks() - self.last < self.time:
            return False
        self.last = pygame.time.get_ticks()
        if not self.can_move():
            return False
        if self.ore is None:
            return False
        if self.game.electricity < ELECTRICITY:
            return False
        return True


class Conveyor(BuildObject):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, facing, 'Конвейер', CONVEYOR_TIME)

    def update(self):
        if not self.can_work():
            return
        super().update()
        self.move_item()

    def move_item(self):
        if self.facing == 'вправо':
            self.item.move(SIDE, 0)
        elif self.facing == 'влево':
            self.item.move(-SIDE, 0)
        elif self.facing == 'вниз':
            self.item.move(0, SIDE)
        elif self.facing == 'вверх':
            self.item.move(0, -SIDE)
        self.item = None

    def can_work(self):
        self.find_item()
        if self.item is None:
            return False
        if pygame.time.get_ticks() - self.item.last < self.time:
            return False
        if not self.can_move():
            return False
        if self.game.electricity < ELECTRICITY:
            return False
        if self.find_object() is not None:
            if not self.find_object().entry_allowed:
                return False
            if isinstance(self.find_object(), Foundry):
                if not self.can_move_to_foundry():
                    return False
            if isinstance(self.find_object(), Level1AssemblyMachine):
                if not self.can_move_to_assembler1():
                    return False
            if isinstance(self.find_object(), Level2AssemblyMachine):
                if not self.can_move_to_assembler2():
                    return False
            if isinstance(self.find_object(), LabAssemblyMachine):
                if not self.can_move_to_lab_assembler():
                    return False
        return True

    def can_move_to_foundry(self):
        if not self.find_object().iron_entry_allowed and isinstance(self.item, IronPlate):
            return False
        if not self.find_object().coal_entry_allowed and isinstance(self.item, ItemCoal):
            return False
        return True

    def can_move_to_assembler1(self):
        if not self.find_object().entry_iron and isinstance(self.item, IronPlate):
            return False
        if not self.find_object().entry_copper and isinstance(self.item, CopperPlate):
            return False
        if not self.find_object().entry_geer and isinstance(self.item, IronGeer):
            return False
        if not self.find_object().entry_stick and isinstance(self.item, IronStick):
            return False
        if not self.find_object().entry_cable and isinstance(self.item, CopperCable):
            return False
        return True

    def can_move_to_assembler2(self):
        if not self.find_object().entry_steel and isinstance(self.item, Steel):
            return False
        if not self.find_object().entry_chip and isinstance(self.item, Chip):
            return False
        if not self.find_object().entry_frame and isinstance(self.item, SteelFrame):
            return False
        if not self.find_object().entry_lpp and isinstance(self.item, LabPocket1Part1):
            return False
        if not self.find_object().entry_gold and isinstance(self.item, ItemGold):
            return False
        return True

    def can_move_to_lab_assembler(self):
        if not self.find_object().entry_lp1p1 and isinstance(self.item, LabPocket1Part1):
            return False
        if not self.find_object().entry_lp1p2 and isinstance(self.item, Chip):
            return False
        if not self.find_object().entry_lp2p1 and isinstance(self.item, Engine):
            return False
        if not self.find_object().entry_lp2p2 and isinstance(self.item, PowerChip):
            return False
        return True

    def find_object(self):
        if self.facing == 'вправо':
            for object in self.game.builds:
                if object.rect.x - 40 == self.rect.x and object.rect.y == self.rect.y:
                    return object
        elif self.facing == 'влево':
            for object in self.game.builds:
                if object.rect.x + 40 == self.rect.x and object.rect.y == self.rect.y:
                    return object
        elif self.facing == 'вниз':
            for object in self.game.builds:
                if object.rect.x == self.rect.x and object.rect.y - 40 == self.rect.y:
                    return object
        elif self.facing == 'вверх':
            for object in self.game.builds:
                if object.rect.x == self.rect.x and object.rect.y + 40 == self.rect.y:
                    return object
        return None


class PullConveyor(Conveyor):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, facing)
        self.image.blit(pygame.image.load(f"img/Вытягивающий_Конвейер_{facing}.png"), (0, 0))

    def update(self):
        self.pull_item()
        super().update()

    def pull_item(self):
        previous_item = self.find_previous_item()
        self.find_item()
        if self.item is not None:
            return
        if previous_item is None:
            return
        previous_object = self.find_previous_object()
        if previous_object is None or isinstance(previous_object, PullConveyor):
            return
        elif isinstance(previous_object, Furnaсe):
            if isinstance(previous_item, IronPlate) or isinstance(previous_item, CopperPlate):
                self.pull_move(previous_item)
        elif isinstance(previous_object, Foundry):
            if isinstance(previous_item, Steel):
                self.pull_move(previous_item)
        elif isinstance(previous_object, Level1AssemblyMachine):
            if isinstance(previous_item, LabPocket1Part1) or isinstance(previous_item, Chip):
                self.pull_move(previous_item)
            elif isinstance(previous_item, CopperCable) and previous_object.can_pull_cable:
                self.pull_move(previous_item)
            elif(isinstance(previous_item, IronGeer) or isinstance(previous_item, IronStick)) and \
                previous_object.can_pull_geer_or_stick:
                self.pull_move(previous_item)
        elif isinstance(previous_object, Level2AssemblyMachine):
            if isinstance(previous_item, PowerChip) or isinstance(previous_item, Engine):
                self.pull_move(previous_item)
            elif isinstance(previous_item, SteelFrame) and previous_object.can_pull_frame:
                self.pull_move(previous_item)
        elif isinstance(previous_object, LabAssemblyMachine):
            if isinstance(previous_item, LabPacket1) or isinstance(previous_item, LabPacket2):
                self.pull_move(previous_item)
        elif isinstance(previous_object, Conveyor):
            self.pull_move(previous_item)


    def pull_move(self, previous_item):
        if self.facing == 'вправо':
            previous_item.move(SIDE, 0)
        elif self.facing == 'влево':
            previous_item.move(-SIDE, 0)
        elif self.facing == 'вниз':
            previous_item.move(0, SIDE)
        elif self.facing == 'вверх':
            previous_item.move(0, -SIDE)

    def find_previous_object(self):
        if self.facing == 'вправо':
            for object in self.game.builds:
                if object.rect.x + 40 == self.rect.x and object.rect.y == self.rect.y:
                    return object
        elif self.facing == 'влево':
            for object in self.game.builds:
                if object.rect.x - 40 == self.rect.x and object.rect.y == self.rect.y:
                    return object
        elif self.facing == 'вниз':
            for object in self.game.builds:
                if object.rect.x == self.rect.x and object.rect.y + 40 == self.rect.y:
                    return object
        elif self.facing == 'вверх':
            for object in self.game.builds:
                if object.rect.x == self.rect.x and object.rect.y - 40 == self.rect.y:
                    return object
        return None

    def find_previous_item(self):
        if self.facing == 'вправо':
            for item in self.game.items:
                if item.rect.x + 40 == self.tech_item.rect.x and item.rect.y == self.tech_item.rect.y and not isinstance(item, TechItem):
                    return item
        elif self.facing == 'влево':
            for item in self.game.items:
                if item.rect.x - 40 == self.tech_item.rect.x and item.rect.y == self.tech_item.rect.y and not isinstance(item, TechItem):
                    return item
        elif self.facing == 'вниз':
            for item in self.game.items:
                if item.rect.x == self.tech_item.rect.x and item.rect.y + 40 == self.tech_item.rect.y and not isinstance(item, TechItem):
                    return item
        elif self.facing == 'вверх':
            for item in self.game.items:
                if item.rect.x == self.tech_item.rect.x and item.rect.y - 40 == self.tech_item.rect.y and not isinstance(item, TechItem):
                    return item
        return None


class Lab(BuildObject):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, None, 'Лаборатория', LAB_TIME)

    def update(self):
        if not self.can_work():
            return
        super().update()
        self.research()

    def research(self):
        self.game.exp += self.item.exp
        self.item.kill()
        self.item = None

    def can_work(self):
        if pygame.time.get_ticks() - self.last < self.time:
            return False
        self.last = pygame.time.get_ticks()
        self.find_item()
        if self.item is None:
            return False
        if self.game.electricity < ELECTRICITY:
            return False
        return True


class AssemblyMachine(BuildObject):
    def __init__(self, game, x, y, name, time):
        super().__init__(game, x, y, None, name, time)
        self.receipt = None
        self.receipts = []

    def update(self):
        super().update()

    def change_receipt(self):
        index = self.receipts.index(self.receipt)
        if index != len(self.receipts) - 1:
            next = index + 1
        else:
            next = 0
        self.receipt = self.receipts[next]


class Level1AssemblyMachine(AssemblyMachine):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, 'Level1_Assembling_machine', ASSEMBLY_MACHINE_TIME)
        self.receipt = 'IronStick'
        self.receipts = ['IronStick', 'IronGeer', 'CopperCable', 'LabPocket1Part1', 'Chip']

        self.iron = 0
        self.copper = 0
        self.geer = 0
        self.stick = 0
        self.cable = 0
        self.max_iron = 0
        self.max_copper = 0
        self.max_geer = 0
        self.max_stick = 0
        self.max_cable = 0

        self.can_pull_cable = True
        self.can_delete_cable = False

        self.can_pull_geer_or_stick = True
        self.can_delete_geer_or_stick = False

        self.entry_iron = False
        self.entry_copper = False
        self.entry_geer = False
        self.entry_stick = False
        self.entry_cable = False

    def update(self):
        self.tech_work()
        if not self.can_work():
            return
        super().update()
        if self.receipt == 'IronStick':
            self.update_IronStick()
        elif self.receipt == 'IronGeer':
            self.update_IronGeer()
        elif self.receipt == 'CopperCable':
            self.update_CopperCable()
        elif self.receipt == 'LabPocket1Part1':
            self.update_LabPocket1Part1()
        elif self.receipt == 'Chip':
            self.update_Chip()

    def tech_work(self):
        self.get_item()
        self.set_max_receipt()
        self.delete_trash()
        self.can_entry()
        if self.receipt == 'Chip':
            self.can_pull_cable = False
            self.can_delete_cable = True
        else:
            self.can_pull_cable = True
            self.can_delete_cable = False

        if self.receipt == 'LabPocket1Part1':
            self.can_pull_geer_or_stick = False
            self.can_delete_geer_or_stick = True
        else:
            self.can_pull_geer_or_stick = True
            self.can_delete_geer_or_stick = False

    def get_item(self):
        self.find_item()
        if self.item is None:
            return
        elif isinstance(self.item, IronPlate):
            self.iron += 1
        elif isinstance(self.item, CopperPlate):
            self.copper += 1
        elif isinstance(self.item, IronStick) and self.can_delete_geer_or_stick:
            self.stick += 1
        elif isinstance(self.item, IronGeer) and self.can_delete_geer_or_stick:
            self.geer += 1
        elif isinstance(self.item, CopperCable) and self.can_delete_cable:
            self.cable += 1
        else:
            return
        self.item.kill()
        self.item = None

    def update_IronStick(self):
        self.iron -= 1
        IronStick(self.game, self.rect.x // 40, self.rect.y // 40)
        IronStick(self.game, self.rect.x // 40, self.rect.y // 40)

    def can_work_IronStick(self):
        if self.iron < 1:
            return False
        return True

    def can_entry(self):
        if self.iron >= self.max_iron:
            self.entry_iron = False
        else:
            self.entry_iron = True

        if self.copper >= self.max_copper:
            self.entry_copper = False
        else:
            self.entry_copper = True

        if self.geer >= self.max_geer:
            self.entry_geer = False
        else:
            self.entry_geer = True

        if self.stick >= self.max_stick:
            self.entry_stick = False
        else:
            self.entry_stick = True

        if self.cable >= self.max_cable:
            self.entry_cable = False
        else:
            self.entry_cable = True

    def update_IronGeer(self):
        self.iron -= 2
        IronGeer(self.game, self.rect.x // 40, self.rect.y // 40)

    def can_work_IronGeer(self):
        if self.iron < 2:
            return False
        return True

    def update_CopperCable(self):
        self.copper -= 1
        CopperCable(self.game, self.rect.x // 40, self.rect.y // 40)
        CopperCable(self.game, self.rect.x // 40, self.rect.y // 40)
        CopperCable(self.game, self.rect.x // 40, self.rect.y // 40)

    def can_work_CopperCable(self):
        if self.copper < 1:
            return False
        return True

    def update_LabPocket1Part1(self):
        self.geer -= 2
        self.stick -= 4
        LabPocket1Part1(self.game, self.rect.x // 40, self.rect.y // 40)

    def update_Chip(self):
        self.iron -= 1
        self.cable -= 2
        Chip(self.game, self.rect.x // 40, self.rect.y // 40)

    def can_work_LabPocket1Part1(self):
        if self.geer < 2:
            return False
        if self.stick < 4:
            return False
        return True

    def can_work_Chip(self):
        if self.iron < 1:
            return False
        if self.cable < 2:
            return False
        return True

    def set_max(self, iron=0, copper=0, stick=0, geer=0, cable=0):
        self.max_iron = iron
        self.max_copper = copper
        self.max_geer = geer
        self.max_stick = stick
        self.max_cable = cable

    def set_max_receipt(self):
        if self.receipt == 'IronStick':
            self.set_max(1)
        elif self.receipt == 'IronGeer':
            self.set_max(2)
        elif self.receipt == 'CopperCable':
            self.set_max(0, 1)
        elif self.receipt == 'LabPocket1Part1':
            self.set_max(0, 0, 4, 2)
        elif self.receipt == 'Chip':
            self.set_max(1, 0, 0, 0, 2)

    def delete_trash(self):
        while self.iron > self.max_iron:
            self.iron -= 1
        while self.copper > self.max_copper:
            self.copper -= 1
        while self.stick > self.max_stick and self.can_delete_geer_or_stick:
            self.stick -= 1
        while self.geer > self.max_geer and self.can_delete_geer_or_stick:
            self.geer -= 1
        while self.cable > self.max_cable and self.can_delete_cable:
            self.cable -= 1

    def can_work_receipt(self):
        if self.receipt == 'IronStick':
            if not self.can_work_IronStick():
                return False
        elif self.receipt == 'IronGeer':
            if not self.can_work_IronGeer():
                return False
        elif self.receipt == 'CopperCable':
            if not self.can_work_CopperCable():
                return False
        elif self.receipt == 'LabPocket1Part1':
            if not self.can_work_LabPocket1Part1():
                return False
        elif self.receipt == 'Chip':
            if not self.can_work_Chip():
                return False
        return True

    def can_work(self):
        if pygame.time.get_ticks() - self.last < self.time:
            return False
        self.last = pygame.time.get_ticks()
        if self.game.electricity < ELECTRICITY:
            return False
        if not self.can_work_receipt():
            return False
        return True


class Level2AssemblyMachine(AssemblyMachine):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, 'Level2_Assembling_machine', ASSEMBLY_MACHINE_TIME)
        self.receipt = 'SteelFrame'
        self.receipts = ['PowerChip', 'Engine', 'SteelFrame']

        self.steel = 0
        self.chip = 0
        self.frame = 0
        self.lpp = 0
        self.gold = 0
        self.max_steel = 0
        self.max_chip = 0
        self.max_frame = 0
        self.max_lpp = 0
        self.max_gold = 0
        self.entry_steel = False
        self.entry_chip = False
        self.entry_frame = False
        self.entry_lpp = False
        self.entry_gold = False

        self.can_pull_frame = True
        self.can_delete_frame = False

    def tech_work(self):
        self.get_item()
        self.set_max_receipt()
        self.delete_trash()
        self.can_entry()
        if self.receipt == 'SteelFrame':
            self.can_pull_frame = True
            self.can_delete_frame = False
        else:
            self.can_pull_frame = False
            self.can_delete_frame = True

    def get_item(self):
        self.find_item()
        if self.item is None:
            return
        elif isinstance(self.item, Steel):
            self.steel += 1
        elif isinstance(self.item, Chip):
            self.chip += 1
        elif isinstance(self.item, SteelFrame) and self.can_delete_frame:
            self.frame += 1
        elif isinstance(self.item, LabPocket1Part1):
            self.lpp += 1
        elif isinstance(self.item, ItemGold):
            self.gold += 1
        else:
            return
        self.item.kill()
        self.item = None

    def can_entry(self):
        if self.steel >= self.max_steel:
            self.entry_steel = False
        else:
            self.entry_steel = True

        if self.chip >= self.max_chip:
            self.entry_chip = False
        else:
            self.entry_chip = True

        if self.frame >= self.max_frame:
            self.entry_frame = False
        else:
            self.entry_frame = True

        if self.lpp >= self.max_lpp:
            self.entry_lpp = False
        else:
            self.entry_lpp = True

        if self.gold >= self.max_gold:
            self.entry_gold = False
        else:
            self.entry_gold = True

    def set_max(self, steel=0, chip=0, frame=0, lpp=0, gold=0):
        self.max_steel = steel
        self.max_chip = chip
        self.max_frame = frame
        self.max_lpp = lpp
        self.max_gold = gold

    def set_max_receipt(self):
        if self.receipt == 'SteelFrame':
            self.set_max(3)
        elif self.receipt == 'Engine':
            self.set_max(0, 0, 1, 1)
        elif self.receipt == 'PowerChip':
            self.set_max(0, 2, 0, 0, 3)

    def delete_trash(self):
        while self.steel > self.max_steel:
            self.steel -= 1
        while self.chip > self.max_chip:
            self.chip -= 1
        while self.frame > self.max_frame and self.can_delete_frame:
            self.frame -= 1
        while self.lpp > self.max_lpp:
            self.lpp -= 1
        while self.gold > self.max_gold:
            self.gold -= 1

    def update(self):
        self.tech_work()
        if not self.can_work():
            return
        super().update()
        if self.receipt == 'SteelFrame':
            self.create_SteelFrame()
        elif self.receipt == 'PowerChip':
            self.create_PowerChip()
        elif self.receipt == 'Engine':
            self.create_Engine()

    def create_SteelFrame(self):
        self.steel -= 3
        SteelFrame(self.game, self.rect.x // 40, self.rect.y // 40)

    def create_PowerChip(self):
        self.chip -= 2
        self.gold -= 3
        PowerChip(self.game, self.rect.x // 40, self.rect.y // 40)
        PowerChip(self.game, self.rect.x // 40, self.rect.y // 40)

    def create_Engine(self):
        self.frame -= 1
        self.lpp -= 1
        Engine(self.game, self.rect.x // 40, self.rect.y // 40)

    def can_work_SteelFrame(self):
        if self.steel < 3:
            return False
        return True

    def can_work_PowerChip(self):
        if self.chip < 2:
            return False
        if self.gold < 3:
            return False
        return True

    def can_work_Engine(self):
        if self.steel < 1:
            return False
        if self.lpp < 1:
            return False
        return True

    def can_work_receipt(self):
        if self.receipt == 'SteelFrame':
            if not self.can_work_SteelFrame():
                return False
        elif self.receipt == 'PowerChip':
            if not self.can_work_PowerChip():
                return False
        elif self.receipt == 'Engine':
            if not self.can_work_Engine():
                return False
        return True

    def can_work(self):
        if pygame.time.get_ticks() - self.last < self.time:
            return False
        self.last = pygame.time.get_ticks()
        if self.game.electricity < ELECTRICITY:
            return False
        if not self.can_work_receipt():
            return False
        return True


class LabAssemblyMachine(AssemblyMachine):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, 'Lab_Assembling_machine', ASSEMBLY_MACHINE_TIME)

        self.lp1p1 = 0
        self.lp1p2 = 0
        self.lp2p1 = 0
        self.lp2p2 = 0
        self.max_lp1p1 = 0
        self.max_lp1p2 = 0
        self.max_lp2p1 = 0
        self.max_lp2p2 = 0
        self.entry_lp1p1 = 0
        self.entry_lp1p2 = 0
        self.entry_lp2p1 = 0
        self.entry_lp2p2 = 0

        self.receipt = 'LabPacket1'
        self.receipts = ['LabPacket1', 'LabPacket2']

    def update(self):
        self.tech_work()
        if not self.can_work():
            return
        super().update()
        if self.receipt == 'LabPacket1':
            self.update_LabPacket1()
        elif self.receipt == 'labPacket2':
            self.update_LabPacket2()

    def tech_work(self):
        self.get_item()
        self.set_max_receipt()
        self.delete_trash()
        self.can_entry()

    def get_item(self):
        self.find_item()
        if self.item is None:
            return
        elif isinstance(self.item, Chip):
            self.lp1p2 += 1
        elif isinstance(self.item, LabPocket1Part1):
            self.lp1p1 += 1
        elif isinstance(self.item, Engine):
            self.lp2p1 += 1
        elif isinstance(self.item, PowerChip):
            self.lp2p2 += 1
        else:
            return
        self.item.kill()
        self.item = None

    def can_entry(self):
        if self.lp1p1 >= self.max_lp1p1:
            self.entry_lp1p1 = False
        else:
            self.entry_lp1p1 = True

        if self.lp1p2 >= self.max_lp1p2:
            self.entry_lp1p2 = False
        else:
            self.entry_lp1p2 = True

        if self.lp2p1 >= self.max_lp2p1:
            self.entry_lp2p1 = False
        else:
            self.entry_lp2p1 = True

        if self.lp2p2 >= self.max_lp2p2:
            self.entry_lp2p2 = False
        else:
            self.entry_lp2p2 = True

    def delete_trash(self):
        while self.lp1p1 > self.max_lp1p1:
            self.lp1p1 -= 1
        while self.lp1p1 > self.max_lp1p1:
            self.lp1p1 -= 1
        while self.lp2p1 > self.max_lp2p1:
            self.lp2p1 -= 1
        while self.lp2p2 > self.max_lp2p2:
            self.lp2p2 -= 1

    def set_max(self, lp1p1=0, lp1p2=0, lp2p1=0, lp2p2=0):
        self.max_lp1p1 = lp1p1
        self.max_lp1p2 = lp1p2
        self.max_lp2p1 = lp2p1
        self.max_lp2p2 = lp2p2

    def set_max_receipt(self):
        if self.receipt == 'LabPacket1':
            self.set_max(1, 1)
        elif self.receipt == 'LabPacket2':
            self.set_max(0, 0, 1, 1)

    def can_work(self):
        if pygame.time.get_ticks() - self.last < self.time:
            return False
        self.last = pygame.time.get_ticks()
        if self.game.electricity < ELECTRICITY:
            return False
        if not self.can_work_receipt():
            return False
        return True

    def can_work_receipt(self):
        if self.receipt == 'LabPacket1':
            if not self.can_work_LabPacket1():
                return False
        elif self.receipt == 'LabPacket2':
            if not self.can_work_LabPacket2():
                return False
        return True

    def can_work_LabPacket1(self):
        if self.lp1p1 < 1:
            return False
        if self.lp1p2 < 1:
            return False
        return True

    def can_work_LabPacket2(self):
        if self.lp2p1 < 1:
            return False
        if self.lp2p2 < 1:
            return False
        return True

    def update_LabPacket1(self):
        self.lp1p1 -= 1
        self.lp1p2 -= 1
        LabPacket1(self.game, self.rect.x // 40, self.rect.y // 40)

    def update_LabPacket2(self):
        self.lp2p1 -= 1
        self.lp2p2 -= 1
        LabPacket2(self.game, self.rect.x // 40, self.rect.y // 40)


class Furnaсe(BuildObject):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, None, 'Furnace', FURNACE_TIME)

    def update(self):
        if not self.can_work():
            return
        super().update()
        self.melt()

    def melt(self):
        if isinstance(self.item, ItemIronOre):
            self.item.kill()
            IronPlate(self.game, self.rect.x / 40, self.rect.y / 40)
            self.item = None
        elif isinstance(self.item, ItemCopperOre):
            self.item.kill()
            CopperPlate(self.game, self.rect.x / 40, self.rect.y / 40)
            self.item = None

    def can_work(self):
        if pygame.time.get_ticks() - self.last < self.time:
            return False
        self.last = pygame.time.get_ticks()
        self.find_item()
        if self.item is None:
            return False
        if self.game.electricity < ELECTRICITY:
            return False
        return True


class SolarPanel(BuildObject):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, None, 'Солнечная панель', SOLAR_PANEL_TIME)
        self.game.electricity -= 50

    def update(self):
        if not self.can_work():
            return
        super().update()
        self.game.electricity += 100

    def can_work(self):
        if pygame.time.get_ticks() - self.last < self.time:
            return False
        self.last = pygame.time.get_ticks()
        return True


class Chest(BuildObject):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, None, 'Chest', 0)
        self.storage = []


class Foundry(BuildObject):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, None, 'Литейная', FOUNDRY_TIME)

        self.iron = 0
        self.coal = 0

        self.iron_entry_allowed = True
        self.coal_entry_allowed = True

    def update(self):
        self.trash()
        if not self.can_work():
            return
        super().update()
        self.alloy()

    def trash(self):
        if self.iron >= 1 and self.coal >= 1:
            self.entry_allowed = False
        else:
            self.entry_allowed = True
        if self.iron >= 1:
            self.iron_entry_allowed = False
        else:
            self.iron_entry_allowed = True
        if self.coal >= 1:
            self.coal_entry_allowed = False
        else:
            self.coal_entry_allowed = True

    def can_work(self):
        self.get_item()
        if pygame.time.get_ticks() - self.last < self.time:
            return False
        self.last = pygame.time.get_ticks()
        if self.iron < 1 or self.coal < 1:
            return False
        if self.game.electricity < ELECTRICITY:
            return False
        return True

    def get_item(self):
        self.find_item()
        if self.item is None:
            return
        elif isinstance(self.item, IronPlate):
            self.iron += 1
            self.item.kill()
        elif isinstance(self.item, ItemCoal):
            self.coal += 1
            self.item.kill()
        elif not isinstance(self.item, Steel):
            self.item.kill()
        self.item = None

    def alloy(self):
        self.iron -= 1
        self.coal -= 1
        Steel(self.game, self.rect.x // 40, self.rect.y // 40)

    def prekill(self):
        for i in range(self.iron):
            IronPlate(self.game, self.rect.x // 40, self.rect.y // 40)
        for i in range(self.coal):
            ItemCoal(self.game, self.rect.x // 40, self.rect.y // 40)


class TrashBox(BuildObject):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, None, 'Мусорка', 0)

    def update(self):
        if not self.can_work():
            return
        super().update()
        self.trash()

    def trash(self):
        self.item.kill()
        self.item = None

    def can_work(self):
        if pygame.time.get_ticks() - self.last < self.time:
            return False
        self.find_item()
        if self.item is None:
            return
        self.last = pygame.time.get_ticks()
        if self.game.electricity < ELECTRICITY:
            return False
        return True


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = 5
        self.groups = self.game.all, self.game.player
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = self.height = SIDE
        self.image = pygame.Surface([SIDE, SIDE])

        image_to_load = pygame.image.load('img/Игрок.png')
        self.image = pygame.Surface([self.width, self.height])
        self.image.set_colorkey(BLACK)
        self.image.blit(image_to_load, (0, 0))

        self.rect = self.image.get_rect()
        self.rect.center = (WIN_WIDTH // 2 + 20, WIN_HEIGHT // 2 + 20)
        self.last = 0

    def update(self):
        if self.game.gamemode == 'creative':
            self.image.fill('black')
        elif self.game.gamemode == 'survive':
            image_to_load = pygame.image.load('img/Игрок.png')
            self.image.blit(image_to_load, (0, 0))
        keys = pygame.key.get_pressed()
        if pygame.time.get_ticks() - self.last >= 75:
            self.last = pygame.time.get_ticks()
            for sprite in self.game.dynamic:
                if keys[pygame.K_d]:
                    sprite.rect.x -= PLAYER_SPEED

                if keys[pygame.K_a]:
                    sprite.rect.x += PLAYER_SPEED

                if keys[pygame.K_w]:
                    sprite.rect.y += PLAYER_SPEED

                if keys[pygame.K_s]:
                    sprite.rect.y -= PLAYER_SPEED


class Button(pygame.sprite.Sprite):
    def __init__(self, game, x, y, event):
        self.game = game
        self._layer = 4
        self.groups = self.game.all
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([192, 96])
        self.image.set_colorkey(BLACK)
        self.image.fill((255, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.event = event

    def update(self):
        hits = pygame.sprite.spritecollide(self, self.game.mouse, False)
        if hits:
            if self.game.click:
                self.event()


class Mouse(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = 6
        self.groups = self.game.all, self.game.mouse
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = self.height = 8
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        if self.game.right_click:
            self.build()
        if self.game.left_click:
            self.kill_object()
            if self.game.mod_item_kill:
                self.kill_item()

    def build(self):
        if self.game.build_object == Foundry and not self.game.can_use_foundry:
            return
        object = self.game.build_object(self.game, self.rect.x // 40, self.rect.y // 40, self.game.facing)
        pygame.sprite.spritecollide(object, self.game.builds, True)
        object = self.game.build_object(self.game, self.rect.x // 40, self.rect.y // 40, self.game.facing)

    def kill_object(self):
        for object in self.game.builds:
            if object.rect.x // 40 == self.rect.x // 40 and object.rect.y // 40 == self.rect.y // 40:
                object.prekill()
                object.tech_item.kill()
                object.kill()

    def kill_item(self):
        for item in self.game.items:
            if item.rect.x // 40 == self.rect.x // 40 and item.rect.y // 40 == self.rect.y // 40:
                item.kill()


class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = 1
        self.groups = self.game.all
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([1024, 1024])
        self.image.blit(pygame.image.load("img/Гига_Земля.png"), (0, 0))
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = x * 1024
        self.rect.y = y * 1024


class Ore(pygame.sprite.Sprite):
    def __init__(self, game, x, y, image):
        self.game = game
        self._layer = 2
        self.groups = self.game.all, self.game.dynamic, self.game.ores
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([40, 40])
        self.image.blit(pygame.image.load(f"img/{image}.png"), (0, 0))
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = x * 40
        self.rect.y = y * 40


class IronOre(Ore):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Железная руда')


class CopperOre(Ore):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Медная руда')


class Coal(Ore):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Уголь')


class Gold(Ore):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Золото')


class Item(pygame.sprite.Sprite):
    def __init__(self, game, x, y, image, exp, layer=4):
        self.game = game
        self._layer = layer
        self.groups = self.game.all, self.game.dynamic, self.game.items
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([24, 24])
        self.image.blit(pygame.image.load(f"img/{image}.xcf"), (0, 0))
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = x * 40 + 8
        self.rect.y = y * 40 + 8

        self.object = None
        self.last = 0
        self.exp = exp

    def update(self):
        self.find_object()

    def find_object(self):
        try:
            object = pygame.sprite.spritecollide(self, self.game.builds, False)[0]
        except:
            object = None
        self.object = object

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y
        self.last = pygame.time.get_ticks()


class ItemIronOre(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Предмет железная руда', 0)


class ItemCopperOre(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Предмет медная руда', 0)


class IronStick(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Железный прут', 0)


class IronPlate(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Железная пластина', 0)


class TechItem(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Технический предмет', 0, 0)


class CopperPlate(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Медная пластина', 0)


class IronGeer(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Железная шестерня', 0)


class ItemCoal(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Предмет уголь', 0)


class Steel(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Сталь', 0)


class CopperCable(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Медный кабель', 0)


class LabPocket1Part1(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'LabPacket1Part1', 0)


class Chip(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Микросхема', 0)


class LabPacket1(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'LabPacket1', 1)


class LabPacket2(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'LabPacket2', 10)


class SteelFrame(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Стальной каркас', 0)


class Engine(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Двигатель', 0)


class PowerChip(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Мощная электросхема', 0)


class ItemGold(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Предмет золото', 0)


class Game_Over_Screen(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = 2
        self.groups = self.game.all
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([WIN_WIDTH, WIN_HEIGHT])
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)

        font = pygame.font.Font(None, 50)
        try:
            if self.game.exp < 100:
                text = font.render("Ваш невероятный счёт: " + str(self.game.exp), True, (100, 255, 100))
            else:
                text = font.render("Ваш очень маленький счёт: " + str(self.game.exp), True, (100, 255, 100))
        except:
            text = font.render("Ваш счёт: Неизвестно", True, (100, 255, 100))
        text_x = WIN_WIDTH // 2 - text.get_width() // 2
        text_y = WIN_HEIGHT // 2 - text.get_height() // 2
        text_w = text.get_width()
        text_h = text.get_height()
        self.image.blit(text, (text_x, text_y))

        self.time = pygame.time.get_ticks() + 3000

        sqlite_connection = sqlite3.connect('db.db')
        cursor = sqlite_connection.cursor()

        sqlite_insert_query = """INSERT INTO Score
                              (score)
                              VALUES
                              (""" + str(self.game.exp) + """);"""

        count = cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        cursor.close()

    def update(self):
        if pygame.time.get_ticks() >= self.time:
            self.game.runnig = False
