import random
import time
from aucteraden.agent import RandomBot
from aucteraden.board import GameState

def main():
	random.seed(42)
	game = GameState.new_game()
	bot = RandomBot()

	counter = 1
	random.seed(None)
	while not game.is_over():
		#time.sleep(0.3)
		print("\n======== Move %d =========" % counter)
		game.board.print_board()

		bot_move = bot.select_move(game)
		print(bot_move)
		print()
		game = game.apply_move(bot_move)
		game.board.refill_market(True)
		counter += 1

	print("\n======== Finished at move %d =========" % counter)
	game.board.print_board()
	print("\nTotal score: %d" % game.calculate_score())

if __name__ == "__main__":
	main()
