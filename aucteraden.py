import argparse
import random
import numpy as np
from aucteraden.agent import OneMoveScoreBot, RandomBot
from aucteraden.board import GameState
from aucteraden.encoders import GameStateEncoder, MoveEncoder
from decktet.deck import Deck

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--seed", "-s", type=int, default=42)
	parser.add_argument("--num-games", "-n", type=int, default=1000)
	parser.add_argument("--verbose", "-v", action="store_true", help="Print every move")
	parser.add_argument("--check-assets", "-A", action="store_true", help="Check if all card images are present")
	args = parser.parse_args()

	if args.check_assets:
		deck = Deck.make_extended()
		deck.check_assets()
		return


	feature_encoder = GameStateEncoder()
	label_encoder = MoveEncoder()

	MAX_GAME_DURATION = 20

	best_score = -10000000
	best_game = 0
	sum_score = 0
	#bot = RandomBot()
	bot = OneMoveScoreBot(25, 4)

	features = []
	labels = []

	base_fn = "%05d_%05d" % (args.seed, args.num_games)
	base_fn = f"aucteraden/generated_games/{base_fn}"

	features_fn = f"{base_fn}F"
	labels_fn   = f"{base_fn}L"
	output_fn =   f"{base_fn}.log"

	random.seed(args.seed)

	counter = 0
	with open(output_fn, "w") as file:
		for i in range(args.num_games):
			print(f"\n======== Game {i} ========", file=file)
			
			game = None
			#random.seed(args.seed + i)
			game = GameState.new_game()
			#random.seed(args.seed + i)

			turn_counter = 0
			while not game.is_over():
				if args.verbose:
					print(f"\n== Move {counter} ({turn_counter})==", file=file)
					print(game.board, file=file)
				
				features.append(feature_encoder.encode(game.board))
				bot_move = bot.select_move(game)

				if args.verbose:
					print(bot_move, file=file)

				labels.append(label_encoder.encode(bot_move))
				game = game.apply_move(bot_move)
				game.board.refill_market(True)
				counter += 1
				turn_counter += 1
			if args.verbose:
				print(f"\n==== Game {i} finished at move {counter} ({turn_counter}) ====", file=file)
			print(game.board, file=file)
			score = game.board.calculate_score()
			print(f"{i};score;{score}", file=file)

			sum_score += score
			if score > best_score:
				best_score = score
				best_game = i
		
		np.save(features_fn, np.stack(features))
		np.save(labels_fn, np.stack(labels))

		print(f"\nMax score = {best_score} on #{best_game}, avg score = {sum_score / args.num_games}", file=file)
	
	print(f"Completed {args.seed}, {args.num_games}")

if __name__ == "__main__":
	main()
