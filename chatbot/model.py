# things we need for NLP
import nltk
from nltk.stem.lancaster import LancasterStemmer
from chatbot.utils import lemmatize_words

# things we need for Tensorflow
import numpy as np
import tflearn
import tensorflow as tf
import random

import json
import pickle

from chatbot.stop_words import ENGLISH_STOP_WORD


def create_chatbot_data():

    with open('intents.json') as json_data:
        intents = json.load(json_data)

    words = []
    classes = []
    documents = []

    for intent in intents['intents']:
        for pattern in intent['patterns']:
            w = nltk.word_tokenize(pattern)
            words.extend(w)
            documents.append((w, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    words = lemmatize_words([w.lower() for w in words])
    words = sorted(list(set(words)))

    classes = sorted(list(set(classes)))

    print(len(documents), 'documents')
    print(len(classes), 'classes', classes)
    print(len(words), 'unique lemmatized words', words)

    training = []
    # output = []
    output_empty = [0] * len(classes)

    for doc in documents:
        bag = []
        pattern_words = doc[0]
        pattern_words = lemmatize_words([w.lower() for w in pattern_words])
        for w in words:
            bag.append(1) if w in pattern_words else bag.append(0)

        output_row = list(output_empty)
        output_row[classes.index(doc[1])] = 1

        training.append([bag, output_row])

    random.shuffle(training)
    training = np.array(training)

    train_x = list(training[:, 0])
    train_y = list(training[:, 1])

    tf.reset_default_graph()
    net = tflearn.input_data(shape=[None, len(train_x[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
    net = tflearn.regression(net)

    model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')
    model.fit(train_x, train_y, n_epoch=1000, batch_size=8, show_metric=True)
    model.save('model.tflearn')

    pickle.dump({'words': words, 'classes': classes, 'train_x': train_x, 'train_y': train_y}, open("training_data", "wb"))


def main():
    create_chatbot_data()
    pass


if __name__ == "__main__":
    main()
