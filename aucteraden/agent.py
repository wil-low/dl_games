import copy
import random
from aucteraden.board import Board, Move
from aucteraden.encoders import GameStateEncoder, MoveEncoder


class Agent:
	def __init__(self):
		pass

	def select_move(self, game_state):
		raise NotImplementedError()
	
	def chip_combos(self, card, cost):
		suit_count = len(card.suits_list)
		if cost == 1:
			if suit_count == 1:
				return [{card.suits_list[0]: 1}]
			elif suit_count == 2:
				return [{card.suits_list[0]: 1}, {card.suits_list[1]: 1}]
		elif cost == 2:
			if suit_count == 1:
				return [{card.suits_list[0]: 2}]
			elif suit_count == 2:
				return [{card.suits_list[0]: 1, card.suits_list[1]: 1}, {card.suits_list[0]: 2}, {card.suits_list[1]: 2}]
		return [{}]

class RandomBot(Agent):
	def select_move(self, game_state):
		candidates = []
		cost = 0
		for mcard in reversed(game_state.board.market):
			idx = len(game_state.board.market) - cost - 1
			for chips in self.chip_combos(mcard, cost):
				for col, row in game_state.board.free_cells:
					move = Move.buy_and_place(idx, chips, col, row)
					if game_state.board.is_valid_move(move, True):
						candidates.append(move)
			cost += 1
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
		cost = 0
		for mcard in reversed(game_state.board.market):
			idx = len(game_state.board.market) - cost - 1
			#print(f"select_move {idx}: {mcard}, cost {cost}")
			for chips in self.chip_combos(mcard, cost):
				for col, row in game_state.board.free_cells:
					move = Move.buy_and_place(idx, chips, col, row)
					if game_state.board.is_valid_move(move, True):
						next_state = game_state.apply_move(move)
						next_score = next_state.board.calculate_score()
						#print(f"select_move {idx}: ({col}, {row}), {mcard}, cost {cost}, score {next_score}: {next_score >= best_score}")
						if next_score >= best_score:
							candidates.append(move)
							best_score = next_score
							if not game_state.board.grid_empty and len(candidates) == self.max_candidates_count:
								return self.select_candidate(game_state, candidates)
			cost += 1
		return self.select_candidate(game_state, candidates)
	
	def select_candidate(self, game_state, candidates):
		#print("\nValid moves: " + str(len(candidates)))
		if len(candidates) == 0:
			return Move.churn()
		if not game_state.board.grid_empty:
			return random.choice(candidates[-self.upper_limit:])
		return random.choice(candidates)


class RandomGymBot(Agent):
	def __init__(self):
		super().__init__()
		self.game_state_encoder = GameStateEncoder()
		self.move_encoder = MoveEncoder()

	def get_action(self, obs):
		board = self.game_state_encoder.decode(obs)
		move = self.select_move(board)
		result = self.move_encoder.encode(move)
		print(f"move: {move}\nget_action: {result}")
		return result

	def select_move(self, board):
		candidates = []
		cost = 0
		for mcard in reversed(board.market):
			idx = len(board.market) - cost - 1
			for chips in self.chip_combos(mcard, cost):
				for col, row in board.free_cells:
					move = Move.buy_and_place(idx, chips, col, row)
					if board.is_valid_move(move, True):
						candidates.append(move)
			cost += 1
		#print("\nValid moves: " + str(len(candidates)))
		if len(candidates) == 0:
			return Move.churn()
		return random.choice(candidates)
