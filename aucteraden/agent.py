import random
from aucteraden.board import Move, Point


class Agent:
	def __init__(self):
		pass

	def select_move(self, game_state):
		raise NotImplementedError()


class RandomBot(Agent):
	def select_move(self, game_state):
		candidates = []
		idx = 0
		for mcard in game_state.board.market:
			for suit in mcard.suits_list:
				for row in range(game_state.board.row_count):
					for col in range(game_state.board.col_count):
						move = Move(idx, {suit: 2 - idx}, Point(col, row), False)
						if game_state.is_valid_move(move):
							candidates.append(move)
			idx += 1
		print("\nValid moves: " + str(len(candidates)))
		if len(candidates) == 0:
			return Move.churn()
		return random.choice(candidates)
