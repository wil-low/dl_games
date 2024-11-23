import copy
import random
from decktet.card import Card, CardSuit, CardType
from decktet.deck import Deck


# Define directions for neighbors (up, down, left, right)
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class Board:
	initial_chip_count = 4
	col_count = 4
	row_count = 4
	standard_deck = Deck.make_standard()

	def __init__(self):
		self.grid = []
		self.free_cells = set()
		for row in range(Board.row_count):
			for col in range(Board.col_count):
				self.grid.append(None)
				self.free_cells.add((col, row))
		self.grid_empty = True
		self.score = 0
		self.market = []
		self.chips = {}
		self.deck = Deck([])

	def prepare(self):
		self.deck = copy.deepcopy(Board.standard_deck)
		random.shuffle(self.deck.cards)
		self.chips = {
			CardSuit.moons:  Board.initial_chip_count,
			CardSuit.suns:   Board.initial_chip_count,
			CardSuit.waves:  Board.initial_chip_count,
			CardSuit.leaves: Board.initial_chip_count,
			CardSuit.wyrms:  Board.initial_chip_count,
			CardSuit.knots:  Board.initial_chip_count
		}
		self.refill_market(False)
		
	def get_card(self, col, row):
		if col < 0 or col >= Board.col_count:
			return None
		if row < 0 or row >= Board.row_count:
			return None
		return self.grid[col + row * Board.col_count]

	def str_card(self, card):
		if card is None:
			return "." * 6 + "  "
		return f"{card}  "

	def __str__(self):
		s = "Deck: %d      Chips: " % len(self.deck.cards)
		for suit, count in self.chips.items():
			s += "%s:%d  " % (Card.suit_map[suit], count)
		s += "\n\n    "
		s += str()
		s += self.str_market() + "\n"
		for row in range(Board.row_count):
			for col in range(Board.col_count):
				card = self.get_card(col, row)
				#card = self.deck.cards[row * Board.col_count + col]
				s += self.str_card(card)
			s += "\n\n"
		return s

	def str_market(self):
		s = ""
		for mcard in self.market:
			s += self.str_card(mcard)
		s += "\n"
		return s

	def refill_market(self, is_discard):
		if is_discard:
			card = self.deck.take_card()
			if card is None:
				return
			#print("Card for discards: " + str(card) + ", market:")
			#self.print_market()
			self.market = [x for x in self.market if not bool(x.suits & card.suits)]
			self.market.insert(0, card)
		while len(self.market) < 3:
			if len(self.deck.cards) > 0:
				card = self.deck.take_card()
				if card is None:
					return
				self.market.insert(0, card)
			else:
				break

	def buy_card(self, idx, payment):
		card = self.market.pop(idx)
		for suit, count in payment.items():
			self.chips[suit] -= count
		return card

	def place_card(self, card, col, row):
		idx = col + row * Board.col_count
		self.grid[idx] = card
		self.free_cells.remove((col, row))
		self.grid_empty = False

	def chain_score(self, chain):
		score = 0
		first_ace = chain[0][0].type == CardType.ace
		last_crowns = chain[-1][0].type == CardType.crowns
		if first_ace and last_crowns:
			score = 4
		elif first_ace:
			score = 1
		elif last_crowns:
			score = 2

		l = len(chain)
		if l >=7:
			score += 30
		elif l == 6:
			score += 20
		elif l == 5:
			score += 14
		elif l == 4:
			score += 9
		elif l == 3:
			score += 5
		elif l == 2:
			score += 2
		else:
			score += -5
		return score

	def find_longest_chains_by_suit(self):
		rows, cols = Board.row_count, Board.col_count
		longest_chains_by_suit = {}

		# DFS function to explore chains
		def dfs(suit, r, c, chain):
			#print(f"dfs enter {r}, {c} suit {suit}: {chain}")
			card = self.get_card(c, r)
			if card is None or suit not in card.suits:
				return
			current_num = card.type
			chain.append((card, c, r))  # Add current card to the chain
			#print(f"append {suit} - {r}, {c}: {chain}")
			dead_end = True
			# Explore all four possible neighbors
			for dr, dc in directions:
				nr, nc = r + dr, c + dc
				if 0 <= nr < rows and 0 <= nc < cols:
					ncard = self.get_card(nc, nr)
					if ncard is not None:
						neighbor_num = ncard.type
						# Check for ascending order and same suit
						if suit in ncard.suits and neighbor_num > current_num:
							#print(f"suit {suit}: descend from {r}, {c} to {nr}, {nc}: {neighbor_num} > {current_num}")
							dfs(suit, nr, nc, chain)
							dead_end = False
			if dead_end and len(chain) > 0:
				chains.append(copy.deepcopy(chain))
				#print(f"Chain added: {chain}")

			# Backtrack: remove the current cell from the path
			chain.pop()

		for suit in CardSuit:
			max_score = -10000000
			chains = []
			#print(f"===== Scan for suit {suit} =====\n")
			# Iterate over each cell in the board
			for r in range(rows):
				for c in range(cols):
					# Start a new chain from each cell
					dfs(suit, r, c, [])
					for chain in chains:
						#print(f"dfs returned {chain}")

						# Update longest chain for the suit if this chain is longer
						ch_score = self.chain_score(chain)
						if suit not in longest_chains_by_suit or ch_score > max_score:
							max_score = ch_score
							#print(f"new longest chain for suit {suit}: {list(map(str, chain))}, score: {ch_score}\n")
							longest_chains_by_suit[suit] = (chain, ch_score)
		return longest_chains_by_suit

	def calculate_score(self):
		score = self.score
		for suit, count in self.chips.items():
			if count == 0 or count == Board.initial_chip_count:
				score -= 5
		for card in self.grid:
			if card is None:
				score -= 5

		longest_chains = self.find_longest_chains_by_suit()
		for suit, (chain, ch_score) in longest_chains.items():
			#print(f"Longest chain for suit {suit}: {list(map(str, chain))}, score: {ch_score}")
			score += ch_score

		return score, longest_chains

	def is_valid_move(self, move, check_payment):
		if move.churn_market:
			return True

		if check_payment and not self.is_valid_payment(move.payment):
			return False

		if self.get_card(move.col, move.row) is not None:
			return False

		mcard = self.market[move.buy_card_index]
		if not self.grid_empty:
			has_neighbour = False
			for dr, dc in directions:
				gcard = self.get_card(move.col + dc, move.row + dr)
				if gcard is not None:
					if (mcard.type == CardType.ace or mcard.type == CardType.crowns) and (gcard.type == CardType.ace or gcard.type == CardType.crowns):
						return False
					has_neighbour = True
			return has_neighbour

		return True
	
	def is_valid_payment(self, payment):
		for suit, count in payment.items():
			if self.chips[suit] < count:
				return False
		return True

	def apply_move(self, move):
		card = None
		next_board = copy.deepcopy(self)
		if move.buy_card_index is not None:
			card = next_board.buy_card(move.buy_card_index, move.payment)
		if move.churn_market:
			next_board.market = []
			next_board.score -= 3
		else:
			next_board.place_card(card, move.col, move.row)
		return next_board

class Move:
	def __init__(self, buy_card_index=None, payment={}, col=None, row=None, churn_market=False):
		#assert (buy_card_index is None) ^ (len(payment) == (2 - buy_card_index))
		self.buy_card_index = buy_card_index
		self.payment = payment
		self.col = col
		self.row = row
		self.churn_market = churn_market
	
	@classmethod
	def buy_and_place(cls, buy_card_index, payment, col, row):
		return Move(buy_card_index, payment, col, row, False)

	@classmethod
	def churn(cls):
		return Move(None, {}, None, None, True)
	
	def __str__(self):
		result = ""
		if self.buy_card_index is not None:
			result += "Buy card #%d, " % self.buy_card_index

		if len(self.payment) > 0:
			result += "Pay "
		for suit, count in self.payment.items():
			result += "%s:%d, " % (Card.suit_map[suit], count)

		if self.col is not None:
			result += "Place card into (%d, %d)" % (self.col, self.row)

		if self.churn_market:
			result = "Churn market"
		return result


class GameState:
	def __init__(self, board, previous, move):
		self.board = board
		self.previous_state = previous
		self.last_move = move

	@classmethod
	def new_game(cls):
		board = Board()
		board.prepare()
		return GameState(board, None, None)

	def apply_move(self, move):
		return GameState(self.board.apply_move(move), self, move)
	
	def is_over(self):
		return len(self.board.deck.cards) == 0 or len(self.board.free_cells) == 0

