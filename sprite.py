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

    def update(self):
        keys = pygame.key.get_pressed()
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


class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = 1
        self.groups = self.game.all, self.game.dynamic
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = self.height = 96
        self.image = pygame.Surface([SIDE, SIDE])
        self.image.fill(GREEN)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Item(pygame.sprite.Sprite):
    def __init__(self, game, x, y, type):
        self.game = game
        self._layer = 1
        self.groups = self.game.all, self.game.dynamic
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([24, 24])
        self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.x = x * 24
        self.rect.y = y * 24

        self.type = type


class Mine(pygame.sprite.Sprite):
    def __init__(self, game, x, y, type):
        self.game = game
        self._layer = 1
        self.groups = self.game.all, self.game.dynamic
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([SIDE, SIDE])
        self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.x = x * SIDE
        self.rect.y = y * SIDE

        self.type = type
        self.last = 0  # последнее время get_ore в мл сек

    def update(self):
        self.get_ore()

    def get_ore(self):
        if pygame.time.get_ticks() - self.last >= 2000:
            print(self.type)
            self.last = pygame.time.get_ticks()


class Conveyor(pygame.sprite.Sprite):
    def __init__(self, game, x, y, facing, st=[None, None, None, None]):
        self.game = game
        self._layer = 1
        self.groups = self.game.all, self.game.dynamic, self.game.storage
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.facing = facing

        self.image = pygame.Surface([SIDE, SIDE])
        self.image.blit(pygame.image.load("img/Конвейер_" + self.facing +".png"), (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = x * SIDE
        self.rect.y = y * SIDE

        self.next_storage =self.storage = st  # хранилище в данный момент
        # [None, None, None, None]  # хранилище в следующий момент (костыль для правильной работы спрайта)
        self.last = 0

    def update(self):
        if pygame.time.get_ticks() - self.last >= 1000:
            self.last = pygame.time.get_ticks()
            if self.storage != [None, None, None, None]:
                for sprite in self.game.storage:
                    if self.facing == "вправо":
                        if sprite.rect.x == self.rect.x + SIDE and sprite.rect.y == self.rect.y:
                            if sprite.storage == [None, None, None, None]:
                                sprite.next_storage = self.storage
                                self.storage = self.next_storage = [None, None, None, None]
                            else:
                                items_sprite = 0
                                for item in sprite.storage:
                                    if item:
                                        items_sprite += 1

                                items_self = 0
                                for item in self.storage:
                                    if item:
                                        items_self += 1

                                if items_self + items_sprite == 4:
                                    sprite.next_storage = [1, 1, 1, 1]
                                    self.storage = self.next_storage = [None, None, None, None]

                                elif items_self + items_sprite < 4:
                                    for el in range(items_self + items_sprite):
                                        sprite.next_storage[el] = 1
                                    self.storage = self.next_storage = [None, None, None, None]

                                elif items_self + items_sprite == 8:
                                    pass

                                else:
                                    sprite.next_storage = [1, 1, 1, 1]
                                    self.next_storage = self.storage = [None, None, None, None]
                                    for el in range(items_self + items_sprite - 4):
                                        self.next_storage[el] = 1
                            break

            #print(self.storage)
            self.storage = self.next_storage

            if self.storage[3] != None:
                self.image.blit(pygame.image.load("img/Конвейер_вправо_4.png"), (0, 0))
            elif self.storage[2] != None:
                self.image.blit(pygame.image.load("img/Конвейер_вправо_3.png"), (0, 0))
            elif self.storage[1] != None:
                self.image.blit(pygame.image.load("img/Конвейер_вправо_2.png"), (0, 0))
            elif self.storage[0] != None:
                self.image.blit(pygame.image.load("img/Конвейер_вправо_1.png"), (0, 0))
            else:
                self.image.blit(pygame.image.load("img/Конвейер_вправо.png"), (0, 0))

