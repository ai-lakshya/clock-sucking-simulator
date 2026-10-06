import pygame

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1280, 720), pygame.SCALED | pygame.RESIZABLE)
    clock = pygame.time.Clock()
    pos = pygame.Vector2(640, 360)
    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(keys[pygame.K_d] - keys[pygame.K_a], keys[pygame.K_s] - keys[pygame.K_w])
        if move.length_squared() > 0:
            pos += move.normalize() * 300 * dt
        screen.fill((20, 20, 28))
        pygame.draw.circle(screen, (230, 90, 80), pos, 16)
        pygame.display.flip()
    pygame.quit()