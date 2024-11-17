import argparse
import numpy as np
from aucteraden.board import Board, GameState
from aucteraden.encoders import GameStateEncoder, MoveEncoder
from decktet.card import CardSuit

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

	base_fn = "%05d_%05d" % (args.seed, args.num_games)
	if args.single:
		base_fn = f"inc_seed/{base_fn}"
	else:
		base_fn = f"fix_seed/{base_fn}"
	base_fn = f"aucteraden/generated_games/{base_fn}"

	features_fn = f"{base_fn}F.npy"
	labels_fn   = f"{base_fn}L.npy"

	#features_fn = f"feat.npy"
	#labels_fn   = f"labe.npy"

	X = np.load(features_fn)
	Y = np.load(labels_fn)
	samples = X.shape[0]

	feature_list = []
	label_list = []
	invalid_X = 0
	invalid_Y = 0

	"""
	for game in range(samples):
		board = feature_encoder.decode(X[game])
		move = label_encoder.decode(Y[game], grid16=True)
		print(f"==== Board for Game {game}: ====\n{board}")
		print(f"Move: {move}\n")
	return
	"""
	for game in range(samples):
		for turn in range(MAX_GAME_DURATION):
			board = feature_encoder.decode(X[game][turn])
			move = label_encoder.decode(Y[game][turn])
			print(f"==== Board for Game {game}, turn {turn}: ====\n{board}")
			print(f"Move: {move}\n")
			chip_count = 0
			for suit in CardSuit:
				chip_count += board.chips[suit]
			if chip_count == 0:
				invalid_X += 1
			else:
				feature_list.append(X[game][turn])
			if not move.churn_market and move.buy_card_index is None:
				invalid_Y += 1
			else:
				ary = Y[game][turn]
				#print(ary)
				split = np.split(ary, [1 + 3 + 6, 14], axis=0)
				#print(split)
				col = np.argmax(split[1], axis=-1)
				row = np.argmax(split[2], axis=-1)
				grid_pos = np.zeros(Board.col_count * Board.row_count, dtype=np.int8)
				grid_pos[col + row * Board.col_count] = 1
				#print(pos_ary)
				label_list.append(np.concatenate([split[0], grid_pos], axis=0))
	
	print(f"Total: {samples * MAX_GAME_DURATION}, invalid ({invalid_X}, {invalid_Y})")

	features = np.stack(feature_list, axis=0)
	print(features.shape)
	
	labels = np.stack(label_list, axis=0) #.reshape(len(label_list), 1 + 3 + 6 + 16)
	print(labels.shape)

	features_fn = features_fn.replace("_games", "_games2")
	labels_fn = labels_fn.replace("_games", "_games2")

	np.save(features_fn, features)
	np.save(labels_fn, labels)
	return

	train_samples = int(0.9 * samples)
	X_train, X_test = X[:train_samples], X[train_samples:]
	Y_train, Y_test = Y[:train_samples], Y[train_samples:]

	# Define input
	input_layer = Input(shape=(6 * 4 * 5,))

	# Common hidden layers
	hidden1 = Dense(256, activation='relu')(input_layer)
	hidden2 = Dense(64, activation='relu')(hidden1)

	# Outputs
	churn_output = Dense(1, activation="sigmoid", name="churn_output")(hidden2)
	buy_output   = Dense(3, activation="softmax", name="buy_output")(hidden2)
	chip_output  = Dense(6, activation="sigmoid", name="chip_output")(hidden2)
	col_output   = Dense(4, activation="softmax", name="col_output")(hidden2)
	row_output   = Dense(4, activation="softmax", name="row_output")(hidden2)

	# Combine into a single model
	model = Model(inputs=input_layer, outputs=[churn_output, buy_output, chip_output, col_output, row_output])

	# Compile the model with separate loss functions for each output
	model.compile(
		optimizer="adam",
		loss={
			"churn_output": "binary_crossentropy",
			"buy_output": "categorical_crossentropy",
			"chip_output": "binary_crossentropy",
			"col_output": "categorical_crossentropy",
			"row_output": "categorical_crossentropy",
		},
		metrics={
			"churn_output": "accuracy",
			"buy_output": "accuracy",
			"chip_output": "accuracy",
			"col_output": "accuracy",
			"row_output": "accuracy",
		}
	)
	model.summary()

	Y_train_split = tf.split(Y_train, [1, 3, 6, 4, 4], axis=1)
	Y_test_split = tf.split(Y_test, [1, 3, 6, 4, 4], axis=1)

	model.fit(X_train, Y_train_split, batch_size=32, epochs=50, verbose=1, validation_data=(X_test, Y_test_split))

	score = model.evaluate(X_test, Y_test_split, verbose=0)
	print("Test metrics:", score)

	col = 5
	row = 9
	board = feature_encoder.decode(X_load[col][row])
	move = label_encoder.decode(Y_load[col][row])
	print(f"==== Board for Game {col}, turn {row}: ====\n{board}")
	print(f"Move: {move}\n")

	predict_board = X_load[col][row].reshape(1, 6 * 4 * 5)
	print(predict_board)
	move_probs = model.predict(predict_board)

	# Step 1: Flatten each tensor in the list
	flattened_tensors = [tf.reshape(t, [-1]) for t in move_probs]
	# Step 2: Concatenate all flattened tensors into a single tensor
	result = tf.concat(flattened_tensors, axis=0)

	print(f"\n==== Move prediction for Game {col}, turn {row}: ====")
	print(label_encoder.decode_predict(result))

if __name__ == "__main__":
	main()
