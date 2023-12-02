import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = 4
        self.groups = self.game.all
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([10, 10])
        self.image.fill((255, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        pass
