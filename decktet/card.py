from enum import Enum, IntEnum


class CardType(IntEnum):
	excuse = 0
	ace = 1
	number2 = 2
	number3 = 3
	number4 = 4
	number5 = 5
	number6 = 6
	number7 = 7
	number8 = 8
	number9 = 9
	pawns = 10
	courts = 11
	crowns = 12


class CardSuit(Enum):
	moons = 0
	suns = 1
	waves = 2
	leaves = 3
	wyrms = 4
	knots = 5


class CardIdentity(Enum):
	location = 0
	personality = 1
	event = 2


class Card:
	type_map = {
		CardType.excuse:  "Ex",
		CardType.ace:     "A ",
		CardType.number2: "2 ",
		CardType.number3: "3 ",
		CardType.number4: "4 ",
		CardType.number5: "5 ",
		CardType.number6: "6 ",
		CardType.number7: "7 ",
		CardType.number8: "8 ",
		CardType.number9: "9 ",
		CardType.pawns:   "Pa",
		CardType.courts:  "Co",
		CardType.crowns:  "Cr"
	}

	suit_map = {
		CardSuit.moons:  "M",
		CardSuit.suns:   "S",
		CardSuit.waves:  "W",
		CardSuit.leaves: "L",
		CardSuit.wyrms:  "Y",
		CardSuit.knots:  "K"
	}

	def __init__(self, type, name, suits, identities = [], image = ""):
		self.type = type
		self.name = name
		self.suits = set(suits)
		self.suits_list = suits
		self.ids = set(identities)
		self.image = image

	def __str__(self):
		suits = ""
		for s in self.suits_list:
			suits += Card.suit_map[s]
		return "%s %-3s" % (Card.type_map[self.type], suits)
		#return "%s %-3s: %s" % (Card.type_map[self.type], suits, self.name)

	def is_extended(self):
		return self.type == CardType.excuse or self.type == CardType.pawns or self.type == CardType.courts
