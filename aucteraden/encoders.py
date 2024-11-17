import numpy as np
from aucteraden.board import Board, Move
from decktet.card import Card, CardSuit
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

	def decode(self, mtx):
		board = Board()
		for idx in range(3):
			card = self.decode_card(mtx, idx, 0)
			if card is not None:
				board.market.insert(0, card)
		board.chips = {}
		for suit in CardSuit:
			board.chips[suit] = mtx[suit.value][GameStateEncoder.CHIP_COL][GameStateEncoder.CHIP_ROW]
		for row in range(Board.row_count):
			for col in range(Board.col_count):
				card = self.decode_card(mtx, col, row + GameStateEncoder.FIRST_BOARD_ROW)
				if card:
					board.place_card(card, col, row)
		return board

	def shape(self):
		return len(CardSuit), 4, 5  # suit, col, row

	def encode_card(self, mtx, card, col, row):
		for suit in card.suits_list:
			mtx[suit.value][col][row] = card.type

	def decode_card(self, mtx, col, row):
		suits = []
		type = None
		for suit in CardSuit:
			t = mtx[suit.value][col][row]
			if t > 0:
				suits.append(suit)
				type = t
		if type is not None:
			return Card(type, "?", suits)
		return None


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

	def decode(self, mtx, grid16 = False):
		if mtx[MoveEncoder.CHURN_OFFSET] == 1:
			return Move.churn()
		buy_card_index = None
		payment = {}
		col = None
		row = None
		for idx in range(3):
			if mtx[MoveEncoder.BUY_OFFSET + idx] == 1:
				buy_card_index = idx
				break
		for suit in CardSuit:
			val = mtx[MoveEncoder.CHIP_OFFSET + suit.value]
			if val > 0:
				payment[suit] = val
		if grid16:
			for idx in range(16):
				if mtx[MoveEncoder.BOARD_COL_OFFSET + idx] == 1:
					col = idx % Board.col_count
					row = idx // Board.row_count
					break
		else:
			for idx in range(4):
				if mtx[MoveEncoder.BOARD_COL_OFFSET + idx] == 1:
					col = idx
					break
			for idx in range(4):
				if mtx[MoveEncoder.BOARD_ROW_OFFSET + idx] == 1:
					row = idx
					break
		return Move.buy_and_place(buy_card_index, payment, col, row)

	def decode_predict(self, mtx):
		fmt = "%.4f"
		s = "Churn: " + fmt % mtx[MoveEncoder.CHURN_OFFSET] + "\n"
		for idx in range(3):
			s += f"Buy #{idx}: " + fmt % mtx[MoveEncoder.BUY_OFFSET + idx] + "\n"
		for suit in CardSuit:
			s += f"{Card.suit_map[suit]}: " + fmt % mtx[MoveEncoder.CHIP_OFFSET + suit.value] + "\n"
		s += "        "
		for idx in range(4):
			s += fmt % mtx[MoveEncoder.BOARD_COL_OFFSET + idx] + "  "
		s += "\n"
		for idx in range(4):
			s += fmt % mtx[MoveEncoder.BOARD_ROW_OFFSET + idx] + "\n"
		return s

	def shape(self):
		return (MoveEncoder.BOARD_ROW_OFFSET + 4,)
