import random
from aucteraden.board import Board, Move, Point


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
				for row in range(Board.row_count):
					for col in range(Board.col_count):
						if game_state.is_valid_move(idx, {suit: 2 - idx}, col, row, False):
							candidates.append(Move(idx, {suit: 2 - idx}, Point(col, row), False))
			idx += 1
		#print("\nValid moves: " + str(len(candidates)))
		if len(candidates) == 0:
			return Move.churn()
		return random.choice(candidates)
