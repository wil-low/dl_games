import random
import time
from aucteraden.agent import OneMoveScoreBot, RandomBot
from aucteraden.board import GameState

def generate_game(bot, game_idx):
	random.seed(42)
	game = GameState.new_game()

	counter = 0
	random.seed(game_idx)
	while not game.is_over():
		print("\n======== Move %d =========" % counter)
		game.board.print_board()

		bot_move = bot.select_move(game)
		print(bot_move)
		game = game.apply_move(bot_move)
		game.board.refill_market(True)
		counter += 1

	print("\n======== Finished at move %d =========" % counter)
	game.board.print_board()
	#print("\nTotal score: %d" % game.calculate_score())
	return (counter, game.board.calculate_score())

def main():
	iter_count = 100

	best_score = -10000000
	best_iteration = 0
	sum_score = 0
	#bot = RandomBot()
	bot = OneMoveScoreBot(25, 4)

	for i in range(iter_count):
		print(f"\n==== Game {i} ====")
		move_counter, score = generate_game(bot, i)
		print(f"{i};score;{score}")
		sum_score += score
		if score > best_score:
			best_score = score
			best_iteration = i
	print(f"\nMax score = {best_score} on #{best_iteration}, avg score = {sum_score / iter_count}")

if __name__ == "__main__":
	main()
