import pygame, random
from config import *


class Interface(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = 3
        self.groups = game.all, game.interface
        super().__init__(self.groups)


class Info(Interface):
    def __init__(self, game):
        super().__init__(game)

        self.image = pygame.Surface([SIDE * 23, SIDE])
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
        text1 = f1.render(self.game.info, True,
                          (0, 0, 0))
        self.image.blit(text1, self.rect)


class Facing(Interface):
    def __init__(self, game):
        super().__init__(game)

        self.image = pygame.Surface([SIDE * 2, SIDE * 2])
        self.image.blit(pygame.image.load("img/Направление_вправо.png"), (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = WIN_WIDTH - 80
        self.rect.y = 0

        self.ind = 0
        self.facings = ["вправо", "вниз", "влево", "вверх"]

        self.last = 500

    def update(self):
        if pygame.time.get_ticks() - self.last >= 200:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.last = pygame.time.get_ticks()
                self.ind += 1
                if self.ind == 4:
                    self.ind = 0

                self.game.facing = self.facings[self.ind]
                self.image.blit(pygame.image.load("img/Направление_" + self.facings[self.ind] + ".png"), (0, 0))


class BuildObject(pygame.sprite.Sprite):
    def __init__(self, game, x, y, facing, name, time):
        self.game = game
        self._layer = 2
        self.groups = self.game.all, self.game.dynamic, self.game.storage, self.game.builds

        super().__init__(self.groups)

        self.image = pygame.Surface([SIDE, SIDE])
        if facing is not None:
            self.image.blit(pygame.image.load(f"img/{name}_{facing}.png"), (0, 0))
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
        # self.move_player()

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
        return True

    # def move_player(self):
    #     for player in self.game.player:
    #         if pygame.time.get_ticks() - player.last2 < 1000:
    #             return
    #         player.last2 = pygame.time.get_ticks()
    #         if not pygame.sprite.spritecollide(self, self.game.player, False):
    #             return
    #         for sprite in self.game.dynamic:
    #             if self.facing == 'вправо':
    #                 sprite.rect.x -= SIDE
    #             elif self.facing == 'влево':
    #                 sprite.rect.x += SIDE
    #             elif self.facing == 'вниз':
    #                 sprite.rect.y -= SIDE
    #             elif self.facing == 'вверх':
    #                 sprite.rect.y += SIDE


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
                if self.facing == 'вправо':
                    previous_item.move(SIDE, 0)
                elif self.facing == 'влево':
                    previous_item.move(-SIDE, 0)
                elif self.facing == 'вниз':
                    previous_item.move(0, SIDE)
                elif self.facing == 'вверх':
                    previous_item.move(0, -SIDE)
        elif isinstance(previous_object, Conveyor):
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
        self.image.blit(pygame.image.load(f"img/Лаборатория.png"), (0, 0))
        self.image.set_colorkey(BLACK)

    def update(self):
        if not self.can_work():
            return
        super().update()
        self.research()

    def research(self):
        if isinstance(self.item, ItemIronOre):
            self.item.kill()
            self.game.exp += 1
            self.item = None
        elif isinstance(self.item, IronPlate):
            self.item.kill()
            self.game.exp += 10
            self.item = None
        elif isinstance(self.item, CopperPlate):
            self.item.kill()
            self.game.exp += 10
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
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, None, 'Assembling_machine', ASSEMBLY_MACHINE_TIME)
        self.image.blit(pygame.image.load(f"img/Assembling_machine.png"), (0, 0))
        self.image.set_colorkey(BLACK)

    def update(self):
        super().update()
        self.find_item()


class Furnaсe(BuildObject):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, None, 'Furnace', FURNACE_TIME)
        self.image.blit(pygame.image.load(f"img/Furnace.png"), (0, 0))
        self.image.set_colorkey(BLACK)

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
        self.image.blit(pygame.image.load(f"img/Солнчная панель.png"), (0, 0))
        self.image.set_colorkey(BLACK)

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
        super().__init__(game, x, y, None, 'Chest')
        self.image.blit(pygame.image.load(f"img/Железный сундук.png"), (0, 0))
        self.image.set_colorkey(BLACK)
        self.storage = []


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = 5
        self.groups = self.game.all, self.game.player
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = self.height = SIDE
        self.image = pygame.Surface([SIDE, SIDE])

        image_to_load = pygame.image.load('img/Безымянный.png')
        self.image = pygame.Surface([self.width, self.height])
        self.image.set_colorkey(BLACK)
        self.image.blit(image_to_load, (0, 0))

        self.rect = self.image.get_rect()
        self.rect.center = (WIN_WIDTH // 2 + 20, WIN_HEIGHT // 2 + 20)
        self.last = 0
        # self.last2 = 0

    def update(self):
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
        image_to_load = pygame.image.load('img/Кнопка играть.png')
        self.image.set_colorkey(BLACK)
        self.image.blit(image_to_load, (0, 0))

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
        object = self.game.build_object(self.game, self.rect.x // 40, self.rect.y // 40, self.game.facing)
        pygame.sprite.spritecollide(object, self.game.builds, True)
        object = self.game.build_object(self.game, self.rect.x // 40, self.rect.y // 40, self.game.facing)

    def kill_object(self):
        for object in self.game.builds:
            if object.rect.x // 40 == self.rect.x // 40 and object.rect.y // 40 == self.rect.y // 40:
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
        self.groups = self.game.all, self.game.dynamic
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
        super().__init__(game, x, y, 'Предмет железная руда', 1)


class ItemCopperOre(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Предмет медная руда', 1)


class IronStick(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Железная Прут', 100)


class IronPlate(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Железная пластина', 10)


class TechItem(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Технический предмет', 0, 0)


class CopperPlate(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Медная пластина', 10)


class IronGeer(Item):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 'Железная шестерня', 400)