#!/bin/python
#
# Chisne ShengJi card game
# Song, Qiang <keeyang@ustc.edu>
#
# card and carddeck definication

import random

class Card:
    specialvals = dict({11:"J", 12:"Q", 13:"K", 14:"A"})
    def __init__(self, suit = "NA", number = -1):
        self.suit = suit
        self.number = number

    def construct_from_str(self, s):
        (self.suit, self.number) = s.split(":")
        if self.number == "J": self.number = 11
        if self.number == "Q": self.number = 12
        if self.number == "K": self.number = 13
        if self.number == "A": self.number = 14
        self.number = int(self.number)
        return self
                
    def __str__(self):
        return self.suit + ":" + (str(self.number) if self.number <= 10 \
                                    else Card.specialvals[self.number])
    def get_score(self):
        return 5 * (1 + int(self.number >= 10)) if self.number in [5, 10, 13] else 0
    def __eq__(self, other): 
        return self.__dict__ == other.__dict__

    def __lt__(self, other): 
        return ord(self.suit) * 100 + self.number \
          < ord(other.suit) * 100 + other.number 

    def is_pair(self, other):
        return self == other

class CardDeck:
    def __init__(self, n_set):
        self.cards = list([])
        for j in range(n_set):
            self.cards.extend([Card("S", i) for i in range(2, 15)])
            self.cards.extend([Card("D", i) for i in range(2, 15)])
            self.cards.extend([Card("H", i) for i in range(2, 15)])
            self.cards.extend([Card("C", i) for i in range(2, 15)])
            self.cards.extend([Card("J", i) for i in range(0, 2)])
        self.shuffle()

    def shuffle(self):
        """shuffle cards
        Arguments:
        - `self`:
        """
        random.shuffle(self.cards)


    def get_card(self):
        card = self.cards[-1]
        del self.cards[-1]
        return card
