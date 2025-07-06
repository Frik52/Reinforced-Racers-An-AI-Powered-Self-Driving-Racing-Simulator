import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Self-Driving Car - Elliptical Track")

# Colors
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
GREEN = (40, 120, 40)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# FPS
FPS = 60
clock = pygame.time.Clock()

class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.max_speed = 5
        self.acceleration = 0.1
        self.turn_speed = 4
        self.width = 20
        self.length = 40

        self.image = pygame.Surface((self.width, self.length), pygame.SRCALPHA)
        self.image.fill(RED)

        self.crashed = False

    def update(self, keys):
        if self.crashed:
            self.speed = 0
            return

        if keys[pygame.K_UP]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed / 2)
        else:
            self.speed *= 0.96

        if keys[pygame.K_LEFT]:
            self.angle += self.turn_speed * (self.speed / self.max_speed)
        if keys[pygame.K_RIGHT]:
            self.angle -= self.turn_speed * (self.speed / self.max_speed)

        rad = math.radians(-self.angle)
        dx = self.speed * math.cos(rad)
        dy = self.speed * math.sin(rad)

        self.x += dx
        self.y += dy

    def draw(self, surface):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(rotated_image, new_rect.topleft)

    def check_collision(self, surface):
        try:
            pixel_color = surface.get_at((int(self.x), int(self.y)))[:3]
            if pixel_color != GRAY and pixel_color != WHITE:
                self.crashed = True
              
        except IndexError:
            self.crashed = True  # Off-screen = crash

def draw_track(surface):
    surface.fill(GREEN)

    # Outer and inner track
    outer = pygame.Rect(100, 100, 600, 400)
    inner = pygame.Rect(200, 200, 400, 200)

    pygame.draw.ellipse(surface, GRAY, outer)
    pygame.draw.ellipse(surface, GREEN, inner)

    # Start line
    pygame.draw.line(surface, WHITE, (400, 100), (400, 200), 5)

def main():
    car = Car(400, 140)

    run = True
    while run:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        draw_track(WIN)
        car.check_collision(WIN)
        car.update(keys)
        car.draw(WIN)

        if car.crashed:
            font = pygame.font.SysFont(None, 48)
            text = font.render("Crashed!", True, BLACK)
            WIN.blit(text, (WIDTH // 2 - 80, HEIGHT // 2 - 20))

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
