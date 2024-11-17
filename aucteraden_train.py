import argparse
import os
import random
import tensorflow as tf
import numpy as np
from keras.models import Model
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

	checkpoint_path = "aucteraden/training_1/cp.weights.h5"
	checkpoint_dir = os.path.dirname(checkpoint_path)
	# Create a callback that saves the model's weights
	cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path, save_weights_only=True, verbose=1)

	# Set the random seed for reproducibility
	seed_value = 42
	# Python random seed
	random.seed(seed_value)
	# NumPy random seed
	np.random.seed(seed_value)
	# TensorFlow random seed
	tf.random.set_seed(seed_value)
	# Optional: Set the environment variable to ensure deterministic operations
	os.environ['PYTHONHASHSEED'] = str(seed_value)

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
			"buy_output": "binary_crossentropy",
			"chip_output": "binary_crossentropy",
			"col_output": "binary_crossentropy",
			"row_output": "binary_crossentropy",
		},
		loss_weights={
			"churn_output": 1.0,
			"buy_output": 1.0,
			"chip_output": 1.0,
			"col_output": 1.0,
			"row_output": 1.0,
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
	#model.load_weights(checkpoint_path)

	Y_train_split = tf.split(Y_train, [1, 3, 6, 4, 4], axis=1)
	Y_test_split = tf.split(Y_test, [1, 3, 6, 4, 4], axis=1)

	model.fit(X_train, Y_train_split, batch_size=32, epochs=32, verbose=1, validation_data=(X_test, Y_test_split), callbacks=[cp_callback])

	metrics = model.evaluate(X_test, Y_test_split, verbose=0)

	# Define your metric names (as per your model)
	metric_names = model.metrics_names

	# Pretty print the results
	print(f"\nModel Evaluation Results:")
	for name, metric in zip(metric_names, metrics):
		print(f"{name}: {metric:.4f}")

	col = 993
	row = 10
	board = feature_encoder.decode(X_load[col][row])
	move = label_encoder.decode(Y_load[col][row])
	print(f"\n==== Board for Game {col}, turn {row}: ====\n{board}")
	print(f"Move: {move}\n")

	predict_board = X_load[col][row].reshape(1, 6 * 4 * 5)
	#print(predict_board)
	move_probs = model.predict(predict_board)
	print("move_probs: ", move_probs)

	# Step 1: Flatten each tensor in the list
	flattened_tensors = [tf.reshape(t, [-1]) for t in move_probs]
	# Step 2: Concatenate all flattened tensors into a single tensor
	result = tf.concat(flattened_tensors, axis=0)

	print(f"\n==== Move prediction for Game {col}, turn {row}: ====")
	print(label_encoder.decode_predict(result))

if __name__ == "__main__":
	main()
