import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Self-Driving Car with Aligned Checkpoints")

# Colors
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
GREEN = (40, 120, 40)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# FPS
FPS = 60
clock = pygame.time.Clock()

# ✅ Updated, aligned checkpoints
checkpoints = [
    # ((450, 150), (450, 200)),   # Start line
    ((580, 125), (580, 185)),   # Post-turn 1
    ((660, 140), (660, 200)),   # Wide curve
    ((730, 270), (780, 270)),   # Hairpin entry
    ((760, 350), (710, 350)),   # Hairpin exit
    ((660, 420), (620, 470)),   # Back straight
    ((500, 420), (500, 470)),   # Tight right
    ((370, 350), (350, 420)),   # Inner corner
    ((310, 270), (370, 310)),   # Final chicane
    ((420, 150), (470, 190))    # Finish approach
]

def is_similar_color(c1, c2, tolerance=30):
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))

class Car:
    def __init__(self, x, y):
        self.init_x = x
        self.init_y = y
        self.x = x
        self.y = y
        self.angle = -10
        self.speed = 0
        self.max_speed = 5
        self.acceleration = 0.1
        self.turn_speed = 4
        self.width = 15
        self.length = 30
        self.crashed = False

        self.sensor_distances = []
        self.ray_endpoints = []

        self.checkpoint_index = 0
        self.laps = 0

        self.image = pygame.Surface((self.width, self.length), pygame.SRCALPHA)
        self.image.fill(RED)

    def reset(self):
        self.x = self.init_x
        self.y = self.init_y
        self.angle = -10
        self.speed = 0
        self.crashed = False
        self.checkpoint_index = 0
        self.laps = 0

    def ai_control(self):
        if self.crashed or len(self.sensor_distances) < 9:
            return
    
        # Assign sensor distances
        L2, L1, FL, FFL, F, FFR, FR, R1, R2 = self.sensor_distances
    
        forward_threshold = 80
        panic_threshold = 30
    
        # Speed control
        if F > forward_threshold:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        else:
            self.speed *= 0.85  # Slow down if front is blocked
    
        # Steering decision
        left_total = L2 + L1 + FL + FFL
        right_total = FR + R1 + R2 + FFR
        steer = (right_total - left_total) / 400.0  # More rays, so scale up denominator
        self.angle += steer * self.turn_speed
    
        # Emergency dodge
        if F < panic_threshold:
            if FL + FFL < FR + FFR:
                self.angle += self.turn_speed
            else:
                self.angle -= self.turn_speed
    
        # Apply movement
        rad = math.radians(-self.angle)
        dx = self.speed * math.cos(rad)
        dy = self.speed * math.sin(rad)
        self.x += dx
        self.y += dy


    def check_collision(self, surface):
        try:
            pixel_color = surface.get_at((int(self.x), int(self.y)))[:3]
            safe_colors = [GRAY, WHITE, CYAN, YELLOW]
            if not any(is_similar_color(pixel_color, safe, 30) for safe in safe_colors):
                self.crashed = True
        except IndexError:
            self.crashed = True

    def cast_rays(self, surface, ray_length=150, num_rays=9, fov=150):
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
                if color not in [GRAY, WHITE]:
                    return length, (test_x, test_y)
            else:
                break

        return max_length, (test_x, test_y)

    def draw(self, surface):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(rotated_image, new_rect.topleft)

    def draw_rays(self, surface):
        for end in self.ray_endpoints:
            pygame.draw.line(surface, CYAN, (self.x, self.y), end, 2)
            pygame.draw.circle(surface, YELLOW, end, 3)

    def check_checkpoint(self, checkpoints):
        if self.crashed or self.checkpoint_index >= len(checkpoints):
            return

        start, end = checkpoints[self.checkpoint_index]

        def ccw(A, B, C):
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

        def intersect(A, B, C, D):
            return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

        front = (self.x, self.y)
        prev = (self.x - self.speed * math.cos(math.radians(-self.angle)),
                self.y - self.speed * math.sin(math.radians(-self.angle)))

        if intersect(start, end, prev, front):
            self.checkpoint_index += 1

            if self.checkpoint_index >= len(checkpoints):
                self.laps += 1
                print(f"🎉 Lap {self.laps} completed!")
                self.checkpoint_index = 0


def draw_track(surface):
    surface.fill(GREEN)

    outer = [
        (400, 150), (500, 130), (600, 120), (700, 140),
        (750, 200), (780, 300), (750, 400), (700, 460),
        (600, 480), (500, 470), (400, 450), (320, 400),
        (300, 300), (320, 200)
    ]

    inner = [
        (450, 200), (530, 185), (610, 180), (680, 190),
        (710, 240), (730, 300), (710, 370), (680, 420),
        (600, 430), (520, 420), (440, 400), (380, 360),
        (370, 300), (380, 240)
    ]

    pygame.draw.polygon(surface, GRAY, outer)
    pygame.draw.polygon(surface, GREEN, inner)
    pygame.draw.lines(surface, WHITE, True, outer, 2)
    pygame.draw.lines(surface, WHITE, True, inner, 2)
    pygame.draw.line(surface, WHITE, outer[0], inner[0], 4)


def main():
    car = Car(420, 160)
    run = True

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        draw_track(WIN)

        car.cast_rays(WIN)
        car.ai_control()
        car.check_collision(WIN)
        car.check_checkpoint(checkpoints)
        car.draw(WIN)
        car.draw_rays(WIN)

        # ✅ Draw checkpoints last — to avoid collision misdetection
        for i, (start, end) in enumerate(checkpoints):
            color = YELLOW if i == car.checkpoint_index else (100, 100, 100)
            pygame.draw.line(WIN, color, start, end, 2)

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
