from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag, RegexpParser
import spacy
import re
import nltk

nltk.download('averaged_perceptron_tagger')

def to_word_tokens(data):
    return word_tokenize(data)

def pos_tagging(data):
    # pos tagging with nltk pos_tag
    return pos_tag(data)

def get_entities(seq):
    pos_tagged_seq = pos_tagging(seq)
    entities = []
    read_nnp = False
    curr_nnp = ""

    for token in pos_tagged_seq:
        # collect proper noun phrases
        if (token[1] == "NNP"):
            if (not read_nnp):
                curr_nnp = token[0]
                read_nnp = True
            else:
                curr_nnp += " "+token[0]
        else:
            if (read_nnp):
                entities.append(curr_nnp)
                curr_nnp = ""
                read_nnp = False
        
    if (read_nnp):
        entities.append(curr_nnp)
        curr_nnp = ""
        read_nnp = False

    return entities