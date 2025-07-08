# evaluate_racer.py
import numpy as np
import time
import pygame
from stable_baselines3 import DQN
from racing_env import RacingEnv

env = RacingEnv()
model = DQN.load("dqn_racer_model")

# Pygame display window
WIN = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Trained Agent Evaluation")


obs, _ = env.reset()
done = False

episodes = 20

for ep in range(episodes):
    obs, info = env.reset()
    done = False
    total_reward = 0
    steps = 0

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                env.close()
                pygame.quit()
                exit()

        obs = np.array(obs, dtype=np.float32)  # <- Ensure correct format
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated,truncated, info = env.step(action)
        done = terminated or truncated
        total_reward += reward
        steps += 1

        # Render with your car drawing and track
        draw_surface = pygame.display.get_surface()
        draw_surface.blit(env.surface, (0, 0))
        env.car.draw(draw_surface)
        pygame.display.flip()

        env.render()
        print(f"[EP {ep+1}] Step: {steps}, Reward: {reward:.2f}, Checkpoint: {info.get('checkpoints', '-')}, Lap: {info.get('laps', '-')}")
        print(f"Obs: {obs}, Action: {action}")
        time.sleep(0.016)  # ~60 FPS

    print(f"\n✅ Episode {ep+1} finished | Total Reward: {total_reward:.2f} | Steps: {steps}\n")

env.close()
pygame.quit()