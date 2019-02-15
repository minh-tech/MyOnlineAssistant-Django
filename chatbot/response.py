import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import tflearn
import random
import pickle
import json
import os
from chatbot.stop_words import ENGLISH_STOP_WORD
from channels.db import database_sync_to_async
from chatbot.utils import lemmatize_words

ERROR_THRESHOLD = 0.25
CHATBOT_DIR = os.path.dirname(os.path.abspath(__file__))


class ChatBotResponse:

    def __init__(self):

        self.context = {}
        # self.stemmer = LancasterStemmer()

        data = pickle.load(open(CHATBOT_DIR+"/training_data", "rb"))
        self.words = data['words']
        self.ignore_words = ENGLISH_STOP_WORD
        self.classes = data['classes']
        train_x = data['train_x']
        train_y = data['train_y']

        with open(CHATBOT_DIR+'/intents.json') as json_data:
            self.intents = json.load(json_data)

        net = tflearn.input_data(shape=[None, len(train_x[0])])
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
        net = tflearn.regression(net)
        logs = CHATBOT_DIR+'/tflearn_logs'
        self.model = tflearn.DNN(net, tensorboard_dir=logs)
        self.model.load(CHATBOT_DIR+'/model.tflearn')

    def clean_up_sentence(self, sentence):
        tokens = nltk.word_tokenize(sentence)
        # sentence_words = [self.stemmer.stem(word.lower()) for word in sentence_words if word not in self.ignore_words]
        tokens, _ = lemmatize_words(tokens)
        return tokens

    def get_named_entity(self, sentence):
        tokens = nltk.word_tokenize(sentence)
        _, proper_name = lemmatize_words(tokens)
        print(">>>>>>>>>> Proper name: " + proper_name)
        return proper_name

    def bow(self, sentence, show_details=False):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0]*len(self.words)
        for sentence_word in sentence_words:
            for i, word in enumerate(self.words):
                if word == sentence_word:
                    bag[i] = 1
                    if show_details:
                        print("found in bag: %s" % word)
                    break
        return np.array(bag)

    def classify(self, sentence):
        results = self.model.predict([self.bow(sentence)])[0]
        results = [[i, r] for i, r in enumerate(results) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append((self.classes[r[0]], r[1]))
        return return_list

    @database_sync_to_async
    def response(self, sentence, user_name='friend', show_details=False):
        results = self.classify(sentence)
        if results:
            while results:
                for i in self.intents['intents']:
                    if i['tag'] == results[0][0]:
                        if 'context_set' in i:
                            if show_details:
                                print('context:', i['context_set'])
                            self.context[user_name] = i['context_set']

                        if 'context_filter' not in i or \
                                (user_name in self.context and 'context_filter' in i and
                                 i['context_filter'] == self.context[user_name]):
                            if show_details:
                                print('tag:', i['tag'])
                            return random.choice(i['responses'])
                results.pop(0)

    @database_sync_to_async
    def welcome(self, username="", existed=False):
        if existed:
            welcome = "Glad to see you come back/What do you want to know this time?"
        elif "visitor" in username.lower():
            welcome = "Hi, there. How are you? My name is Cheri/I am an online assistant of Minh/" \
                      "What should I call you by?"
        else:
            welcome = "Nice to meet you, %s/What do you want to know about him?" % username

        return welcome


def main():
    # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # print(BASE_DIR)


    chatbot = ChatBotResponse()
    chatbot.get_named_entity("My name is Minh")

    # flag = True
    # print("Cheri: My name is Cheri. I will answer your queries about my moped rental shop.")
    #
    # while flag:
    #     user_response = input()
    #     user_response = user_response.lower()
    #     if user_response != 'bye':
    #         print("Cheri: ", end="")
    #         print(chatbot_response.response(user_response))
    #     else:
    #         flag = False
    #         print("Cheri: Bye! Take care...")


if __name__ == '__main__':
    main()
