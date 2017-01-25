from models.spacy_model import load_spacy
import re

PrimitiveNumbers = {
    'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90
}

Magnitudes = {
    'thousand': 1000,
    'million': 1000000,
    'billion': 1000000000
}


class NumberExtractor:
    """
    Class providing naive
    """
    def __init__(self):
        self.nlp = load_spacy('en')

    def parse(self, doc):
        parsed_doc = self.nlp(doc)
        cardinal_tokens = []
        for token in parsed_doc:
            if token.ent_type_ == 'CARDINAL' or token.ent_type_ == 'MONEY':
                cardinal_tokens.append(token)
        text = ''
        for token in cardinal_tokens:
            text += token.orth_ + ' '
            text.strip(' ')
        try:
            return int(text)
        except ValueError as e:
            return self.text2num(text)


    def text2num(self, text):
        if len(text) == 0:
            return None
        # Split text on spaces or hyphens
        split_text = re.split(r"[\s-]+", text)
        magnification = 0
        basic_amount = 0
        for token in split_text:
            # Iterate over tokens and accumulate basic_term amounts.
            basic_term = PrimitiveNumbers.get(token, None)
            if basic_term is not None:
                basic_amount += basic_term
            # If a basic term is followed by 100 multiply by 100
            elif token == "hundred" and basic_amount != 0:
                basic_amount *= 100
            # Else multiply by the magnitude term and reset the basic amount.
            else:
                magnitude = Magnitudes.get(token, None)
                if magnitude is not None:
                    magnification += basic_amount * magnitude
                    basic_amount = 0
        return magnification + basic_amount
