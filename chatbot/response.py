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
from nltk.tag import StanfordNERTagger

ERROR_THRESHOLD = 0.25
CHATBOT_DIR = os.path.dirname(os.path.abspath(__file__))


class ChatBotResponse:

    def __init__(self):

        self.context = {}
        self.username = "Visitor"
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
        tokens = lemmatize_words(tokens)
        return tokens

    def get_entity_name(self, sentence):
        tokens = nltk.word_tokenize(sentence)
        st = StanfordNERTagger(CHATBOT_DIR + '/Standford_lib/english.all.3class.distsim.crf.ser.gz',
                               CHATBOT_DIR + '/Standford_lib/stanford-ner.jar')

        tagged_words_list = st.tag(tokens)
        for word, tag in tagged_words_list:
            if tag == 'PERSON':
                return word
        return ""

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
        print(return_list)
        return return_list

    @database_sync_to_async
    def response(self, sentence, user_id='1106'):
        results = self.classify(sentence)
        if results:
            while results:
                for i in self.intents['intents']:
                    if i['tag'] == results[0][0]:

                        if 'context_filter' not in i or \
                                (user_id in self.context and 'context_filter' in i and
                                 i['context_filter'] == self.context[user_id]):

                            if 'context_set' in i:
                                self.context[user_id] = i['context_set']

                            if 'function' in i:
                                if i['function'] == 'get_entity_name':
                                    self.username = self.get_entity_name(sentence)
                                    result = "%s|%s" % (random.choice(i['responses']) % self.username,
                                                        random.choice(i['follows']))
                                    return result

                            return random.choice(i['responses'])
                results.pop(0)

    @database_sync_to_async
    def get_username(self):
        return self.username

    @database_sync_to_async
    def welcome(self, username="", existed=False):
        if existed:
            welcome = "Glad to see you come back|What do you want to know this time?"
        elif "visitor" in username.lower():
            welcome = "Hi, there. How are you? My name is Cheri|I am an online assistant of Minh|" \
                      "What should I call you by?"
        else:
            welcome = "Nice to meet you, %s|What do you want to know about him?" % username

        return welcome


def main():
    # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # print(BASE_DIR)


    chatbot = ChatBotResponse()
    name = chatbot.clean_up_sentence("My linkedin is linkedin/harrison-Addex")
    print(name)
    # print("chatbot get username: " + chatbot.get_username())
    # response = chatbot.response("Nice to meet you")
    # print(response)
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
    pass


if __name__ == '__main__':
    main()
