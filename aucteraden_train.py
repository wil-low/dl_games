import argparse
import random
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Input
from aucteraden.agent import OneMoveScoreBot, RandomBot
from aucteraden.board import GameState
from aucteraden.encoders import GameStateEncoder, MoveEncoder

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--seed", "-s", type=int, default=42)
	parser.add_argument("--num-games", "-n", type=int, default=1000)
	parser.add_argument("--verbose", "-v", action="store_true", help="Print every move")
	parser.add_argument("--single", "-1", action="store_true", help="Generate one game per seed, then increase seed")
	args = parser.parse_args()

	feature_encoder = GameStateEncoder()
	label_encoder = MoveEncoder()

	MAX_GAME_DURATION = 20

	best_score = -10000000
	best_game = 0
	sum_score = 0
	#bot = RandomBot()
	bot = OneMoveScoreBot(25, 4)

	feature_shape = np.insert(feature_encoder.shape(), 0, MAX_GAME_DURATION)
	feature_shape = np.insert(feature_shape, 0, args.num_games)
	features = np.zeros(feature_shape, dtype=np.int8)
	label_shape = np.insert(label_encoder.shape(), 0, MAX_GAME_DURATION)
	label_shape = np.insert(label_shape, 0, args.num_games)
	labels = np.zeros(label_shape, dtype=np.int8)

	base_fn = "%05d_%05d" % (args.seed, args.num_games)
	if args.single:
		base_fn = f"inc_seed/{base_fn}"
	else:
		base_fn = f"fix_seed/{base_fn}"
	base_fn = f"aucteraden/generated_games/{base_fn}"

	features_fn = f"{base_fn}F.npy"
	labels_fn   = f"{base_fn}L.npy"

	np.random.seed(args.seed)

	X_load = np.load(features_fn)
	Y_load = np.load(labels_fn)
	samples = X_load.shape[0]

	X = X_load.reshape(samples * 20, 6 * 4 * 5)
	Y = Y_load.reshape(samples * 20, 18)

	print(X[0])
	print(Y[0])

	train_samples = int(0.9 * samples)
	X_train, X_test = X[:train_samples], X[train_samples:]
	Y_train, Y_test = Y[:train_samples], Y[train_samples:]

	model = Sequential()
	model.add(Input(shape=(6 * 4 * 5,)))
	model.add(Dense(256, activation="relu"))
	model.add(Dense(64, activation="relu"))
	model.add(Dense(18, activation="sigmoid"))
	model.summary()

	model.compile(loss="mean_squared_error", optimizer="sgd", metrics=["accuracy"])

	model.fit(X_train, Y_train, batch_size=16, epochs=50, verbose=1, validation_data=(X_test, Y_test))

	score = model.evaluate(X_test, Y_test, verbose=0)
	print("Test loss:", score[0])
	print("Test accuracy:", score[1])

	col = 5
	row = 15
	for i in range(20):
		board = feature_encoder.decode(X_load[col][i])
		move = label_encoder.decode(Y_load[col][i])
		if not move.churn_market and move.buy_card_index is not None:
			print(f"==== Board for Game {col}, turn {i}: ====\n{board}")
			print(f"Move: {move}\n")

	predict_board = X_load[col][row].reshape(1, 6 * 4 * 5)
	print(predict_board)
	move_probs = model.predict(predict_board)
	print(f"move_probs.shape = {move_probs.shape}")
	print(move_probs[0])
	print(label_encoder.decode_predict(move_probs[0]))

if __name__ == "__main__":
	main()
