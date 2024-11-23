import os
from typing import Optional

import numpy as np

from aucteraden.board import Board, GameState
from aucteraden.encoders import GameStateEncoder, MoveEncoder
from decktet.card import Card, CardSuit
import gymnasium as gym
from gymnasium import spaces
from gymnasium.error import DependencyNotInstalled


class AucteradenEnv(gym.Env):

	metadata = {
		"render_modes": ["human", "rgb_array"],
		"render_fps": 1,
	}

	def __init__(self, render_mode: Optional[str] = None):
		self.game_state_encoder = GameStateEncoder()
		self.move_encoder = MoveEncoder()

		arr = np.ones([10 + 16], dtype=np.int8) * 2
		self.action_space = spaces.MultiDiscrete(arr)
		
		arr = np.ones([6, 4, 5], dtype=np.int8) * 13
		self.observation_space = spaces.MultiDiscrete(arr)

		self.render_mode = render_mode
		self.card_image_cache = {}
		self.suit_image_cache = {}

	def step(self, action):
		print("step")
		#assert self.action_space.contains(action)
		terminated = False
		reward = 0.0
		bot_move = self.move_encoder.decode(action)
		self.game = self.game.apply_move(bot_move)
		self.game.board.refill_market(True)
		if self.game.is_over():
			terminated = True

		if self.render_mode == "human":
			self.render()
		# truncation=False as the time limit is handled by the `TimeLimit` wrapper added during `make`
		result = (self._get_obs(), reward, terminated, False, {})
		#print(f"step: {result}")
		return result

	def _get_obs(self):
		return self.game_state_encoder.encode(self.game.board)

	def reset(
		self,
		seed: Optional[int] = None,
		options: Optional[dict] = None,
	):
		super().reset(seed=seed)

		print("reset")

		self.game = GameState.new_game()

		if self.render_mode == "human":
			self.render()
		result = (self._get_obs(), {})
		#print(f"reset: {result}")
		return result

	def render(self):
		if self.render_mode is None:
			assert self.spec is not None
			gym.logger.warn(
				"You are calling render method without specifying any render mode. "
				"You can specify the render_mode at initialization, "
				f'e.g. gym.make("{self.spec.id}", render_mode="rgb_array")'
			)
			return

		try:
			import pygame
		except ImportError as e:
			raise DependencyNotInstalled(
				'pygame is not installed, run `pip install "gymnasium[toy-text]"`'
			) from e

		card_img_width = int(224 * 0.7) + 2
		card_img_height = int(314 * 0.7) + 2
		suit_img_width = 47
		suit_img_height = 47
		spacing = 10

		screen_width, screen_height = 1300, (card_img_height + spacing) * 4 + spacing

		market_x, market_y = spacing, spacing * 5
		grid_x, grid_y = screen_width - (card_img_width + spacing) * 4, spacing

		bg_color = (7, 99, 36)
		white = (255, 255, 255)
		suit_color = {
			CardSuit.moons: (153, 153, 153),
			CardSuit.suns:  (255, 102, 0),
			CardSuit.waves: (0, 102, 255),
			CardSuit.leaves:(200, 113, 55),
			CardSuit.wyrms: (0, 170, 0),
			CardSuit.knots: (255, 204, 0)
		}
		line_width = 4

		if not hasattr(self, "screen"):
			pygame.init()
			if self.render_mode == "human":
				pygame.display.init()
				pygame.display.set_caption("Aucteraden")
				self.screen = pygame.display.set_mode((screen_width, screen_height))
			else:
				pygame.font.init()
				self.screen = pygame.Surface((screen_width, screen_height))

		if not hasattr(self, "clock"):
			self.clock = pygame.time.Clock()

		self.screen.fill(bg_color)

		title_font = pygame.font.Font(pygame.font.get_default_font(), 45)

		font = pygame.font.Font(pygame.font.get_default_font(), 25)

		def draw_text(s, font, x, y):
			text = font.render(s, 1, white)
			rect = text.get_rect()
			rect.topleft = (x, y)
			self.screen.blit(text, rect)

		def show_suit_chip(suit, count, x, y):
			img = None
			if suit in self.suit_image_cache:
				img = self.suit_image_cache[suit]
			else:
				img = pygame.image.load(f"decktet/assets/{Card.suit_map[suit]}.png")
				#img = pygame.transform.scale(img, (card_img_width, card_img_height))
				self.suit_image_cache[suit] = img
			self.screen.blit(img, (x, y))
			draw_text(f"{count}", font, x + suit_img_width + spacing, y + suit_img_height // 4)

		def show_card(card_id, x, y):
			img = None
			if card_id in self.card_image_cache:
				img = self.card_image_cache[card_id]
			else:
				img = pygame.image.load(f"decktet/assets/{card_id}.png")
				img = pygame.transform.scale(img, (card_img_width, card_img_height))
				self.card_image_cache[card_id] = img
			return self.screen.blit(img, (x, y))
		
		def draw_chains(longest_chains):
			for suit, items in longest_chains.items():
				cards, _ = items
				if len(cards) > 1:
					offset = (suit.value - 3) * line_width
					lines = [(grid_x + card_img_width // 2 + offset + (card_img_width + spacing) * col,
							grid_y + card_img_height // 2 + offset + (card_img_height + spacing) * row)
							for _, col, row in cards]
					pygame.draw.lines(self.screen, suit_color[suit], False, lines, line_width)

		# Cards in deck
		draw_text(f"Deck: {len(self.game.board.deck.cards)}", font, spacing * 2, spacing)

		# Score
		score, longest_chains = self.game.board.calculate_score()
		draw_text(f"Score: {score}", font, spacing * 2 + (spacing + card_img_width) * 2, spacing)

		# Chain lines
		draw_chains(longest_chains)

		# Market
		for i in range(3):
			draw_text(f"Cost: {2 - i}", font, market_x + (card_img_width + spacing) * i + spacing, market_y + spacing)
		for i in range(len(self.game.board.market)):
			card = self.game.board.market[i]
			show_card(card.id, market_x + (card_img_width + spacing) * i, market_y + spacing * 5)

		# Suit chips
		for suit in CardSuit:
			count = self.game.board.chips[suit]
			show_suit_chip(suit, count, spacing + suit_img_width * 2 * suit.value, market_y + card_img_height + spacing * 8)

		# Grid
		for row in range(Board.row_count):
			for col in range(Board.col_count):
				card = self.game.board.get_card(col, row)
				img_id = "empty"
				if card:
					img_id = card.id
				show_card(img_id, grid_x + (card_img_width + spacing) * col, grid_y + (card_img_height + spacing) * row)

		# Title
		draw_text(f"Aucteraden", title_font, spacing, screen_height - spacing * 5)

		if self.render_mode == "human":
			pygame.event.pump()
			pygame.display.update()
			self.clock.tick(self.metadata["render_fps"])
		else:
			return np.transpose(
				np.array(pygame.surfarray.pixels3d(self.screen)), axes=(1, 0, 2)
			)

	def close(self):
		if hasattr(self, "screen"):
			import pygame

			pygame.display.quit()
			pygame.quit()

