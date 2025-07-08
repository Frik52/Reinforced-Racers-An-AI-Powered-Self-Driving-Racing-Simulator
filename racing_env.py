import gymnasium as gym
import numpy as np
import pygame
import math
from car_sim import Car, draw_track

WIDTH, HEIGHT = 800, 600

checkpoints = [
    ((440, 180), (490, 180)),
    ((580, 125), (580, 185)),
    ((660, 140), (660, 200)),
    ((730, 270), (780, 270)),
    ((760, 350), (710, 350)),
    ((660, 420), (620, 470)),
    ((500, 450), (500, 490)),
    ((370, 390), (420, 430)),
    ((340, 270), (390, 310)),
    ((420, 150), (470, 190))
]

class RacingEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self):
        super().__init__()
        pygame.init()
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        self.display = None  # Only used in render()

        self.car = Car(425, 190)
        self.checkpoints = checkpoints
        self.prev_checkpoint = 0
        self.laps = 0
        self.steps = 0
        self.max_steps = 1500

        # Action: [0: nothing, 1: accelerate, 2: brake, 3: turn left, 4: turn right]
        self.action_space = gym.spaces.Discrete(5)

        # Observation: 9 sensors + 1 speed = 10
        self.observation_space = gym.spaces.Box(
            low=0, high=1, shape=(10,), dtype=np.float32
        )

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            self.np_random = np.random.default_rng(seed)

        self.car.reset()
        self.prev_checkpoint = 0
        self.laps = 0
        self.steps = 0

        draw_track(self.surface)
        self.car.cast_rays(self.surface)

        obs = self._get_state()
        return obs, self._get_info()

    def _get_state(self):
        self.car.cast_rays(self.surface)
        sensors = [min(d / 150, 1.0) for d in self.car.sensor_distances]
        speed = self.car.speed / self.car.max_speed
        return np.array(sensors + [speed], dtype=np.float32)

    def _get_info(self):
        return {
            "checkpoints": self.car.checkpoint_index,
            "laps": self.laps,
            "steps": self.steps,
            "speed": self.car.speed,
            "crashed": self.car.crashed
        }

    def step(self, action):
        self.steps += 1
        reward = 0.0
        reward = 0.1 *self.car.speed

        if self.car.crashed:
            reward = -10.0
            return self._get_state(), reward, True, False, self._get_info()

        # Apply discrete actions
        if action == 1:
            self.car.speed = min(self.car.speed + self.car.acceleration, self.car.max_speed)
        elif action == 2:
            self.car.speed = max(self.car.speed - self.car.acceleration, -self.car.max_speed / 2)
        elif action == 3:
            self.car.angle += self.car.turn_speed * (self.car.speed / self.car.max_speed)
        elif action == 4:
            self.car.angle -= self.car.turn_speed * (self.car.speed / self.car.max_speed)

        rad = math.radians(-self.car.angle)
        self.car.x += self.car.speed * math.cos(rad)
        self.car.y += self.car.speed * math.sin(rad)

        draw_track(self.surface)
        self.car.check_collision(self.surface)
        self.car.check_checkpoint(self.checkpoints)

        reward = -0.01  # Small time penalty

        if self.car.checkpoint_index > self.prev_checkpoint:
            reward += 1.0
            self.prev_checkpoint = self.car.checkpoint_index

        # Completed a full lap
        if self.car.checkpoint_index == 0 and self.prev_checkpoint == len(self.checkpoints):
            reward += 20.0
            self.prev_checkpoint = 0
            self.laps += 1

        terminated = self.car.crashed or self.laps > 0
        truncated = self.steps >= self.max_steps

        return self._get_state(), reward, terminated, truncated, self._get_info()

    def render(self, mode='human'):
        if self.display is None:
            self.display = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Racing Agent")

        self.display.blit(self.surface, (0, 0))
        self.car.draw(self.display)
        pygame.display.flip()

    def close(self):
        pygame.quit()
