import pygame


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, filename):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert_alpha()
        self.rect = self.image.get_rect(center=(x, 0))


if __name__ == '__main__':
    pygame.init()
    size = width, height = 40, 40
    screen = pygame.display.set_mode(size)

    screen.fill('black')
    running = True
    speed = 600
    FPS = 90
    clock = pygame.time.Clock()
    b1 = Ball(width // 2, 'Без названия.jfif')

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        screen.fill('black')
        screen.blit(b1.image, b1.rect)
        pygame.display.update()

        clock.tick(FPS)

        if b1.rect.y < height:
            b1.rect.y += speed / FPS
        else:
            b1.rect.y = 0
    pygame.quit()