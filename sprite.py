import pygame
from config import *

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

        self.last = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if pygame.time.get_ticks() - self.last >= 75:
            self.last = pygame.time.get_ticks()
            if keys[pygame.K_d]:
                for sprite in self.game.dynamic:
                    sprite.rect.x -= PLAYER_SPEED

            if keys[pygame.K_a]:
                for sprite in self.game.dynamic:
                    sprite.rect.x += PLAYER_SPEED

            if keys[pygame.K_w]:
                for sprite in self.game.dynamic:
                    sprite.rect.y += PLAYER_SPEED

            if keys[pygame.K_s]:
                for sprite in self.game.dynamic:
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
        if self.game.click:
            Conveyor(self.game, self.rect.x // 40, self.rect.y // 40, self.game.facing)


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
    def __init__(self, game):
        self.game = game
        self._layer = 1
        self.groups = self.game.all, self.game.dynamic
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([24, 24])
        self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

        self.type = 0


class Mine(pygame.sprite.Sprite):
    def __init__(self, game, x, y, facing):
        self.game = game
        self._layer = 1
        self.groups = self.game.all, self.game.dynamic
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([SIDE, SIDE])
        self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.x = x * SIDE
        self.rect.y = y * SIDE

        self.last = 0  # последнее время get_ore в мл сек
        self.facing = facing

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


class Conveyor(pygame.sprite.Sprite):
    def __init__(self, game, x, y, facing, st=None):
        self.game = game
        self._layer = 2
        self.groups = self.game.all, self.game.dynamic, self.game.storage
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.facing = facing

        self.image = pygame.Surface([SIDE, SIDE])
        self.image.blit(pygame.image.load("img/Конвейер_" + self.facing +".png"), (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = x * SIDE
        self.rect.y = y * SIDE

        self.next_storage = None
        self.peredacha = False
        self.storage = st  # хранилище в данный момент
        self.last = 2000

    def update(self):
        if pygame.time.get_ticks() - self.last >= 1000:
            self.last = pygame.time.get_ticks()
            self.peredacha = False
            self.sprite = None
            if self.storage != None:
                if self.facing == "вверх":
                    for sprite in self.game.storage:
                        if sprite.rect.x == self.rect.x and sprite.rect.y == self.rect.y - SIDE:
                            self.sprite = sprite
                            if not sprite.next_storage:
                                if not sprite.storage:
                                    sprite.next_storage = self.storage
                                    self.peredacha = True
                            break

                if self.facing == "вниз":
                    for sprite in self.game.storage:
                        if sprite.rect.x == self.rect.x and sprite.rect.y == self.rect.y + SIDE:
                            self.sprite = sprite
                            if not sprite.next_storage:
                                if not sprite.storage:
                                    sprite.next_storage = self.storage
                                    self.peredacha = True
                            break

                if self.facing == "вправо":
                    for sprite in self.game.storage:
                        if sprite.rect.x == self.rect.x + SIDE and sprite.rect.y == self.rect.y:
                            self.sprite = sprite
                            if not sprite.next_storage:
                                if not sprite.storage:
                                    sprite.next_storage = self.storage
                                    self.peredacha = True
                            break

                if self.facing == "влево":
                    for sprite in self.game.storage:
                        if sprite.rect.x == self.rect.x - SIDE and sprite.rect.y == self.rect.y:
                            self.sprite = sprite
                            if not sprite.next_storage:
                                if not sprite.storage:
                                    sprite.next_storage = self.storage
                                    self.peredacha = True
                            break

    def next(self):
        try:
            if self.sprite.peredacha:
                self.sprite.next_storage = self.storage
                self.peredacha = True
        except AttributeError:
            pass
        if not self.storage:
            self.storage = self.next_storage
            self.next_storage = None

        elif self.peredacha:
            self.storage = self.next_storage
            self.next_storage = None
            self.peredacha = False

        if self.facing == "вправо":
            if self.storage:
                self.image.blit(pygame.image.load("img/Конвейер_вправо_зап.png"), (0, 0))
            else:
                self.image.blit(pygame.image.load("img/Конвейер_вправо.png"), (0, 0))

        elif self.facing == "влево":
            if self.storage:
                self.image.blit(pygame.image.load("img/Конвейер_влево_зап.png"), (0, 0))
            else:
                self.image.blit(pygame.image.load("img/Конвейер_влево.png"), (0, 0))

        elif self.facing == "вверх":
            if self.storage:
                self.image.blit(pygame.image.load("img/Конвейер_вверх_зап.png"), (0, 0))
            else:
                self.image.blit(pygame.image.load("img/Конвейер_вверх.png"), (0, 0))

        elif self.facing == "вниз":
            if self.storage:
                self.image.blit(pygame.image.load("img/Конвейер_вниз_зап.png"), (0, 0))
            else:
                self.image.blit(pygame.image.load("img/Конвейер_вниз.png"), (0, 0))


class Facing(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = 3
        self.groups = self.game.all
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([SIDE * 2, SIDE * 2])
        self.image.blit(pygame.image.load("img/Направление_вниз.png"), (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = WIN_WIDTH - 80
        self.rect.y = 0

        self.ind = 0
        self.facings = ["вниз", "вправо", "вверх", "влево"]

        self.last = 500

    def update(self):
        if pygame.time.get_ticks() - self.last >= 500:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.last = pygame.time.get_ticks()
                self.ind += 1
                if self.ind == 4:
                    self.ind = 0

                self.game.facing = self.facings[self.ind]
                self.image.blit(pygame.image.load("img/Направление_" + self.facings[self.ind] + ".png"), (0, 0))
