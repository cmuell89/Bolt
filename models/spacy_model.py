'''
Created on Jul 4, 2016

This might simply be replaced by textacy's caching from which this code is taken. 
I want to see it in action up close before I make use of textacy for calls to SpaCy


@author: carl
'''

from functools import partial
import logging
import os
from cachetools import cached, Cache
from cachetools.keys import hashkey
import spacy


logger = logging.getLogger('BOLT.spacy')


@cached(Cache(1), key=partial(hashkey, 'spacy'))
def load_spacy(name, **kwargs):
    """
    Load a language-specific spaCy pipeline (collection of data, models, and
    resources) for tokenizing, tagging, parsing, etc. text; the most recent
    package loaded is cached.
    Args:
        name (str): standard 2-letter language abbreviation for a language;
            currently, spaCy supports English ('en') and German ('de')
        **kwargs: keyword arguments passed to :func:`spacy.load`; see the
            `spaCy docs <https://spacy.utils/docs#english>`_ for details
            * via (str): non-default directory from which to load package data
            * vocab
            * tokenizer
            * parser
            * tagger
            * entity
            * matcher
            * serializer
            * vectors
    Returns:
        :class:`spacy.<lang>.<Language>`
    Raises:
        RuntimeError: if package can't be loaded
    """
    spacy_datapath = os.environ.get('SPACY_DATA_PATH')
    logger.info('Spacy datapath: "%s"', spacy_datapath)
    spacy.util.set_data_path(spacy_datapath)
    logger.info('Caching "%s" language spaCy', name)
    return spacy.load(name, **kwargs)
