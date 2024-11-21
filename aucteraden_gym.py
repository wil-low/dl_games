
from aucteraden.agent import OneLayerModelGymBot, OneMoveScoreGymBot, RandomGymBot
import gymnasium as gym
import numpy as np
from gymnasium.utils.play import play
from gymnasium.wrappers import RecordEpisodeStatistics, RecordVideo

from gymnasium_env.aucteraden import AucteradenEnv

record_video = False

gym.register(
	id="Aucteraden-v0",
	entry_point="gymnasium_env.aucteraden:AucteradenEnv",
)

render_mode = "human"
if record_video:
	render_mode = "rgb_array"

env = gym.make("Aucteraden-v0", render_mode=render_mode)

if record_video:
	env = RecordVideo(env, video_folder="random-gym-agent", name_prefix="eval", episode_trigger=lambda x: True)
	env = RecordEpisodeStatistics(env, buffer_length=1)

#agent = RandomGymBot()
#agent = OneMoveScoreGymBot(25, 4)
agent = OneLayerModelGymBot("aucteraden/training_1/cp.weights.h5")

while render_mode == "human":
	observation, info = env.reset()

	episode_over = False
	while not episode_over:
		action = agent.get_action(observation)
		observation, reward, terminated, truncated, info = env.step(action)
		episode_over = terminated or truncated

	env.render()

print("Terminated, press any key...")
input()
env.close()
