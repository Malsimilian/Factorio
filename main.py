import pygame


class Object:
    def __init__(self, image):
        self.image = pygame.image.load(image).convert_alpha()


class Player(Object):
    def __init__(self):
        super().__init__('Безымянный.png')



if __name__ == '__main__':
    pygame.init()
    size = width, height = 1000, 1000
    screen = pygame.display.set_mode(size)

    screen.fill('black')
    running = True
    speed = side = 40
    FPS = 30
    player = Player()
    clock = pygame.time.Clock()
    rect = pygame.Rect(0, 0, side, side)
    screen.blit(player.image, rect)
    moving = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    rect.center = (rect.center[0] - speed, rect.center[1])
                if event.key == pygame.K_RIGHT:
                    rect.center = (rect.center[0] + speed, rect.center[1])
                if event.key == pygame.K_UP:
                    rect.center = (rect.center[0], rect.center[1] - speed)
                if event.key == pygame.K_DOWN:
                    rect.center = (rect.center[0], rect.center[1] + speed)

        screen.fill('black')
        screen.blit(player.image, rect)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()