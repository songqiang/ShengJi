#! /bin/python
#
# Chisne ShengJi card game
# Song, Qiang <keeyang@ustc.edu>
#

import sys

from Card import Card
from Card import CardDeck
from Player import Player

class GameMaster:
    def __init__(self, level):
        """initialize game
        Arguments:
        - `self`:
        """
        self.carddeck = CardDeck(2)
        self.players = [Player(i) for i in range(4)]
        self.level = level
        self.dealer = 0
        self.last_player = -1
        self.trump = "Z"
        self.non_trumps = ["H", "S" "D", "C"] 
        self.trump_card = None
        self.oddscore = 0
        self.evenscore = 0
        self.round = 0

    def deal_cards(self):
        for i in range(25):
            for p in range(4):
                self.players[p].receive_card(self.carddeck.get_card(), self)
        print "Level={:d}, Trump={}".format(self.level, self.trump)
        for p in self.players:
            print p

    def set_trump(self, card):
        if not self.trump_card and card.number == self.level:
            self.trump = card.suit
            self.trump_card = card
            #            if self.trump != "J": self.non_trumps.remove(self.trump)        

    def is_pair(self, cards):
        return len(cards) == 2 and cards[0].is_pair(cards[1])
    
    def is_tuolaji(self, cards):
        if len(cards) != 4: return False
        cards.sort()
        if cards[0].suit == "J" or cards[0].number == self.level \
            or cards[0].suit == self.trump:
            return False ## not correct
        else:
            return all([cards[0].suit == c.suit for c in cards]) \
              and cards[0].is_pair(cards[1]) and cards[2].is_pair(cards[3]) \
              and (cards[0].number + 1 == cards[2].number if cards[0].number != self.level - 1 else cards[0].number + 2 == cards[2].number)
             

    def get_key(self, card):
        return (card.suit == "J")*100000 + (card.number == self.level)*10000 \
          + (card.suit == self.trump)*1000 + ord(card.suit)*10 + card.number
                
    def cmp_card_single(self, card1, card2):
        return self.get_key(card1) + (card1.suit != card2.suit)*100 \
          > self.get_key(card2)

    def cmp_card_pair(self, cards1, cards2):
        return self.get_key(cards1[0]) + (cards1[0].suit != cards2[0].suit)*100 \
          > self.get_key(cards2[0])

    def cmp_card_tuolaji(self, cards1, cards2):
        return self.get_key(cards1[0]) + (cards1[0].suit != cards2[0].suit)*100 \
          > self.get_key(cards2[0])

    def cmp_card(self, cards1, cards2):
        """
        compare cards taking into accoutn of zhu
        """
        if len(cards1) != len(cards2): 
            raise Exception("Cards sequences differ in length")
        if not cards1 and not cards2: return True    
        cards1.sort(key = self.get_key, reverse = True)
        cards2.sort(key = self.get_key, reverse = True)
        if self.is_tuolaji(cards1[0:4]):
            if self.is_tuolaji(cards2[0:4]):
                return self.cmp_card_tuolaji(cards1[0:4], cards2[0:4]) # cannot have the same tuolaji
            else:
                return True
        elif self.is_pair(cards1[0:2]):
            if self.is_pair(cards2[0:2]): 
                return self.cmp_card_pair(cards1[0:2], cards2[0:2]) # cannot have same pair
            else:
                return True
        elif cards1[0] == cards2[0]:
            return self.cmp_card(cards1[1:], cards2[1:])
        else:    
            return self.cmp_card_single(cards1[0], cards2[0])
        
    def validate_play_first(self):
        ## make sure it correctly played
        if len(self.players[self.dealer].playedcards) != self.round \
            or self.players[self.dealer].playedcards[-1].empty():
            return False
        
        self.players[self.dealer].playedcards[-1].sort( \
            key = lambda c: ord(x.suit) * 100 + x.number)

        ## single card: no need to check
        if len(self.players[self.dealer].playedcards[-1]) == 1:
            pass
        elif len(self.players[self.dealer].playedcards[-1]) == 2:
            if not self.is_pair(self.players[self.dealer].playedcards[-1]):
                for card in self.players[self.dealer].playedcards[-1]:
                    for p in range(4):
                        if p != self.dealer \
                            and self.players[p].has_better_card_single(card, game):
                            return False
        elif len(self.players[self.dealer].playedcards[-1]) == 4:
            pass
        else:
            pass 

        return True
        
    def play_round(self):
        self.players[self.dealer].play_card_first(self)
        self.validate_play_first()
        self.last_player = self.dealer

        self.players[(self.dealer + 1) % 4].play_card_second(self)
        self.last_player = (self.dealer + 1) % 4

        self.players[(self.dealer + 2) % 4].play_card_third(self)
        self.last_player = (self.dealer + 2) % 4

        self.players[(self.dealer + 3) % 4].play_card_fourth(self)
        self.last_player = -1
            
        ## determine winner
        winner = self.dealer
        score = self.players[winner].playedcards[-1][0].get_score()
        for p in range(self.dealer + 1, self.dealer + 4):
            score += self.players[p % 4].playedcards[-1][0].get_score()
            if not self.cmp_card(self.players[winner].playedcards[-1], self.players[p % 4].playedcards[-1]):
                winner = p % 4
        
        if winner % 2 == 0:
            self.evenscore += score
        else:
            self.oddscore += score
        self.dealer = winner % 4

        print "Winner={:d}, N/S={:d}, E/W={:d}".format(self.dealer, 
                                                       self.oddscore,
                                                       self.evenscore) 
        for p in range(4):
            sys.stdout.write(str(p) + ": ")
            self.players[p].print_played_cards()
        for p in range(4):
            print  "*" if p == self.dealer else "-", p, ":", self.players[p]
        

    def play_game(self):
        remaining_card_num = sum([len(v) for v in self.players[self.dealer].hands.values()])
        while remaining_card_num:
            self.play_round()
            remaining_card_num = sum([len(v) for v in self.players[self.dealer].hands.values()])

        

def main():
    g = GameMaster(2)
    g.deal_cards()
    g.play_game()


if __name__ == "__main__":
    main()




        
        
        

	
	
