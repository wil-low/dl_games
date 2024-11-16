import argparse
import random
import numpy as np
from aucteraden.agent import OneMoveScoreBot, RandomBot
from aucteraden.board import GameState
from aucteraden.encoders import GameStateEncoder, MoveEncoder

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--seed", "-s", type=int, default=42)
	parser.add_argument("--num-games", "-n", type=int, default=1000)
	parser.add_argument("--verbose", "-v", action="store_true", help="Print every move")
	parser.add_argument("--single", "-1", action="store_true", help="Generate one game per seed, then increase seed")
	args = parser.parse_args()

	feature_encoder = GameStateEncoder()
	label_encoder = MoveEncoder()

	MAX_GAME_DURATION = 20

	best_score = -10000000
	best_game = 0
	sum_score = 0
	#bot = RandomBot()
	bot = OneMoveScoreBot(25, 4)

	feature_shape = np.insert(feature_encoder.shape(), 0, MAX_GAME_DURATION)
	feature_shape = np.insert(feature_shape, 0, args.num_games)
	features = np.zeros(feature_shape, dtype=np.int8)
	label_shape = np.insert(label_encoder.shape(), 0, MAX_GAME_DURATION)
	label_shape = np.insert(label_shape, 0, args.num_games)
	labels = np.zeros(label_shape, dtype=np.int8)

	base_fn = "%05d_%05d" % (args.seed, args.num_games)
	if args.single:
		base_fn = f"inc_seed/{base_fn}"
	else:
		base_fn = f"fix_seed/{base_fn}"
	base_fn = f"aucteraden/generated_games/{base_fn}"

	features_fn = f"{base_fn}F"
	labels_fn   = f"{base_fn}L"
	output_fn =   f"{base_fn}.log"

	with open(output_fn, "w") as file:
		for i in range(args.num_games):
			print(f"\n======== Game {i} ========", file=file)
			
			game = None
			if args.single:
				random.seed(args.seed + i)
				game = GameState.new_game()
				random.seed(args.seed + i)
			else:
				random.seed(args.seed)
				game = GameState.new_game()
				random.seed(i)

			counter = 0
			while not game.is_over():
				if args.verbose:
					print(f"\n== Move {counter} ==", file=file)
					print(game.board, file=file)
				
				features[i][counter] = feature_encoder.encode(game.board)
				bot_move = bot.select_move(game)

				if args.verbose:
					print(bot_move, file=file)

				labels[i][counter] = label_encoder.encode(bot_move)
				game = game.apply_move(bot_move)
				game.board.refill_market(True)
				counter += 1
			if args.verbose:
				print(f"\n==== Game {i} finished at move {counter} ====", file=file)
			print(game.board, file=file)
			score = game.board.calculate_score()
			print(f"{i};score;{score}", file=file)

			sum_score += score
			if score > best_score:
				best_score = score
				best_game = i
		
		np.save(features_fn, features)
		np.save(labels_fn, labels)

		print(f"\nMax score = {best_score} on #{best_game}, avg score = {sum_score / args.num_games}", file=file)
	
	print(f"Completed {args.seed}, {args.num_games}")

if __name__ == "__main__":
	main()
