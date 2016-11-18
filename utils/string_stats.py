"""
Created on November 16, 2016

@author: Carl Mueller
"""
import settings
from nltk import word_tokenize, FreqDist
from database.database import ExpressionsDatabaseEngine, IntentsDatabaseEngine, StopwordDatabaseEngine
from utils.string_cleaners import remove_foward_slash, remove_apostrophe, remove_commas, remove_question_mark, normalize_whitespace

class IntentStopwordGenerator:
    def __init__(self):
        self.exp_db = ExpressionsDatabaseEngine()
        self.int_db = IntentsDatabaseEngine()

    def __del__(self):
        self.exp_db.release_database_connection()
        self.int_db.release_database_connection()

    def add_stopwords_to_intent_in_database(self):
        intent_stopwords = self.get_intent_stopwords_dict()
        for intent, stopwords in intent_stopwords.items():
            self.int_db.add_stopwords_to_intent(intent, stopwords)

    def get_intent_stopwords_dict(self, n=20):
        intents = self.int_db.get_intents()
        intent_stopwords = {}
        for intent in intents:
            stopwords = self.get_stopwords_for_intent(intent)
            intent_stopwords[intent] = stopwords
        return intent_stopwords

    def get_stopwords_for_intent(self, intent, n=20):
        freq_stats = self.get_frequency_statistics(intent)
        most_common_tokens = freq_stats.most_common(n)
        stopwords = [x[0] for x in most_common_tokens]
        return stopwords

    def get_frequency_statistics(self, intent):
        text = self.get_expressions_as_text(intent)
        tokens = word_tokenize(text)
        cleaned_tokens = self.clean_tokens(tokens)
        frequency_distribution = FreqDist(cleaned_tokens)
        return frequency_distribution

    def get_expressions_as_text(self, intent):
        list_of_expressions = self.exp_db.get_intent_expressions(intent)
        text = ''
        for expression in list_of_expressions:
            expression += ' '
            text += expression
        return text

    def clean_tokens(self, tokens):
        cleaned_tokens = []
        for token in tokens:
            token = remove_foward_slash(token)
            token = remove_question_mark(token)
            token = remove_commas(token)
            token = remove_apostrophe(token)
            token = normalize_whitespace(token)
            token = token.lower()
            cleaned_tokens.append(token)
        token_list = [tok for tok in cleaned_tokens if tok is not '']
        return token_list

generator = IntentStopwordGenerator()


stopwords_dict = generator.get_intent_stopwords_dict()

for key, value in stopwords_dict.items():
    print(key)
    print(value)

generator.add_stopwords_to_intent_in_database()