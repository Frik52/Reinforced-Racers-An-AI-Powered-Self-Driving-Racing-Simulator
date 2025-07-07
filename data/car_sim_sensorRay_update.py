import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Self-Driving Car - Complex Track")

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
        self.init_x = x
        self.init_y = y
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.max_speed = 5
        self.acceleration = 0.1
        self.turn_speed = 4
        self.width = 15
        self.length = 30
        self.crashed = False

        self.sensor_distances = []
        self.ray_endpoints = []

        self.image = pygame.Surface((self.width, self.length), pygame.SRCALPHA)
        self.image.fill(RED)

    def reset(self):
        self.x = self.init_x
        self.y = self.init_y
        self.angle = 0
        self.speed = 0
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
            print("Pixel under car:", pixel_color)
            if pixel_color not in [GRAY, WHITE, (0, 255, 255), (255, 255, 0)]:
                self.crashed = True
        except IndexError:
            self.crashed = True

    def cast_rays(self, surface, ray_length=150, num_rays=5, fov=90):
        self.sensor_distances = []
        self.ray_endpoints = []

        half_fov = fov / 2
        angle_between = fov / (num_rays - 1)

        for i in range(num_rays):
            ray_angle = self.angle - half_fov + i * angle_between
            distance, end_pos = self.cast_single_ray(surface, ray_angle, ray_length)
            self.sensor_distances.append(distance)
            self.ray_endpoints.append(end_pos)

    def cast_single_ray(self, surface, angle, max_length):
        rad = math.radians(-angle)
        x, y = self.x, self.y

        for length in range(max_length):
            test_x = int(x + length * math.cos(rad))
            test_y = int(y + length * math.sin(rad))

            if 0 <= test_x < surface.get_width() and 0 <= test_y < surface.get_height():
                color = surface.get_at((test_x, test_y))[:3]
                if color != GRAY and color != WHITE:
                    return length, (test_x, test_y)
            else:
                break

        return max_length, (test_x, test_y)

    def draw_rays(self, surface):
        for end in self.ray_endpoints:
            pygame.draw.line(surface, (0, 255, 255), (self.x, self.y), end, 1)
            pygame.draw.circle(surface, (255, 255, 0), end, 3)


def draw_track(surface):
    surface.fill(GREEN)

    # Outer boundary (track outer edge)
    outer = [
        (400, 150), (500, 130), (600, 120), (700, 140),
        (750, 200), (780, 300), (750, 400), (700, 460),
        (600, 480), (500, 470), (400, 450), (320, 400),
        (300, 300), (320, 200)
    ]

    # Inner boundary (track inner edge)
    inner = [
        (450, 200), (530, 185), (610, 180), (680, 190),
        (710, 240), (730, 300), (710, 370), (680, 420),
        (600, 430), (520, 420), (440, 400), (380, 360),
        (370, 300), (380, 240)
    ]

    # 1. Draw filled outer track first
    pygame.draw.polygon(surface, GRAY, outer)

    # 2. Cut out inner "hole" using green (track grass)
    pygame.draw.polygon(surface, GREEN, inner)

    # 3. Draw borders (for aesthetics)
    pygame.draw.lines(surface, WHITE, True, outer, 2)
    pygame.draw.lines(surface, WHITE, True, inner, 2)

    # 4. Draw start line
    pygame.draw.line(surface, WHITE, outer[0], inner[0], 4)


def main():
    car = Car(430, 170)  # Safe start inside track

    run = True
    while run:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        draw_track(WIN)
        car.update(keys)
        car.cast_rays(WIN)
        car.check_collision(WIN)
        car.draw(WIN)
        car.draw_rays(WIN)
       

        if car.crashed:
            font = pygame.font.SysFont(None, 48)
            text = font.render("Crashed!", True, BLACK)
            WIN.blit(text, (WIDTH // 2 - 80, HEIGHT // 2 - 20))
            pygame.display.update()
            pygame.time.delay(1000)
            car.reset()

        pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
