import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = 4
        self.groups = self.game.all
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([10, 10])
        self.image.fill((255, 0, 0))

        """
        image_to_load = pg.image.load('img/Размытыш 2.0.jpg')
        self.image = pg.Surface([self.width, self.hieght])
        self.image.set_colorkey(BLACK)
        self.image.blit(image_to_load, (0, 0))
        """

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.rect.x += 10
