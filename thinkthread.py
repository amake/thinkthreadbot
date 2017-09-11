from __future__ import print_function
import os
import sys
import re
import random
import nltk
from nltk.corpus.reader import PlaintextCorpusReader, TaggedCorpusReader, TaggedCorpusView
from nltk.tokenize import BlanklineTokenizer
from pattern.en import pluralize

nouns = []

def load_words(filename):
    if os.path.isfile(filename):
        with open(filename) as f:
            return f.read().splitlines()
    else:
        print(filename + ' not found. Generate it.')
        sys.exit(1)

nouns = load_words('nouns.txt')

def random_subject():
    return random.choice(nouns)

def random_intro():
    subject = random_subject()
    return subject, "OK folks, It's time to talk about %s.\n\nThread." % _pluralize(subject)

def _pluralize(word):
    plural = pluralize(word)
    return word if plural.lower().endswith('ss') else plural

sentences = None

corpora = [nltk.corpus.reuters, nltk.corpus.brown, nltk.corpus.inaugural]

def _get_sentences():
    global sentences
    if sentences is None:
        sentences = [_join(sent) for corpus in corpora for  sent in corpus.sents()]
    return sentences

def random_thread():
    while True:
        subject, intro = random_intro()
        more = [sent for sent in _get_sentences()
                if re.search(r'\b%s\b' % subject, sent) and len(sent) < 137]
        if len(more) > 2:
            random.shuffle(more)
            return [intro] + more[:20]

close_front = '.,:;'
close_both = '\''
deduplicate = '!'

def _join(words):
    result = ' '.join(words)
    for c in close_front:
        result = result.replace(' ' + c, c)
    for c in close_both:
        result = result.replace(' ' + c + ' ', c)
    for c in deduplicate:
        result = result.replace(c + ' ' + c, c)
    return result

def _sentences_from_corpus(corpus, fileids=None):
    from nltk.corpus.reader.plaintext import read_blankline_block, concat
    def read_sent_block(stream):
        sents = []
        for para in corpus._para_block_reader(stream):
            sents.extend([s.replace('\n', ' ') for s in corpus._sent_tokenizer.tokenize(para)])
        return sents
    return concat([corpus.CorpusView(path, read_sent_block, encoding=enc)
                   for (path, enc, fileid)
                   in corpus.abspaths(fileids, True, True)])

def _sentences_from_tagged_corpus(corpus, fileids=None):
    from nltk.corpus.reader.plaintext import read_blankline_block, concat
    return concat([TaggedCorpusView(fileid, enc,
                                    False, True, False,
                                    corpus._sep, corpus._word_tokenizer,
                                    corpus._sent_tokenizer,
                                    corpus._para_block_reader,
                                    None)
                   for (fileid, enc) in corpus.abspaths(fileids, True)])

if __name__ == '__main__':
    print('\n'.join(['%s /%d' % (tweet, n + 1) for n, tweet in enumerate(random_thread())]))
