from fuzzywuzzy import process, fuzz
from models.spacy_model import load_spacy
from utils.string_cleaners import remove_apostrophe, remove_commas, remove_foward_slash, remove_question_mark, \
                                  remove_quotations, normalize_whitespace, dash_to_single_space
class FuzzyMatcher():

    def __init__(self):
        self.nlp = load_spacy('en')

    def find(self, query, search_list):

        final_matches = []
        query_doc = self.nlp(query)

        for token in query_doc:
            match = process.extractOne(token.text, search_list, scorer=fuzz.ratio)
            if match[1] > 85:
                final_matches.append(match)

        final_matches = sorted(final_matches, key=lambda tup: tup[1])
        final_matches = [x[0] for x in final_matches]
        return final_matches
