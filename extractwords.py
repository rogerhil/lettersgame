import os
import re
import string
import inflect

p = inflect.engine()

MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
DATA_DIR = os.path.join(MAIN_DIR, 'wordnet')
FREQ_FILE = os.path.join(MAIN_DIR, 'wordnet', 'lemma.num.txt')

MIN_LENGTH = 3

WORDS_LENGTHS = [5, 6, 7, 8, 9, 10]
FREQ_TYPES = ['adv', 'a', 'infinitive-marker', 'det', 'n', 'pron', 'modal',
              'v', 'conj', 'prep', 'interjection']
FREQ_REGEXP = re.compile('^(\d+)\s(\d+)\s([\w-]+)\s([\w-]+)$')

VALID_CHARS = string.ascii_lowercase

MOST_FREQ_FILE_PREFIX = 'most_freq'

def generate_most_frequent_words():
    afile = open(FREQ_FILE)
    lines = afile.readlines()
    afile.close()
    data = {}
    for line in lines:
        line = line.strip()
        rank, n, word, typ = FREQ_REGEXP.match(line).groups()
        word = word.replace('-', '').replace('_', '').strip()
        length = len(word)
        if not data.has_key(length):
            data[length] = []
        data[length].append("%s %s %s %s" % (rank, n, word, typ))

    for length, lis in data.items():
        filename = "%s_%s.db" % (MOST_FREQ_FILE_PREFIX, length)
        afile = open(filename, 'w')
        afile.write('\n'.join(lis))
        afile.close()

def generate_db(max_length):
    data = []
    for filename in os.listdir(DATA_DIR):
        if not filename.startswith('index'): continue
        filepath = os.path.join(DATA_DIR, filename)
        is_noun = filename.endswith('noun')
        is_verb = filename.endswith('verb')
        is_adj = filename.endswith('adj')
        afile = open(filepath)
        for line in afile.xreadlines():
            line = line.strip()
            if not line or line.startswith('  '): continue
            splited = line.split(' ')
            if not splited: continue
            word = splited[0]
            if len(word) < MIN_LENGTH or len(word) > max_length: continue
            invalid = False
            for letter in word:
                if letter not in VALID_CHARS:
                    invalid = True
                    break
            if invalid: continue
            data.append(word)
            if is_noun:
                newword = p.plural_noun(word)
                if newword and newword != word and len(newword) >= MIN_LENGTH and len(newword) <= max_length and newword not in data:
                    data.append(newword)
            if is_adj:
                newword = p.plural_adj(word)
                if newword and newword != word and len(newword) >= MIN_LENGTH and len(newword) <= max_length and newword not in data:
                    data.append(newword)
            if is_verb:
                newword = p.plural_verb(word)
                if newword and newword != word and len(newword) >= MIN_LENGTH and len(newword) <= max_length and newword not in data:
                    data.append(newword)
        afile.close()
    return data


def generate_whole_database():
    for word_length in WORDS_LENGTHS:
        data = generate_db(word_length)
        print "Total words for length (%s): %s" % (word_length, len(data))
        afile = open(os.path.join(MAIN_DIR, 'words_%s.db' % word_length), 'w')
        afile.write('\n'.join(data))
        afile.close()

generate_most_frequent_words()