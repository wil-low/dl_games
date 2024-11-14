from decktet.card import Card, CardSuit
from decktet.deck import Deck


class Board:
	def __init__(self):
		self.col_count = 4
		self.row_count = 4
		self.grid = [[None for _ in range(self.col_count)] for _ in range(self.row_count)]
		self.deck = Deck.make_standard()
		self.market = [None, None, None]
		self.chips = {
			CardSuit.moons:  4,
			CardSuit.suns:   4,
			CardSuit.waves:  4,
			CardSuit.leaves: 4,
			CardSuit.wyrms:  4,
			CardSuit.knots:  4
		}

	def print_card(self, card):
		if card is None:
			print("." * 6, end="  ")
		else:
			print(card, end="  ")

	def print_board(self):
		print("Deck: %d      Chips: " % len(self.deck.cards), end="")
		for suit, count in self.chips.items():
			print("%s: %d" % (Card.suit_map[suit], count), end="  ")
		print()
		print()
		print("    ", end="")
		for mcard in self.market:
			self.print_card(mcard)
		print()
		print()
		for row in range(self.row_count):
			for col in range(self.col_count):
				card = self.grid[row][col]
				#card = self.deck.cards[row * self.col_count + col]
				self.print_card(card)
			print()
			print()

