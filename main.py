import pygame


class Object:
    def __init__(self, image):
        self.image = pygame.image.load(image).convert_alpha()


class Player(Object):
    def __init__(self):
        super().__init__('Игрок.png')

class Floor(Object):
    def __init__(self):
        super().__init__('Земля.png')


def draw_floor(screen):
    print(1)
    side = 40
    big_side = int(screen.get_size()[0] / side)
    for i in range(big_side):
        for j in range(big_side):
            rect = pygame.Rect(side * j, side * i, side * j + side, side * i + side)
            screen.blit(Floor().image, rect)


if __name__ == '__main__':
    pygame.init()
    size = width, height = 1000, 1000
    screen = pygame.display.set_mode(size)

    draw_floor(screen)
    running = True
    side = 40
    FPS = 30
    player = Player()
    clock = pygame.time.Clock()
    rect = pygame.Rect(0, 0, side, side)
    screen.blit(player.image, rect)
    moving = False
    need_draw = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                need_draw = True
                if event.key == pygame.K_LEFT:
                    rect.center = (rect.center[0] - side, rect.center[1])
                if event.key == pygame.K_RIGHT:
                    rect.center = (rect.center[0] + side, rect.center[1])
                if event.key == pygame.K_UP:
                    rect.center = (rect.center[0], rect.center[1] - side)
                if event.key == pygame.K_DOWN:
                    rect.center = (rect.center[0], rect.center[1] + side)
        if need_draw:
            need_draw = False
            draw_floor(screen)
            screen.blit(player.image, rect)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()