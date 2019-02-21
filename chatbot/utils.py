import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from chatbot.stop_words import ENGLISH_STOP_WORD

# Download the corpora and models
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('tagsets')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')


# Get wordnet part-of-speech tagger
def get_wordnet_pos(word_tag):
    if word_tag.startswith('N'):
        return wordnet.NOUN
    elif word_tag.startswith('J'):
        return wordnet.ADJ
    elif word_tag.startswith('V'):
        return wordnet.VERB
    elif word_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


# Convert pronoun
def convert_pronoun(word):
    person1st = ('me', 'my', 'mine', 'myself')
    person2nd = ('your', 'yours', 'yourself')
    person3rd_male = ('him', 'his', 'himself')
    person3rd_female = ('her', 'hers', 'herself')
    person3rd = ('its', 'itself')
    person1st_plural = ('us', 'our', 'ours', 'ourselves')
    person3rd_plural = ('them', 'their', 'theirs', 'themselves')

    if word in person1st:
        return 'i'
    if word in person2nd:
        return 'you'
    if word in person3rd_male:
        return 'he'
    if word in person3rd_female:
        return 'she'
    if word in person3rd:
        return 'it'
    if word in person1st_plural:
        return 'we'
    if word in person3rd_plural:
        return 'they'
    return word


# Split a sentence into array of words
def tokenize_text(text):
    tokens = nltk.word_tokenize(text)
    return lemmatize_words(tokens)


# Convert words to infinitive words
def lemmatize_words(words):
    tagged_tokens = nltk.pos_tag(words)
    # print(tagged_tokens)
    array = []
    lemma = WordNetLemmatizer()
    for token in tagged_tokens:
        temp = token[0].lower()
        if temp in ENGLISH_STOP_WORD:
            continue
        temp = convert_pronoun(temp)
        array.append(lemma.lemmatize(temp, pos=get_wordnet_pos(token[1])))
    # print(array)
    return array


def main():
    text = "Would you mind to answer me this question?"
    array = tokenize_text(text)
    print(array)
    print(name)


if __name__ == "__main__":
    main()
