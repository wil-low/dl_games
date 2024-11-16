import numpy as np
from aucteraden.board import Board
from decktet.card import CardSuit
from encoders.base import Encoder


class GameStateEncoder(Encoder):
	MARKET_ROW = 0
	CHIP_ROW = 0
	CHIP_COL = 3
	FIRST_BOARD_ROW = 1

	def name(self):
		return "GameStateEncoder"

	def encode(self, board):
		mtx = np.zeros(self.shape(), dtype=np.int8)
		idx = 0
		for card in reversed(board.market):
			self.encode_card(mtx, card, idx, 0)
			idx += 1
		for suit, count in board.chips.items():
			mtx[suit.value][GameStateEncoder.CHIP_COL][GameStateEncoder.CHIP_ROW] = count
		for row in range(Board.row_count):
			for col in range(Board.col_count):
				card = board.get_card(col, row)
				if card:
					self.encode_card(mtx, card, col, row + GameStateEncoder.FIRST_BOARD_ROW)
		return mtx

	def decode(self):
		raise NotImplementedError

	def shape(self):
		return len(CardSuit), 4, 5  # suit, col, row

	def encode_card(self, mtx, card, col, row):
		for suit in card.suits_list:
			mtx[suit.value][col][row] = card.type


class MoveEncoder(Encoder):
	CHURN_OFFSET = 0
	BUY_OFFSET = 1
	CHIP_OFFSET = 4
	BOARD_COL_OFFSET = 10
	BOARD_ROW_OFFSET = 14

	def name(self):
		return "MoveEncoder"

	def encode(self, move):
		mtx = np.zeros(self.shape(), dtype=np.int8)
		if move.churn_market:
			mtx[MoveEncoder.CHURN_OFFSET] = 1
		else:
			mtx[MoveEncoder.BUY_OFFSET + move.buy_card_index] = 1
			for suit, count in move.payment.items():
				mtx[MoveEncoder.CHIP_OFFSET + suit.value] = count
			mtx[MoveEncoder.BOARD_COL_OFFSET + move.col] = 1
			mtx[MoveEncoder.BOARD_ROW_OFFSET + move.row] = 1
		return mtx

	def decode(self):
		raise NotImplementedError

	def shape(self):
		return (MoveEncoder.BOARD_ROW_OFFSET + 4,)
