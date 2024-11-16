import random
import time

import numpy as np
from aucteraden.agent import OneMoveScoreBot, RandomBot
from aucteraden.board import GameState
from aucteraden.encoders import GameStateEncoder, MoveEncoder

def main():
	seed = 42

	feature_encoder = GameStateEncoder()
	label_encoder = MoveEncoder()

	iter_count = 1000
	MAX_GAME_DURATION = 20

	best_score = -10000000
	best_iteration = 0
	sum_score = 0
	#bot = RandomBot()
	bot = OneMoveScoreBot(25, 4)

	feature_shape = np.insert(feature_encoder.shape(), 0, MAX_GAME_DURATION)
	feature_shape = np.insert(feature_shape, 0, iter_count)
	features = np.zeros(feature_shape, dtype=np.int8)
	label_shape = np.insert(label_encoder.shape(), 0, MAX_GAME_DURATION)
	label_shape = np.insert(label_shape, 0, iter_count)
	labels = np.zeros(label_shape, dtype=np.int8)

	for i in range(iter_count):
		print(f"\n==== Game {i} ====")
		random.seed(seed)

		game = GameState.new_game()

		counter = 0
		random.seed(i)
		while not game.is_over():
			#print("\n======== Move %d =========" % counter)
			#game.board.print_board()
			features[i][counter] = feature_encoder.encode(game.board)

			bot_move = bot.select_move(game)
			#print(bot_move)
			labels[i][counter] = label_encoder.encode(bot_move)

			game = game.apply_move(bot_move)
			game.board.refill_market(True)
			counter += 1

		#print("\n======== Finished at move %d =========" % counter)
		game.board.print_board()
		score = game.board.calculate_score()
		print(f"{i};score;{score}")

		sum_score += score
		if score > best_score:
			best_score = score
			best_iteration = i
	
	features_fn = "aucteraden/generated_games/F_%05d_%05d" % (seed, iter_count)
	labels_fn = features_fn.replace("/F_", "/L_")
	np.save(features_fn, features)
	np.save(labels_fn, labels)

	print(f"\nMax score = {best_score} on #{best_iteration}, avg score = {sum_score / iter_count}")

if __name__ == "__main__":
	main()
