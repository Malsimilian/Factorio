import pygame


if __name__ == '__main__':
    pygame.init()
    size = width, height = 300, 300
    screen = pygame.display.set_mode(size)

    screen.fill('black')
    running = True
    rect = pygame.Rect(0, 0, 100, 100)
    pygame.draw.rect(screen, 'green', rect)
    moving = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                if moving:
                    rect.center = (rect.center[0] + event.rel[0], rect.center[1] + event.rel[1])
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect.left <= event.pos[0] <= rect.right and rect.top <= event.pos[1] <= rect.bottom:
                    moving = True
            if event.type == pygame.MOUSEBUTTONUP:
                moving = False
        screen.fill('black')
        pygame.draw.rect(screen, 'green', rect)
        pygame.display.flip()
    pygame.quit()