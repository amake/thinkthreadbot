from __future__ import print_function
import os
import sys
import re
import logging
import wikipedia
from wikipedia import DisambiguationError
from itertools import islice
from random import shuffle, randint, choice
from collections import defaultdict
from pattern.en import pluralize


def iterslice(items, size):
    for i in xrange(0, len(items) - size + 1):
        slse = items[i:i + size]
        trailing =  items[i + size] if i + size < len(items) else None
        yield slse, trailing


class MarkovGenerator(object):
    def __init__(self, raw_data, order=5):
        self.raw_data = raw_data
        self.order = order
        self.chains = self._train()
        self.seeds = self._get_seeds()
        logging.debug(u'Seeds: %d' % len(self.seeds))
        logging.debug(u'Chain keys: %d' % len(self.chains))
        logging.debug(u'Random key: %s' % choice(self.chains.keys()))

    def _train(self):
        result = defaultdict(list)
        for item in self.raw_data:
            for key, value in iterslice(item, self.order):
                result[unicode(key)].append(value)
        return dict(result)

    def _get_seeds(self):
        regex = re.compile(ur'(?:^|(?<=\s))([A-Z].{%d})' % (self.order - 1))
        return [m.group(1) for item in self.raw_data for m in regex.finditer(item)]

    def generate(self):
        result = choice(self.seeds)
        order = len(result)
        while True:
            values = self.chains.get(unicode(result[-order:]))
            if not values:
                break
            value = choice(values)
            if not value:
                break
            result += value
        return self.generate() if result in self.raw_data else result


def random_subject():
    return wikipedia.random()

def random_intro():
    subject = random_subject()
    return subject, "OK folks, It's time to talk about %s.\n\nThread." % _pluralize(subject)

def _pluralize(word):
    if word.istitle():
        return word
    plural = pluralize(word)
    return word if plural.lower().endswith('ss') else plural

refs_pattern = re.compile(ur'=+\s*References\s*=+.*$', flags=re.DOTALL)

seg_pattern = re.compile(ur'(?<=[.?!])\s(?=\S)')

def _get_page(subject):
    try:
        page = wikipedia.page(subject)
    except DisambiguationError, e:
        page = wikipedia.page(e.options[0])
    full_text = page.content
    text_no_refs = refs_pattern.sub('', full_text)
    paragraphs = [p for p in text_no_refs.split('\n') if p and not p.startswith('==')]
    return [sent for p in paragraphs for sent in seg_pattern.split(p)]

def random_sentences(data):
    generator = MarkovGenerator(data)
    while True:
        sent = generator.generate()
        yield sent[0].upper() + sent[1:]

def random_thread():
    subject, intro = random_intro()
    logging.debug(u'Subject: %s' % subject)
    sentences = _get_page(subject)
    logging.debug(sentences)
    warmup_gen = (sent for sent in sentences if len(sent) < 137)
    warmup = list(islice(warmup_gen, 2))
    count = min(len(sentences), randint(5, 20))
    gen_sents = (sent for sent in random_sentences(sentences)
                 if len(sent) < 137 and len(sent.split()) > 4)
    more = list(islice(gen_sents, count - len(warmup)))
    tweets = [intro] + warmup + more
    return ['%s /%s' % (tweet, 'end' if n == count else str(n + 1))
            for n, tweet in enumerate(tweets)]

def main():
    print('\n'.join(random_thread()).encode('utf-8'))


if __name__ == '__main__':
    import sys
    if '-v' in sys.argv:
        logging.getLogger().setLevel(logging.DEBUG)
    main()
