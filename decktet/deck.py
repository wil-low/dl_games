import os
from decktet.card import Card, CardIdentity, CardSuit, CardType


class Deck:
	def __init__(self, cards):
		self.cards = cards
	
	@classmethod
	def make_extended(cls):
		deck = Deck([
			Card(CardType.excuse,  "Excuse",        []),

			Card(CardType.ace,     "Ace of Moons",  [CardSuit.moons]),
			Card(CardType.ace,     "Ace of Suns",   [CardSuit.suns]),
			Card(CardType.ace,     "Ace of Waves",  [CardSuit.waves]),
			Card(CardType.ace,     "Ace of Leaves", [CardSuit.leaves]),
			Card(CardType.ace,     "Ace of Wyrms",  [CardSuit.wyrms]),
			Card(CardType.ace,     "Ace of Knots",  [CardSuit.knots]),

			Card(CardType.number2, "Desert",        [CardSuit.suns, CardSuit.wyrms],   [CardIdentity.location]),
			Card(CardType.number2, "Origin",        [CardSuit.waves, CardSuit.leaves], [CardIdentity.location, CardIdentity.event]),
			Card(CardType.number2, "Author",        [CardSuit.moons, CardSuit.knots],  [CardIdentity.personality]),

			Card(CardType.number3, "Painter",       [CardSuit.suns, CardSuit.knots],   [CardIdentity.personality]),
			Card(CardType.number3, "Savage",        [CardSuit.leaves, CardSuit.wyrms], [CardIdentity.personality]),
			Card(CardType.number3, "Journey",       [CardSuit.moons, CardSuit.waves],  [CardIdentity.event]),

			Card(CardType.number4, "Mountain",      [CardSuit.moons, CardSuit.suns],   [CardIdentity.location]),
			Card(CardType.number4, "Sailor",        [CardSuit.waves, CardSuit.leaves], [CardIdentity.personality]),
			Card(CardType.number4, "Battle",        [CardSuit.wyrms, CardSuit.knots],  [CardIdentity.event]),

			Card(CardType.number5, "Forest",        [CardSuit.moons, CardSuit.leaves], [CardIdentity.location]),
			Card(CardType.number5, "Soldier",       [CardSuit.wyrms, CardSuit.knots],  [CardIdentity.personality]),
			Card(CardType.number5, "Discovery",     [CardSuit.suns, CardSuit.waves],   [CardIdentity.event]),

			Card(CardType.number6, "Market",        [CardSuit.leaves, CardSuit.knots], [CardIdentity.location, CardIdentity.event]),
			Card(CardType.number6, "Lunatic",       [CardSuit.moons, CardSuit.waves],  [CardIdentity.personality]),
			Card(CardType.number6, "Penitent",      [CardSuit.suns, CardSuit.wyrms],   [CardIdentity.personality]),

			Card(CardType.number7, "Castle",        [CardSuit.suns, CardSuit.knots],   [CardIdentity.location]),
			Card(CardType.number7, "Cave",          [CardSuit.waves, CardSuit.wyrms],  [CardIdentity.location]),
			Card(CardType.number7, "Chance Meeting",[CardSuit.moons, CardSuit.leaves], [CardIdentity.event]),

			Card(CardType.number8, "Mill",          [CardSuit.waves, CardSuit.leaves], [CardIdentity.location]),
			Card(CardType.number8, "Diplomat",      [CardSuit.moons, CardSuit.suns],   [CardIdentity.personality]),
			Card(CardType.number8, "Betrayal",      [CardSuit.wyrms, CardSuit.knots],  [CardIdentity.event]),

			Card(CardType.number9, "Darkness",      [CardSuit.waves, CardSuit.wyrms],  [CardIdentity.location]),
			Card(CardType.number9, "Merchant",      [CardSuit.leaves, CardSuit.knots], [CardIdentity.personality]),
			Card(CardType.number9, "Pact",          [CardSuit.moons, CardSuit.suns],   [CardIdentity.event]),

			Card(CardType.pawns,   "Borderland",    [CardSuit.waves, CardSuit.leaves, CardSuit.wyrms], [CardIdentity.location]),
			Card(CardType.pawns,   "Watchman",      [CardSuit.moons, CardSuit.wyrms, CardSuit.knots],  [CardIdentity.personality]),
			Card(CardType.pawns,   "Light Keeper",  [CardSuit.suns, CardSuit.waves, CardSuit.knots],   [CardIdentity.personality]),
			Card(CardType.pawns,   "Harvest",       [CardSuit.moons, CardSuit.suns, CardSuit.leaves],  [CardIdentity.event]),

			Card(CardType.courts,  "Island",        [CardSuit.suns, CardSuit.waves, CardSuit.wyrms],   [CardIdentity.location]),
			Card(CardType.courts,  "Window",        [CardSuit.suns, CardSuit.leaves, CardSuit.knots],  [CardIdentity.location]),
			Card(CardType.courts,  "Consul",        [CardSuit.moons, CardSuit.waves, CardSuit.knots],  [CardIdentity.personality]),
			Card(CardType.courts,  "Rite",          [CardSuit.moons, CardSuit.leaves, CardSuit.wyrms], [CardIdentity.event]),

			Card(CardType.crowns,  "Sea",           [CardSuit.waves],  [CardIdentity.location]),
			Card(CardType.crowns,  "End",           [CardSuit.leaves], [CardIdentity.location, CardIdentity.event]),
			Card(CardType.crowns,  "Bard",          [CardSuit.suns],    [CardIdentity.personality]),
			Card(CardType.crowns,  "Huntress",      [CardSuit.moons],  [CardIdentity.personality]),
			Card(CardType.crowns,  "Calamity",      [CardSuit.wyrms],  [CardIdentity.event]),
			Card(CardType.crowns,  "Windfall",      [CardSuit.knots],  [CardIdentity.event]),
		])
		return deck

	@classmethod
	def make_standard(cls):
		deck = cls.make_extended()
		deck = Deck([x for x in deck.cards if not Card.is_extended(x)])
		return deck

	def take_card(self):
		if len(self.cards) > 0:
			return self.cards.pop(0)
		return None

	def check_assets(self):
		for card in self.cards:
			fname = f"decktet/assets/{card.id}.png"
			if not os.path.isfile(fname):
				print(f"check_assets: {fname} is missing ({card.name})")
