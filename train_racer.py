# train_racer.py
from stable_baselines3 import DQN
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import EvalCallback
from racing_env import RacingEnv
import os

# Setup logging and model directories
log_dir = "./logs/dqn_racer"
model_dir = "./models/"
os.makedirs(log_dir, exist_ok=True)
os.makedirs(model_dir, exist_ok=True)

# Create training environment
env = RacingEnv()
env = Monitor(env, log_dir)

# Create separate evaluation environment
eval_env = Monitor(RacingEnv(), log_dir)

# Evaluation callback to save best model
eval_callback = EvalCallback(
    eval_env,
    best_model_save_path=model_dir,
    log_path=log_dir,
    eval_freq=5000,
    deterministic=True,
    render=False
)

# Load model if it exists
model_path = os.path.join(model_dir, "best_model.zip")
if os.path.exists(model_path):
    print("🔁 Continuing training from saved model...")
    model = DQN.load(model_path, env=env, tensorboard_log=log_dir)
    model.set_env(env)  # Reset env
else:
    print("🆕 Training new model...")
    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=1e-3,
        buffer_size=100_000,
        learning_starts=1000,
        batch_size=64,
        exploration_fraction=0.3,
        exploration_final_eps=0.05,
        tau=0.1,
        gamma=0.99,
        train_freq=1,
        target_update_interval=1000,
        verbose=1,
        tensorboard_log=log_dir
    )

# Start training
model.learn(total_timesteps=1_000_000, callback=eval_callback)

# Save final model
model.save("dqn_racer_model")
print("✅ Training complete and model saved.")
