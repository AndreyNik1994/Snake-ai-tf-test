import keras
import tensorflow as tf
from config import Config

class SnakeModel:
    """Creating untrained model for Snake_AI"""
    def __init__(self, input_size, hidden_sizes, output_size: int = 4):
        self.model = self._build_model(input_size, hidden_sizes, output_size=output_size)
        self.optimizer = keras.optimizers.Adam(learning_rate=Config.LEARNING_RATE)
        # self.loss_fn = keras.losses.MeanSquaredError()
        self.loss_fn = keras.losses.Huber()

    def _build_model(self, input_size, hidden_sizes, output_size):
        """Construct sequential model with given architecture"""
        model = keras.Sequential()
        model.add(keras.layers.InputLayer(input_shape=(input_size,)))

        for units in hidden_sizes:
            model.add(keras.layers.Dense(units, activation='relu'))
            model.add(keras.layers.BatchNormalization())
            model.add(keras.layers.Dropout(0.3))

        model.add(keras.layers.Dense(output_size, activation='linear'))
        return model

    def predict(self, state):
        return self.model.predict(state, verbose=0)

    def train_step(self, data):
        states, targets = data
        with tf.GradientTape() as tape:
            predictions = self.model(states, training=True)
            loss = self.loss_fn(targets, predictions)
        gradients = tape.gradient(loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
        return loss.numpy()
