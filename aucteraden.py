import random
import time
from aucteraden.agent import RandomBot
from aucteraden.board import GameState

def generate_game():
	game = GameState.new_game()
	bot = RandomBot()

	counter = 1
	#random.seed(None)
	while not game.is_over():
		#time.sleep(0.3)
		#print("\n======== Move %d =========" % counter)
		#game.board.print_board()

		bot_move = bot.select_move(game)
		#print(bot_move)
		#print()
		game = game.apply_move(bot_move)
		game.board.refill_market(True)
		counter += 1

	#print("\n======== Finished at move %d =========" % counter)
	#game.board.print_board()
	#print("\nTotal score: %d" % game.calculate_score())
	return (counter, game.calculate_score())

def main():
	random.seed(42)
	best_score = -10000000
	best_iteration = 0
	for i in range(1000):
		move_counter, score = generate_game()
		#print(f"{i}: moves={move_counter}, score={score}")
		if score > best_score:
			best_score = score
			best_iteration = i
	print(f"Max score = {best_score} on #{best_iteration}")

if __name__ == "__main__":
	main()
