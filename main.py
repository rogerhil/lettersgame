import os
import re
import pygame
import string
import random
from pygame.locals import *
from pygame.compat import geterror
import time

DISPLAY_WIDTH = 1560
DISPLAY_HEIGHT = 760

MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
DATA_DIR = os.path.join(MAIN_DIR, 'wordnet')

DISPLAY_SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLOCK_SIZE = 140
MATRIX_SIZE = (DISPLAY_WIDTH / BLOCK_SIZE, DISPLAY_HEIGHT / BLOCK_SIZE)

FREQ_REGEXP = re.compile('^(\d+)\s(\d+)\s([\w-]+)\s([\w-]+)$')

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
img_dir = os.path.join(main_dir, 'img')

FREQ_TYPES = {
    'adv': 'Adverb',
    'a': 'Adjective',
    'infinitive-marker': 'Infinitive Marker',
    'det': 'Determiner',
    'n': 'Noun',
    'pron': 'Pronoun',
    'modal': 'Modal',
    'v': 'Verb',
    'conj': 'Conjunction',
    'prep': 'Proposition',
    'interjection': 'Interjection'
}

TYPES = {
    'adv': 'adv',
    'a': 'adj',
    'infinitive-marker': 'verb',
    #'det': 'Determiner',
    'n': 'noun',
    #'pron': 'Pronoun',
    #'modal': 'Modal',
    'v': 'verb',
    #'conj': 'Conjunction',
    #'prep': 'Proposition',
    #'interjection': 'Interjection'
}


class WordsDatabase(object):

    def __init__(self, word_length):
        self.word_length = word_length
        self.words = {}
        self.full_words = []
        self.freq_words = {}
        self.load_words()

    def load_words(self):
        afile = open(os.path.join(main_dir, 'words_%s.db' % self.word_length))
        for line in afile.xreadlines():
            line = line.strip()
            if len(line) == self.word_length:
                self.full_words.append(line)
            w1, w2, w3, rest = line[0], line[1], line[2], line[3:]
            if not self.words.has_key(w1):
                self.words[w1] = {}
            if not self.words[w1].has_key(w2):
                self.words[w1][w2] = {}
            if not self.words[w1][w2].has_key(w3):
                self.words[w1][w2][w3] = []
            self.words[w1][w2][w3].append(rest)
        afile.close()
        filename = 'most_freq_%s.db' % self.word_length
        afile = open(os.path.join(main_dir, filename))
        for line in afile.xreadlines():
            rank, n, word, typ = FREQ_REGEXP.match(line).groups()
            if not self.freq_words.has_key(word):
                self.freq_words[word] = []
            self.freq_words[word].append((rank, n, typ))
        afile.close()

    def get_random_word(self):
        word = self.full_words[random.randint(0, len(self.full_words))]
        return word

    def get_random_word_by_frequency(self, freq=0):
        freq = abs(int(freq))
        all_words = self.freq_words.keys()
        length = len(all_words)
        freq = freq if freq < 4 else 3
        if not freq:
            fro, to = 0, length
        else:
            setn = length / 3
            fro, to = setn * (freq - 1), setn * freq
        word = all_words[random.randint(fro, to)]
        print word
        return word

    def get_word_details(self, word):
        details = []
        def get_meaning(ext, ind):
            filename = 'data.%s' % ext
            datafile = open(os.path.join(DATA_DIR, filename))
            m = ''
            for line in datafile.xreadlines():
                if line.startswith(' '):
                    continue
                if line.startswith(ind):
                    ind_det, m = line.split(' | ')
                    break
            return m.strip()

        for rank, n, typ in self.freq_words.get(word):
            ext = TYPES.get(typ)
            if not ext:
                continue
            filename = 'index.%s' % ext
            indfile = open(os.path.join(DATA_DIR, filename))
            meaning = []
            for line in indfile.xreadlines():
                if line.startswith(' '):
                    continue
                splited = line.split(' ')
                if not splited:
                    continue
                if splited[0] == word:
                    inds = [s for s in splited if s.isdigit() and len(s) == 8]
                    for ind in inds:
                        meaning.append(get_meaning(ext, ind))
                    break
            details.append((rank, n, typ, meaning))

        return details

    def word_exists(self, word):
        if len(word) < 3 or len(word) > self.word_length:
            return False
        w1, w2, w3, rest = word[0], word[1], word[2], word[3:]
        matches = self.words.get(w1, {}).get(w2, {}).get(w3, {})
        return rest in matches


#functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join(img_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    #image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound


class Alphabet(object):

    letters = list(set(string.letters.lower()))

    def __init__(self):
        for letter in self.letters:
            self.load_image_rect("%s.png" % letter)

    def load_image_rect(self, filename):
        img = load_image(filename)
        name, ext = os.path.splitext(filename)
        setattr(self.__class__, '%s' % name, property(self._new_letter(img)))

    def _new_letter(self, img):
        return lambda s: (img, img.get_rect().copy())

    @classmethod
    def validate(cls, letter):
        letter = letter.strip().lower()
        valid = letter.strip().lower() in cls.letters
        if valid:
            return letter


class GameSprite(pygame.sprite.DirtySprite):

    def __init__(self):
        super(GameSprite, self).__init__()
        self.moving = False
        self.move_dest = 0, 0
        self.move_distance = 0, 0
        self.move_pass = 0, 0
        self.timerun = 2
        self.position = 0, 0
        self.last_position = 0, 0
        self.last_destiny = 0, 0
        self.move_count = 0

    def move(self, pos, timerun=12):
        self.last_position = self.move_dest
        #if self.moving:
        #    self.position = self.move_dest
        #    self.rect.midtop = self.position
        x, y = pos
        self.moving = True
        self.move_dest = pos
        self.timerun = timerun
        x2, y2 = self.position
        dx, dy = x - x2,  y - y2
        self.move_distance = dx, dy
        self.move_pass = (float(dx) / timerun, float(dy) / timerun)
        self.move_count = 0

    def update(self):
        if not self.moving:
            return
        self.position = self.rect.midtop
        if self.move_count >= self.timerun:
            self.moving = False
            self.move_count = 0
            self.position = self.move_dest
            self.rect.midtop = self.position
            return
        newpos = self.rect.move(self.move_pass)
        self.rect = newpos
        self.move_count += 1
        self.visible = 1
        self.position = self.rect.midtop


class Letter(GameSprite):

    alphabet = None

    def __init__(self, letter):
        super(Letter, self).__init__() # call Sprite initializer
        if not self.alphabet:
            self.__class__.alphabet = Alphabet()
        self.image, self.rect = getattr(self.alphabet, letter)
        self.clicking = False
        self.letter = letter
        self.letter_position = 0, 0
        self.rect.midtop = self.position

    def update(self):
        super(Letter, self).update()

    def click(self, target):
        if not self.clicking:
            self.clicking = True
            hitbox = self.rect.inflate(-5, -5)
            if hitbox.colliderect(target.rect):
                self.rect.move_ip(5, 10)

    def _mpos(self, pos):
        return tuple([i * BLOCK_SIZE for i in pos])

    def unclick(self):
        self.punching = False

    def set_letter_position(self, pos, reload=True):
        self.letter_position = pos
        self.position = self._mpos(pos)
        self.move_dest = self.position
        if reload:
            self.reload_position()

    def reload_position(self):
        self.rect.midtop = self._mpos(self.letter_position)

    def move_letter(self, pos, *args, **kwargs):
        super(Letter, self).move(self._mpos(pos), *args, **kwargs)
        
    def move_to_last_position(self):
        self.move(self.last_position)

class Word(object):

    def __init__(self, word):
        self.word = word.strip().lower()
        shuffled = [i for i in word]
        random.shuffle(shuffled)
        self.shuffled = ''.join(shuffled)
        self.letters = []
        for s in shuffled:
            self.letters.append(Letter(s))
        self.position = 0, 0
        self.last_position = 0, 0
        self.letters_count = {}
        self.pushed_letters = {}
        for l in self.letters:
            if not self.pushed_letters.has_key(l.letter):
                self.pushed_letters[l.letter] = []
            if not self.letters_count.has_key(l.letter):
                self.letters_count[l.letter] = 0
            self.letters_count[l.letter] += 1
        self.reload()

    def reload(self):
        self.pushed_letters = {}
        for l in self.letters:
            if not self.pushed_letters.has_key(l.letter):
                self.pushed_letters[l.letter] = []

    def set_position(self, pos):
        self.last_position = self.position
        self.position = pos
        self.reload_position()

    def reload_position(self):
        x, y = self.position
        for i, l in enumerate(self.letters):
            l.set_letter_position((x + i, y))

    def reload_pushed_letters_from_last_position(self):
        for letters in self.pushed_letters.values():
            for l in letters:
                l.move_to_last_position()

    def push_letter(self, l):
        self.pushed_letters[l.letter].append(l)

    def can_push_letter(self, letter):
        if letter not in self.letters_count.keys():
            return False
        count = self.letters_count[letter]
        return len(self.pushed_letters[letter]) < count

    def clear_pushed(self):
        self.pushed_letters = []

    def stack_length(self):
        return sum([len(l) for l in self.pushed_letters.values()])


class Level(object):

    len_score = {3:5, 4:10, 5:15, 6:20, 7:30, 8:40}
    max_score = 100
    max_time = 20

    def __init__(self, number, word_db):
        self.number = number
        self.word_db = word_db
        self.score = 0
        self.word = Word(self.word_db.get_random_word_by_frequency(1))
        self._finished = False
        self.pushed_already = []
        self.t0 = time.time()
        self.objects = {'letters': [], 'word': {}, 'other': []}
        self._showing_word = False
        self.won = False

    def compute_word(self, word):
        if word == self.word.word:
            self._finished = True
            self.won = True
            return
        if self.elapsed_time() > self.max_time:
            self._finished = True
            return
        if word in self.pushed_already:
            return
        if not self.word_db.word_exists(word):
            return
        length = len(word)
        self.score += self.len_score.get(length)
        self.pushed_already.append(word)
        if self.score >= self.max_score:
            self.score = self.max_score
            self._finished = True
            self.won = True
            return

    def start(self):
        self.word.set_position((1, 4))
        self.reload()

    def reload(self):
        self.objects['letters'] = []
        self.objects['word'] = {}
        self.objects['other'] = []
        for l in self.word.letters:
            if not self.objects['word'].has_key(l.letter):
                self.objects['word'][l.letter] = []
            self.objects['word'][l.letter].append(l)
        for i in xrange(self.word_db.word_length):
            img = load_image('empty.png')
            rect = img.get_rect()
            rect.midtop = ((i + 1) * BLOCK_SIZE, (3 * BLOCK_SIZE) - 5)
            spr = GameSprite()
            spr.image = img
            spr.rect = rect
            self.objects['other'].append(spr)

    def rel(self):
        self.reload()
        self.word.reload_pushed_letters_from_last_position()
        self.word.reload()

    def all_sprites_ordered(self):
        sprites = list()
        sprites.append(self.objects['other'])
        for sprite_set in self.objects['word'].values():
            sprites.append(sprite_set)
        sprites.append(self.objects['letters'])
        return sprites

    def all_sprites(self):
        sprites = []
        for sprite_set in self.all_sprites_ordered():
            sprites += sprite_set
        return sprites

    def moving(self):
        return any([o.moving for o in self.all_sprites()])

    def enter_word(self):
        sw = ''.join([l.letter for l in self.objects['letters']])
        self.compute_word(sw)
        if self.finished():
            return
        self.rel()

    def process_letter(self, char):
        letter = Alphabet.validate(char)
        if not letter:
            return
        if letter not in self.word.shuffled:
            return
        if not self.word.can_push_letter(letter):
            return
        self.put_letter(letter, len(self.objects['letters']))

    def put_letter(self, char, pos):
        letter = self.objects['word'].get(char).pop(0)
        self.word.push_letter(letter)
        letter.move_letter((1 + pos, 3))
        self.objects['letters'].append(letter)

    def show_word(self):
        if self._showing_word:
            return
        self._showing_word = True
        self.reload()
        self.word.reload()
        for i, char in enumerate(self.word.word):
            self.put_letter(char, i)

    def elapsed_time(self):
        return 0 if self.finished() else time.time() - self.t0

    @property
    def count_down_time(self):
        return int(self.max_time - self.elapsed_time())

    def finished(self):
        return self._finished

    def process(self):
        if self.finished():
            return
        if self.elapsed_time() > self.max_time:
            self._finished = True

    def current_word_details(self):
        return self.word_db.get_word_details(self.word.word)


class Game(object):

    def __init__(self, background, word_length):
        self.current_level = None
        self.word_db = WordsDatabase(word_length)
        self.word_details = []
        self.levels = []
        self.score = 0
        self.background = background
        self._started = False
        self._sprites_cache = []
        self.bg_color = (220, 220, 220)

    def start(self):
        self.load_level(1)
        self.load_all_sprites_for_render()
        self._started = True

    def has_started(self):
        return self._started

    def process(self, clock):
        level = self.current_level
        level.process()
        if level.finished():
            if not level.moving():
                level.show_word()
        self.load_all_sprites_for_render()
        self.display_level_score()
        if level.finished():
            if level.won:
                self.display_won()
            else:
                self.display_game_over()
        return self._sprites_cache

    def load_next_level(self):
        self.load_level(len(self.levels) + 1)
        self.load_all_sprites_for_render()
        self.bg_color = tuple([(c - 10) - (i * 2) for i, c in
                               enumerate(self.bg_color)])

    def load_level(self, number):
        level = Level(number, self.word_db)
        self.current_level = level
        self.levels.append(level)
        level.start()
        self.display_level_score()
        self.word_details = level.current_word_details()

    def load_all_sprites_for_render(self):
        sprites = []
        for sprite in self.current_level.all_sprites_ordered():
            rendered = pygame.sprite.RenderPlain(sprite)
            rendered.update()
            sprites.append(rendered)
        self._sprites_cache = sprites

    def process_event(self, event):
        level = self.current_level
        if event.type == MOUSEBUTTONDOWN:
            pass
        elif event.type == MOUSEBUTTONUP:
            pass
        elif event.type == KEYDOWN and event.dict.get('key') == 13:
            if level.finished():
                if level.won:
                    self.load_next_level()
            else:
                level.enter_word()
        elif event.type == KEYDOWN:
            level.process_letter(event.dict['unicode'])

        return False

    def display_game_over(self):
        font = pygame.font.Font(None, 100)
        text = font.render("G A M E    O V E R", 1, (255, 10, 10))
        textpos = text.get_rect(centerx=self.background.get_width()/2, y=150)
        self.background.blit(text, textpos)
        self.display_current_word_details()

    def display_won(self):
        font = pygame.font.Font(None, 100)
        text = font.render("C O N G R A T U L A T I O N S", 1, (160, 90, 120))
        textpos = text.get_rect(centerx=self.background.get_width()/2, y=150)
        self.background.blit(text, textpos)
        self.display_current_word_details()

    def display_current_word_details(self):
        details = self.word_details
        if not details:
            return
        starty = 220
        for i, detail in enumerate(details):
            rank, n, typ, meaning = detail
            font = pygame.font.Font(None, 40)
            text = 'This is the %sth english word (%s) most frequently ' \
                   'used' % (rank, FREQ_TYPES.get(typ, typ))
            text = font.render(text, 1, (160, 90, 10))
            textpos = text.get_rect(centerx=self.background.get_width()/2,
                                    y=starty)
            self.background.blit(text, textpos)
            if meaning:
                starty += 20
            for m in meaning:
                font = pygame.font.Font(None, 20)
                font.set_bold(True)
                whole_text = "* %s" % m.capitalize()
                length = (len(whole_text) / 100)
                for p in xrange(length + 1):
                    text = whole_text[p: 100 + p]
                    text = font.render(text, 1, (160, 90, 10))
                    textpos = text.get_rect(centerx=self.background.get_width()/2,
                                            y=starty + 20)
                    self.background.blit(text, textpos)
                    starty += 15
            starty += 40

    def display_score(self):
        level = self.current_level
        font = pygame.font.Font(None, 36)
        text = font.render("SCORE %s" % level.score, 1, (10, 10, 10))
        textpos = text.get_rect(centerx=self.background.get_width()/2, y=100)
        self.background.blit(text, textpos)

    def display_level(self):
        level = self.current_level
        font = pygame.font.Font(None, 36)
        text = font.render("LEVEL %s" % level.number, 1, (10, 10, 10))
        textpos = text.get_rect(centerx=self.background.get_width()/2, y=20)
        self.background.blit(text, textpos)

    def display_time(self):
        level = self.current_level
        font = pygame.font.Font(None, 36)
        text = font.render("TIME %s" % level.count_down_time, 1, (10, 10, 10))
        textpos = text.get_rect(centerx=self.background.get_width()/2 + 200,
                                y=100)
        self.background.blit(text, textpos)

    def display_found(self):
        level = self.current_level
        font = pygame.font.Font(None, 36)
        text = font.render("FOUND", 1, (10, 10, 10))
        textpos = text.get_rect(x=50, y=50)
        self.background.blit(text, textpos)
        for i, word in enumerate(level.pushed_already):
            text = font.render(word.upper(), 1, (255, 10, 10))
            textpos = text.get_rect(x=50, y=(50 + 25 * (i+1)))
            self.background.blit(text, textpos)

    def display_level_score(self):
        self.background.fill(self.bg_color)
        self.display_level()
        self.display_found()
        self.display_score()
        self.display_time()


class Main(object):

    word_lengths = range(5, 11)

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(DISPLAY_SIZE)
        pygame.display.set_caption('Letters')
        pygame.mouse.set_visible(1)

        #Create The Backgound
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((200, 200, 200))

        #Display The Background
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        self.clock = pygame.time.Clock()
        self._running = False
        self.game = None

    def draw_all(self, all_sprites):
        self.screen.blit(self.background, (0, 0))
        for sprites in all_sprites:
            sprites.draw(self.screen)
        pygame.display.flip()

    def run(self):
        if self._running:
            return
        quit = False
        while not quit:
            self._running = True
            self.clock.tick(60)
            if self.game:
                all_sprites = self.game.process(self.clock)
            else:
                all_sprites = []
            for event in pygame.event.get():
                if self.game:
                    self.game.process_event(event)
                quit = self.process_global_events(event)
            self.draw_all(all_sprites)

    def start_game(self, number):
        self.game = Game(self.background, number)
        self.game.start()

    def process_global_events(self, event):
        if event.type == QUIT:
            return True
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            return True
        elif event.type == KEYDOWN:
            if event.dict.get('key') == 13:
                if not self.game:
                    self.start_game(8)
            elif event.dict.get('key') == 8:
                self.game = None
                self.show_main_screen()
            else:
                char = event.dict['unicode']
                if char.isdigit():
                    n = int(char)
                    if n in self.word_lengths:
                        self.start_game(n)
        return False

    def show_main_screen(self):
        self.background.fill((30, 20, 40))
        font = pygame.font.Font(None, 120)
        text_color = (220, 220, 220)
        text = font.render("5210   L e t t e r s".upper(), 1, text_color)
        bgwidth = self.background.get_width()
        bgheight = self.background.get_height()
        textpos = text.get_rect(centerx=bgwidth / 2, y=bgheight / 3)
        self.background.blit(text, textpos)
        font = pygame.font.Font(None, 66)
        text = font.render("Choose the word length to play".lower(), 1,
                            text_color)
        textpos = text.get_rect(centerx=bgwidth / 2, y=(bgheight / 2))
        self.background.blit(text, textpos)
        for i, length in enumerate(self.word_lengths):
            text = font.render(str(length), 1, text_color)
            textpos = text.get_rect(centerx=550 + i * 90, y=(bgheight / 3)*2)
            self.background.blit(text, textpos)


if __name__ == '__main__':
    main = Main()
    main.show_main_screen()
    main.run()
    pygame.quit()

