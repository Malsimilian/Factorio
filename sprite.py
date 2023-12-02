import pygame
from config import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = 4
        self.groups = self.game.all
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = self.height = SIDE
        self.image = pygame.Surface([SIDE, SIDE])
        self.image.fill((255, 0, 0))


        image_to_load = pygame.image.load('img/Человек.png')
        self.image = pygame.Surface([self.width, self.height])
        # self.image.set_colorkey('black')
        self.image.blit(image_to_load, (0, 0))


        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.rect.x += 10
