from mongoengine import DictField, StringField, Document, IntField
import matplotlib.pyplot as plt
import numpy as np
from keras.models import load_model


class NetworkModel(Document):
    track_length = IntField(required=True)
    history = DictField(required=False)
    model_params = DictField(required=False)
    model_file = StringField(required=False)
    keras_model = None

    meta = {'allow_inheritance': True}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if self.id is None:
            self.save()
        self.model_file = ''.join(['models/', str(self.id), '.h5'])

    def train_network(self, batch_size, track_time):
        pass

    def evaluate_track_input(self, track):
        pass

    def convert_history_to_db_format(self, history_training):
        for k, v in history_training.history.items():
            for i in range(len(history_training.history[k])):
                history_training.history[k][i] = float(history_training.history[k][i])
        self.history = history_training.history

    def load_model_from_file(self):
        try:
            self.keras_model = load_model(self.model_file, compile=True)
        except ValueError:
            print("File does not exist!")

    def plot_loss_model(self, train=True, val=True):
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Model Loss')
        if train:
            plt.plot(np.arange(1, len(self.history['loss']) + 1, 1), self.history['loss'], label="Train loss")
        if val:
            plt.plot(np.arange(1, len(self.history['val_loss']) + 1, 1), self.history['val_loss'], label="Val loss")
        plt.legend()
        plt.show()

    def plot_mse_model(self, train=True, val=True):
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Model MSE')
        if train:
            plt.plot(np.arange(1, len(self.history['mse']) + 1, 1), self.history['mse'], label="Train mse")
        if val:
            plt.plot(np.arange(1, len(self.history['val_mse']) + 1, 1), self.history['val_mse'], label="Val mse")
        plt.legend()
        plt.show()

    def plot_accuracy_model(self, train=True, val=True, categorical=False):
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Model Accuracy')
        if categorical:
            if train:
                plt.plot(np.arange(1, len(self.history['categorical_accuracy']) + 1, 1),
                         self.history['categorical_accuracy'], label="Train categorical accuracy")
            if val:
                plt.plot(np.arange(1, len(self.history['val_categorical_accuracy']) + 1, 1),
                         self.history['val_categorical_accuracy'], label="Val categorical accuracy")
        else:
            if train:
                plt.plot(np.arange(1, len(self.history['acc']) + 1, 1), self.history['acc'],
                         label="Train accuracy")
            if val:
                plt.plot(np.arange(1, len(self.history['val_acc']) + 1, 1), self.history['val_acc'],
                         label="Val accuracy")

        plt.legend()
        plt.show()
