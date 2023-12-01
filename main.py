import pygame





if __name__ == '__main__':
    pygame.init()
    size = width, height = 1000, 1000
    screen = pygame.display.set_mode(size)

    screen.fill('black')
    running = True
    speed = side = 40
    FPS = 30
    image = pygame.image.load('Безымянный.png').convert_alpha()
    clock = pygame.time.Clock()
    rect = pygame.Rect(0, 0, side, side)
    screen.blit(image, rect)
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
        screen.blit(image, rect)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()