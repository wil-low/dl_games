import argparse
import glob
import os
import random
from aucteraden.models import *
import tensorflow as tf
import numpy as np
from aucteraden.agent import OneMoveScoreBot, RandomBot
from aucteraden.board import GameState
from aucteraden.encoders import GameStateEncoder, MoveEncoder

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--seed", "-s", type=int, default=None)
	parser.add_argument("--num-games", "-n", type=int, default=None)
	parser.add_argument("--verbose", "-v", action="store_true", help="Print every move")
	parser.add_argument("--single", "-1", action="store_true", help="Generate one game per seed (inc_seed)")
	parser.add_argument("--load-weights", "-L", action="store_true", help="Load weights into model")
	parser.add_argument("--fit", "-F", action="store_true", help="Perform model fitting")
	parser.add_argument("--predict", "-p", type=int, help="Perdict move #")
	args = parser.parse_args()

	feature_encoder = GameStateEncoder()
	label_encoder = MoveEncoder()

	features_fn = []
	labels_fn   = []

	if args.seed is None and args.num_games is None:
		base_fn = f"aucteraden/generated_games/"
		if args.single:
			base_fn += "inc_seed"
		else:
			base_fn += "fix_seed"
		files = glob.glob(f"{base_fn}/*F.npy")
		for f in files:
			features_fn.append(f);
			f = f.replace("F.", "L.")
			labels_fn.append(f)
	else:
		base_fn = "%05d_%05d" % (args.seed, args.num_games)
		if args.single:
			base_fn = f"inc_seed/{base_fn}"
		else:
			base_fn = f"fix_seed/{base_fn}"
		base_fn = f"aucteraden/generated_games2/{base_fn}"

		features_fn.append(f"{base_fn}F.npy")
		labels_fn.append(f"{base_fn}L.npy")

	checkpoint_path = "aucteraden/training_1/cp.weights.h5"
	checkpoint_dir = os.path.dirname(checkpoint_path)
	# Create a callback that saves the model's weights
	cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path, save_weights_only=True, verbose=1)
	es_callback = tf.keras.callbacks.EarlyStopping(patience=2, restore_best_weights=True)

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

	X_load = []
	Y_load = []

	for i in range(len(features_fn)):
		x = np.load(features_fn[i])
		y = np.load(labels_fn[i])
		if x.shape[0] != y.shape[0]:
			print(f"{x.shape[0]} != {y.shape[0]} in {features_fn[i]}")
		else:
			X_load.append(x)
			Y_load.append(y)

	X = np.concatenate(X_load)
	print(X.shape)
	Y = np.concatenate(Y_load)
	print(Y.shape)
	assert(X.shape[0] == Y.shape[0])
	samples = X.shape[0]

	X = X.reshape(samples, 6 * 4 * 5)

	train_samples = int(0.9 * samples)
	X_train, X_test = X[:train_samples], X[train_samples:]
	Y_train, Y_test = Y[:train_samples], Y[train_samples:]

	print(f"Samples: {samples} from {len(features_fn)} files; test samples start from {len(X_train) + 1}")

	model = OneLayerModel()  # MultiOutputModel()
	model.summary()

	if args.load_weights:
		print(f"Load weights from {checkpoint_path}")
		model.load_weights(checkpoint_path)

	X_train_prep, Y_train_prep, X_test_prep, Y_test_prep = model.prepare_data(X_train, Y_train, X_test, Y_test)

	if args.fit:
		print(f"Start fitting")
		model.fit(X_train_prep, Y_train_prep, batch_size=256, epochs=5, verbose=1, validation_data=(X_test_prep, Y_test_prep),
			callbacks=[cp_callback, es_callback])

	metrics = model.evaluate(X_test, Y_test_prep, verbose=0)

	# Define your metric names (as per your model)
	metric_names = model.metrics_names

	# Pretty print the results
	print(f"\nModel Evaluation Results:")
	for name, metric in zip(metric_names, metrics):
		print(f"{name}: {metric:.4f}")

	if args.predict is not None:
		turn = args.predict
		board = feature_encoder.decode(X[turn].reshape(6, 4, 5))
		move = label_encoder.decode(Y[turn])
		print(f"\n==== Board for turn {turn}: ====\n{board}")
		print(f"Move: {move}\n")

		predict_board = X[turn].reshape(1, 120)
		#print(predict_board.shape)
		#print(predict_board)

		move_probs = model.predict(predict_board)
		#print("move_probs: ", move_probs)

		# Step 1: Flatten each tensor in the list
		flattened_tensors = [tf.reshape(t, [-1]) for t in move_probs]
		# Step 2: Concatenate all flattened tensors into a single tensor
		result = tf.concat(flattened_tensors, axis=0)

		print(f"\n==== Move prediction for turn {turn}: ====")
		print(label_encoder.decode_predict(result))

if __name__ == "__main__":
	main()
