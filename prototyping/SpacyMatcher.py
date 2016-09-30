from __future__ import unicode_literals, print_function

import spacy.en
import spacy.matcher
from spacy.attrs import ORTH, TAG, LOWER, IS_ALPHA, FLAG63

import plac


def main():
    nlp = spacy.en.English(parser=False, load_vectors=False, tagger=False)
    example = u"What is my best selling pops volley of all time?"
    nlp.matcher.add(
        "Product_Name", # Entity ID: Not really used at the moment.
        "PRODUCT",   # Entity type: should be one of the types in the NER data
        {"product_name": "pops volley"}, # Arbitrary attributes. Currently unused.
        [  # List of patterns that can be Surface Forms of the entity

            # This Surface Form matche
            [ # Each Surface Form is a list of Token Specifiers.
                { # This Token Specifier matches tokens whose orth field is "Google"
                    ORTH: "Pops"
                },
                { # This Token Specifier matches tokens whose orth field is "Now"
                    ORTH: "Volley"
                }
            ],
            [ # This Surface Form matches "google now", verbatim, and requires
              # "google" to have the NNP tag. This helps prevent the pattern from
              # matching cases like "I will google now to look up the time"
                {
                    ORTH: "pops"
                },
                {
                    ORTH: "volley"
                }
            ]
        ]
    )
    result = nlp(example)
    for ent in result.ents:
        print(ent.text, ent.label_, [w.tag_ for w in ent])
     
    product_sizes = ['Small','S', 'extra-small','XS','Medium','M','L','Large','XL', 'extra-large', 'x-large']
    # Internally, the tokenizer immediately maps each token to a pointer to a 
    # LexemeC struct. These structs hold various features, e.g. the integer IDs
    # of the normalized string forms.
    # For our purposes, the key attribute is a 64-bit integer, used as a bit field.
    # spaCy currently only uses 12 of the bits for its built-in features, so
    # the others are available for use. It's best to use the higher bits, as
    # future versions of spaCy may add more flags. For instance, we might add
    # a built-in IS_MONTH flag, taking up FLAG13. So, we bind our user-field to
    # FLAG63 here.
    is_product_size = FLAG63
    # Now we need to set the flag value. It's False on all tokens by default,
    # so we just need to set it to True for the tokens we want.
    # Here we iterate over the strings, and set it on only the literal matches.
    for string in product_sizes:
        lexeme = nlp.vocab[string]
        lexeme.set_flag(is_product_size, True)
    print('extra small', nlp.vocab[u'extra small'].check_flag(is_product_size))
    print('large', nlp.vocab[u'large'].check_flag(is_product_size))
    # If we want case-insensitive matching, we have to be a little bit more
    # round-about, as there's no case-insensitive index to the vocabulary. So
    # we have to iterate over the vocabulary.
    # We'll be looking up attribute IDs in this set a lot, so it's good to pre-build it
    target_ids = {nlp.vocab.strings[s.lower()] for s in product_sizes}
    for lexeme in nlp.vocab:
        if lexeme.lower in target_ids:
            lexeme.set_flag(is_product_size, True)
    print('XL', nlp.vocab[u'XL'].check_flag(is_product_size))
    print('xl', nlp.vocab[u'xl'].check_flag(is_product_size))
    print('extra-small', nlp.vocab[u'extra-small'].check_flag(is_product_size))


    # The key thing to note here is that we're setting these attributes once,
    # over the vocabulary --- and then reusing them at run-time. This means the
    # amortized complexity of anything we do this way is going to be O(1). You
    # can match over expressions that need to have sets with tens of thousands
    # of values, e.g. "all the street names in Germany", and you'll still have
    # O(1) complexity. Most regular expression algorithms don't scale well to
    # this sort of problem.
    #
    # Now, let's use this in a pattern
    nlp.matcher.add("Product Size", "PROD_SIZE", {},
        [
            [   {ORTH:'xx'},
                {is_product_size: True}
            ],
            [   {ORTH:'x'},
                {is_product_size: True}
            ],
            [   {ORTH:'extra'},
                {is_product_size: True}
            ],
            [
                {is_product_size: True}
            ]
        ])
    
    print("\nTest one")
    doc = nlp(u'What is the best selling extra large Pops Volley?')
    print(doc.text)
    for ent in doc.ents:
        print(ent.text, ent.label_)
    
    print("\nTest two")
    doc = nlp(u'What is the best selling XL Pops Volley?')
    print(doc.text)
    for ent in doc.ents:
        print(ent.text, ent.label_)
    
    print("\nTest three")  
    doc = nlp(u'What is the best selling medium Pops Volley?')
    print(doc.text)
    for ent in doc.ents:
        print(ent.text, ent.label_)
    
    print("\nTest four")  
    doc = nlp(u'What is the best selling extra small Pops Volley?')
    print(doc.text)
    for ent in doc.ents:
        print(ent.text, ent.label_)
        
    print("\nTest four")  
    doc = nlp(u'How many medium pops volley do I have in stock?')
    print(doc.text)
    for ent in doc.ents:
        print(ent.text, ent.label_)
    
    print("\nTest five")  
    doc = nlp(u'How many L pops volley do I have in stock?')
    print(doc.text)
    for ent in doc.ents:
        print(ent.text, ent.label_)     
        
    print("\nTest six")  
    doc = nlp(u'How many M pops volley do I have in stock?')
    print(doc.text)
    for ent in doc.ents:
        print(ent.text, ent.label_)
    
    print("\nTest six")  
    doc = nlp(u'How many small pops volley do I have in stock?')
    print(doc.text)
    for ent in doc.ents:
        print(ent.text, ent.label_) 


if __name__ == '__main__':
    main()