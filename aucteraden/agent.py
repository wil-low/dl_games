import copy
import random
from aucteraden.board import Board, Move


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
						move = Move(2 - idx, {suit: idx}, col, row, False)
						if game_state.is_valid_move(move):
							candidates.append(move)
			idx += 1
		#print("\nValid moves: " + str(len(candidates)))
		if len(candidates) == 0:
			return Move.churn()
		return random.choice(candidates)


class OneMoveScoreBot(Agent):
	def __init__(self, max_candidates_count, upper_limit):
		super().__init__()
		self.max_candidates_count = max_candidates_count
		self.upper_limit = upper_limit

	def select_move(self, game_state):
		candidates = []
		best_score = -100000000
		idx = 0
		for mcard in game_state.board.market:
			for suit in mcard.suits_list:
				for row in range(Board.row_count):
					for col in range(Board.col_count):
						move = Move(2 - idx, {suit: idx}, col, row, False)
						if game_state.is_valid_move(move):
							next_state = game_state.apply_move(move)
							next_score = next_state.board.calculate_score()
							if next_score >= best_score:
								candidates.append(move)
								best_score = next_score
								if len(candidates) == self.max_candidates_count:
									return random.choice(candidates[-self.upper_limit:])
			idx += 1
		#print("\nValid moves: " + str(len(candidates)))
		if len(candidates) == 0:
			return Move.churn()
		return random.choice(candidates[-self.upper_limit:])
