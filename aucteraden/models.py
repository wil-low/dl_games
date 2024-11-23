import tensorflow as tf
from keras.models import Model
from keras.layers import Dense, Input, Dropout


class MultiOutputChanneledModel(Model):
	def __init__(self):
		# Define input
		input_layer = Input(shape=(6 * 4 * 5,))

		# Common hidden layers
		hidden1 = Dense(256, activation='relu')(input_layer)
		dropout1 = Dropout(0.5)(hidden1)
		hidden2 = Dense(128, activation='relu')(dropout1)
		dropout2 = Dropout(0.5)(hidden2)
		hidden3 = Dense(128, activation='relu')(dropout2)
		dropout3 = Dropout(0.5)(hidden3)

		# Outputs
		churn_output = Dense(1, activation="sigmoid", name="churn")(dropout3)
		buy_output   = Dense(3, activation="softmax", name="buy")(dropout3)
		chip_output  = Dense(6, activation="softmax", name="chip")(dropout3)
		place_output = Dense(16, activation="softmax", name="place")(dropout3)

		# Combine into a single model
		super().__init__(inputs=input_layer, outputs=[churn_output, buy_output, chip_output, place_output])

		# Compile the model with separate loss functions for each output
		self.compile(
			optimizer="adam",
			loss={
				"churn": "binary_crossentropy",
				"buy": "binary_crossentropy",
				"chip": "binary_crossentropy",
				"place": "binary_crossentropy",
			},
			loss_weights={
				"churn": 1.0,
				"buy": 1.0,
				"chip": 1.0,
				"place": 1.0,
			},
			metrics={
				"churn": "accuracy",
				"buy": "accuracy",
				"chip": "accuracy",
				"place": "accuracy",
			}
		)

	def prepare_data(self, X_train, Y_train, X_test, Y_test):
		Y_train_split = tf.split(Y_train, [1, 3, 6, 16], axis=1)
		Y_test_split = tf.split(Y_test, [1, 3, 6, 16], axis=1)
		return (X_train, Y_train_split, X_test, Y_test_split)		


class MultiOutputModel(Model):
	def __init__(self):
		# Define input
		input_layer = Input(shape=(6 * 4 * 5,))

		# Common hidden layers
		hidden1 = Dense(256, activation='relu')(input_layer)
		hidden2 = Dense(128, activation='relu')(hidden1)

		# Outputs
		churn_output = Dense(1, activation="sigmoid", name="churn_output")(hidden2)
		buy_output   = Dense(3, activation="softmax", name="buy_output")(hidden2)
		chip_output  = Dense(6, activation="softmax", name="chip_output")(hidden2)
		place_output = Dense(16, activation="softmax", name="place_output")(hidden2)

		# Combine into a single model
		super().__init__(inputs=input_layer, outputs=[churn_output, buy_output, chip_output, place_output])

		# Compile the model with separate loss functions for each output
		self.compile(
			optimizer="adam",
			loss={
				"churn_output": "binary_crossentropy",
				"buy_output": "binary_crossentropy",
				"chip_output": "binary_crossentropy",
				"place_output": "binary_crossentropy",
			},
			loss_weights={
				"churn_output": 1.0,
				"buy_output": 1.0,
				"chip_output": 1.0,
				"place_output": 1.0,
			},
			metrics={
				"churn_output": "accuracy",
				"buy_output": "accuracy",
				"chip_output": "accuracy",
				"place_output": "accuracy",
			}
		)

	def prepare_data(self, X_train, Y_train, X_test, Y_test):
		Y_train_split = tf.split(Y_train, [1, 3, 6, 16], axis=1)
		Y_test_split = tf.split(Y_test, [1, 3, 6, 16], axis=1)
		return (X_train, Y_train_split, X_test, Y_test_split)		


class OneLayerModel(Model):
	def __init__(self):
		# Define input
		input_layer = Input(shape=(6 * 4 * 5,))

		# Common hidden layers
		hidden1 = Dense(256, activation='relu')(input_layer)
		dropout1 = Dropout(0.3)(hidden1)
		hidden2 = Dense(128, activation='relu')(dropout1)
		dropout2 = Dropout(0.3)(hidden2)

		# Outputs
		output = Dense(1 + 3 + 6 + 16, activation="sigmoid")(dropout2)

		# Combine into a single model
		super().__init__(inputs=input_layer, outputs=output)

		# Compile the model with separate loss functions for each output
		self.compile(
			optimizer="adam",
			loss= "mse",
			metrics=["accuracy"]
		)

	def prepare_data(self, X_train, Y_train, X_test, Y_test):
		return (X_train, Y_train, X_test, Y_test)
