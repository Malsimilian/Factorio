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
        text1 = f1.render('Текущий обЪект ' + str(self.game.info_build_object), True,
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
    def __init__(self, game, x, y, facing, name):
        self.game = game
        self._layer = 2
        self.groups = self.game.all, self.game.dynamic, self.game.storage, self.game.builds

        super().__init__(self.groups)

        self.image = pygame.Surface([SIDE, SIDE])
        if facing is not None:
            self.image.blit(pygame.image.load(f"img/{name}_{facing}.png"), (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = x * SIDE
        self.rect.y = y * SIDE

        self.name = name

        self.last = 0
        self.facing = facing

    def __str__(self):
        return self.name


class Mine(BuildObject):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, facing, 'Бур')
        self.remove(self.game.storage)

    def update(self):
        hits = pygame.sprite.spritecollide(self, self.game.ores, False)
        if hits:
            self.get_ore()

    def get_ore(self):
        if pygame.time.get_ticks() - self.last >= 4000:
            self.last = pygame.time.get_ticks()
            if self.facing == "вправо":
                for sprite in self.game.storage:
                    if sprite.rect.x == self.rect.x + SIDE and sprite.rect.y == self.rect.y:
                        self.sprite = sprite
                        if not sprite.next_storage:
                            if not sprite.storage:
                                sprite.next_storage = 1
                        break
            if self.facing == "влево":
                for sprite in self.game.storage:
                    if sprite.rect.x == self.rect.x - SIDE and sprite.rect.y == self.rect.y:
                        self.sprite = sprite
                        if not sprite.next_storage:
                            if not sprite.storage:
                                sprite.next_storage = 1
                        break
            if self.facing == "вниз":
                for sprite in self.game.storage:
                    if sprite.rect.x == self.rect.x and sprite.rect.y == self.rect.y + SIDE:
                        self.sprite = sprite
                        if not sprite.next_storage:
                            if not sprite.storage:
                                sprite.next_storage = 1
                        break
            if self.facing == "вверх":
                for sprite in self.game.storage:
                    if sprite.rect.x == self.rect.x + SIDE and sprite.rect.y == self.rect.y - SIDE:
                        self.sprite = sprite
                        if not sprite.next_storage:
                            if not sprite.storage:
                                sprite.next_storage = 1
                        break


class Conveyor(BuildObject):
    def __init__(self, game, x, y, facing, st=None):
        super().__init__(game, x, y, facing, 'Конвейер')

        self.next_storage = None
        self.peredacha = False
        self.storage = st
        self.item = None

    # def update(self):
    #     if pygame.time.get_ticks() - self.last >= 1000:
    #         self.last = pygame.time.get_ticks()
    #         self.peredacha = False
    #         self.sprite = None
    #         if self.storage != None:
    #             if self.facing == "вверх":
    #                 for sprite in self.game.storage:
    #                     if sprite.rect.x == self.rect.x and sprite.rect.y == self.rect.y - SIDE:
    #                         self.sprite = sprite
    #                         if not sprite.next_storage:
    #                             if not sprite.storage:
    #                                 sprite.next_storage = self.storage
    #                                 self.peredacha = True
    #                         break
    #
    #             if self.facing == "вниз":
    #                 for sprite in self.game.storage:
    #                     if sprite.rect.x == self.rect.x and sprite.rect.y == self.rect.y + SIDE:
    #                         self.sprite = sprite
    #                         if not sprite.next_storage:
    #                             if not sprite.storage:
    #                                 sprite.next_storage = self.storage
    #                                 self.peredacha = True
    #                         break
    #
    #             if self.facing == "вправо":
    #                 for sprite in self.game.storage:
    #                     if sprite.rect.x == self.rect.x + SIDE and sprite.rect.y == self.rect.y:
    #                         self.sprite = sprite
    #                         if not sprite.next_storage:
    #                             if not sprite.storage:
    #                                 sprite.next_storage = self.storage
    #                                 self.peredacha = True
    #                         break
    #
    #             if self.facing == "влево":
    #                 for sprite in self.game.storage:
    #                     if sprite.rect.x == self.rect.x - SIDE and sprite.rect.y == self.rect.y:
    #                         self.sprite = sprite
    #                         if not sprite.next_storage:
    #                             if not sprite.storage:
    #                                 sprite.next_storage = self.storage
    #                                 self.peredacha = True
    #                         break
    #
    # def next(self):
    #     try:
    #         if self.sprite.peredacha:
    #             self.sprite.next_storage = self.storage
    #             self.peredacha = True
    #     except AttributeError:
    #         pass
    #     if not self.storage:
    #         self.storage = self.next_storage
    #         self.next_storage = None
    #
    #     elif self.peredacha:
    #         self.storage = self.next_storage
    #         self.next_storage = None
    #         self.peredacha = False
    #
    #     if self.facing == "вправо":
    #         if self.storage:
    #             self.image.blit(pygame.image.load("img/Конвейер_вправо_зап.png"), (0, 0))
    #         else:
    #             self.image.blit(pygame.image.load("img/Конвейер_вправо.png"), (0, 0))
    #
    #     elif self.facing == "влево":
    #         if self.storage:
    #             self.image.blit(pygame.image.load("img/Конвейер_влево_зап.png"), (0, 0))
    #         else:
    #             self.image.blit(pygame.image.load("img/Конвейер_влево.png"), (0, 0))
    #
    #     elif self.facing == "вверх":
    #         if self.storage:
    #             self.image.blit(pygame.image.load("img/Конвейер_вверх_зап.png"), (0, 0))
    #         else:
    #             self.image.blit(pygame.image.load("img/Конвейер_вверх.png"), (0, 0))
    #
    #     elif self.facing == "вниз":
    #         if self.storage:
    #             self.image.blit(pygame.image.load("img/Конвейер_вниз_зап.png"), (0, 0))
    #         else:
    #             self.image.blit(pygame.image.load("img/Конвейер_вниз.png"), (0, 0))

    def update(self):
        self.find_item()
        self.move_item()

    def find_item(self):
        for item in self.game.items:
            if item.object == self:
                self.item = item

    def move_item(self):
        if self.item is None:
            return
        if pygame.time.get_ticks() - self.item.last < 100:
            return
        if self.facing == 'вправо':
            self.item.move(SIDE, 0)
        elif self.facing == 'влево':
            self.item.move(-SIDE, 0)
        elif self.facing == 'вниз':
            self.item.move(0, SIDE)
        elif self.facing == 'вверх':
            self.item.move(0, -SIDE)
        self.item = None

class Lab(BuildObject):
    def __init__(self, game, x, y, facing):
        super().__init__(game, x, y, None, 'Лаборотория')

        self.image.fill('blue')

        self.storage = 0
        self.next_storage = None

    def update(self):
        if self.storage:
            self.image.fill('green')
        else:
            self.image.fill('blue')
        if pygame.time.get_ticks() - self.last >= 4000:
            self.last = pygame.time.get_ticks()
            if self.storage:
                self.storage -= 1
                self.game.exp += 1

    def next(self):
        if not self.storage:
            self.storage = self.next_storage
            self.next_storage = None

    def __str__(self):
        return 'Lab'


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = 4
        self.groups = self.game.all
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = self.height = SIDE
        self.image = pygame.Surface([SIDE, SIDE])

        image_to_load = pygame.image.load('img/Безымянный.png')
        self.image = pygame.Surface([self.width, self.height])
        self.image.set_colorkey(BLACK)
        self.image.blit(image_to_load, (0, 0))

        self.rect = self.image.get_rect()
        self.rect.center = (WIN_WIDTH // 2, WIN_HEIGHT // 2)
        #  * random.randint(-5, +5)  * random.randint(-5, +5)
        self.last = 0

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
        self._layer = 4
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

    def build(self):
        object = self.game.build_object(self.game, self.rect.x // 40, self.rect.y // 40, self.game.facing)
        pygame.sprite.spritecollide(object, self.game.builds, True)
        object = self.game.build_object(self.game, self.rect.x // 40, self.rect.y // 40, self.game.facing)

    def kill_object(self):
        for object in self.game.builds:
            if object.rect.x // 40 == self.rect.x // 40 and object.rect.y // 40 == self.rect.y // 40:
                object.kill()


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
    def __init__(self, game, x, y):
        self.game = game
        self._layer = 2
        self.groups = self.game.all, self.game.dynamic, self.game.ores
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([40, 40])
        self.image.blit(pygame.image.load("img/Руда_1.png"), (0, 0))
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = x * 40
        self.rect.y = y * 40


class Item(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = 4
        self.groups = self.game.all, self.game.dynamic, self.game.items
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([24, 24])
        self.image.fill((50, 50, 50))

        self.rect = self.image.get_rect()
        self.rect.x = x * 40 + 8
        self.rect.y = y * 40 + 8

        self.type = 0
        self.object = None
        self.last = 0

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
