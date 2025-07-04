import copy
import random

import numpy as np
import tensorflow as tf
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


class GymAgent(Agent):
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
						next_score, _ = next_state.board.calculate_score()
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


class RandomGymBot(GymAgent):
	def __init__(self):
		super().__init__()

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


class OneMoveScoreGymBot(GymAgent):
	def __init__(self, max_candidates_count, upper_limit):
		super().__init__()
		self.max_candidates_count = max_candidates_count
		self.upper_limit = upper_limit

	def select_move(self, board):
		candidates = []
		best_score = -100000000
		cost = 0
		for mcard in reversed(board.market):
			idx = len(board.market) - cost - 1
			#print(f"select_move {idx}: {mcard}, cost {cost}")
			for chips in self.chip_combos(mcard, cost):
				for col, row in board.free_cells:
					move = Move.buy_and_place(idx, chips, col, row)
					if board.is_valid_move(move, True):
						next_board = board.apply_move(move)
						next_score, _ = next_board.calculate_score()
						#print(f"select_move {idx}: ({col}, {row}), {mcard}, cost {cost}, score {next_score}: {next_score >= best_score}")
						if next_score >= best_score:
							candidates.append(move)
							best_score = next_score
							if not board.grid_empty and len(candidates) == self.max_candidates_count:
								return self.select_candidate(board, candidates)
			cost += 1
		return self.select_candidate(board, candidates)
	
	def select_candidate(self, board, candidates):
		#print("\nValid moves: " + str(len(candidates)))
		if len(candidates) == 0:
			return Move.churn()
		if not board.grid_empty:
			return random.choice(candidates[-self.upper_limit:])
		return random.choice(candidates)


class ModelGymBot(GymAgent):
	def __init__(self, model):
		super().__init__()
		self.model = model
		self.model.summary()
		checkpoint_path = f"aucteraden/training_1/{self.model.name}.weights.h5"
		print(f"Load weights from {checkpoint_path}")
		self.model.load_weights(checkpoint_path)

	def get_action(self, obs):
		predict_board = obs.reshape(1, 120)
		move_probs = self.model.predict(predict_board)
		flattened_tensors = [tf.reshape(t, [-1]) for t in move_probs]
		mtx = tf.concat(flattened_tensors, axis=0)
		print(self.move_encoder.decode_predict(mtx))
		mtx = np.array(mtx)
		#if mtx[MoveEncoder.CHURN_OFFSET] == 1:
		#	return Move.churn()
		board = self.game_state_encoder.decode(obs)
		print(f"Board: {board}")

		candidates = []
		cost = 0
		for mcard in reversed(board.market):
			#print(f"Market card: {mcard}")
			idx = len(board.market) - cost - 1
			buy_prob = mtx[MoveEncoder.BUY_OFFSET + idx]
			for chips in self.chip_combos(mcard, cost):
				chip_prob = 0
				for suit, count in chips.items():
					chip_prob += mtx[MoveEncoder.CHIP_OFFSET + suit.value]
				for col, row in board.free_cells:
					grid_prob = mtx[MoveEncoder.BOARD_COL_OFFSET + col + row * Board.col_count]
					move = Move.buy_and_place(idx, chips, col, row)
					is_valid = board.is_valid_move(move, True)
					#print(f"Check move: {move} = {is_valid}") 
					if is_valid:
						prob = 100 * buy_prob + 10 * chip_prob + grid_prob
						#print(f"Move: {move}, prob {buy_prob} + {chip_prob} + {grid_prob} = {prob}")
						candidates.append((prob, move))
			cost += 1

		if len(candidates) == 0:
			print(f"Move failed, churn")
			move = Move.churn()
			return self.move_encoder.encode(move)

		candidates.sort(reverse=True, key=lambda item: item[0])
		#for prob, move in candidates:
		#	print(f"{prob}: {move}")
		_, move = candidates[0]
		result = self.move_encoder.encode(move)
		print(f"Best move: {move}")
		return result
