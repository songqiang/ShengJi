#! /bin/python

import sys
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

class Player:
    def __init__(self):
        self.hands = dict({"S":list(), "D":list(), "H":list(),
                           "C":list(), "Z":list()})
        self.playedcards = list()

    def receive_card(self, card, game):
        if card.suit in ["S", "D", "H", "C"] and card.number != game.level: 
            self.hands[card.suit].append(card)
            self.hands[card.suit].sort(key = lambda c: c.number)
            if len(self.hands[card.suit]) >= 6 \
                and Card(card.suit, game.level) in self.hands["Z"]:
                game.set_trump(Card(card.suit, game.level))
        else:
            self.hands["Z"].append(card)
            self.hands["Z"].sort(key = lambda c: c.number)

    def remove_card(self, card, game):
        if card.number == game.level or card.suit == "J":
            self.hands["Z"].remove(card)
        else:
            self.hands[card.suit].remove(card)
            
    def play_card_first(self, game):
        var = raw_input("Which card to play (First play: enter to delegate): ")
        if var:
            card = Card().construct_from_str(var)
            self.playedcards.append([card])
            self.remove_card(card, game)
            return
            
        for suit in ["H", "S", "C", "D"]:
            if game.trump != suit and self.hands[suit] \
                and self.hands[suit][-1].number >= 11:
                self.playedcards.append([self.hands[suit][-1]])
                del self.hands[suit][-1]
                return 

        if self.hands[game.trump]:
            self.playedcards.append([self.hands[game.trump][0]])
            del self.hands[game.trump][0]
            return 

        if self.hands["Z"]:
            self.playedcards.append([self.hands["Z"][0]])
            del self.hands["Z"][0]
            return 

        for suit in ["H", "S", "C", "D"]:
            if game.trump != suit and self.hands[suit]:
                self.playedcards.append([self.hands[suit][0]])
                del self.hands[suit][0]
                return 
        
    def play_card_second(self, game):
        var = raw_input("Which card to play (enter to delegate): ")
        if var:
            card = Card().construct_from_str(var)
            self.playedcards.append([card])
            self.remove_card(card, game)

        last_card = game.players[game.last_player].playedcards[-1][0]
        if last_card.suit == "J" or last_card.suit == game.trump \
            or last_card.number == game.level:

            best = Card("Z", -1)
            worst = Card("Z", 15)

            if self.hands["Z"]:
                best = self.hands["Z"][0]
                worst = self.hands["Z"][0]
            elif self.hands[game.trump]:
                best = self.hands[game.trump][0]
                worst = self.hands[game.trump][0]
                
            if best.number != -1:
                for card in self.hands["Z"]:
                    if game.cmp_card(card, best):
                        best = card
                    if game.cmp_card(worst, card):
                        worst = card
                if not game.cmp_card(last_card, best):
                    self.playedcards.append([best])
                    self.remove_card(best, game)
                else:
                    self.playedcards.append([worst])
                    self.remove_card(worst, game)
            else:
                for cards in self.hands.values():
                    for c in cards:
                        if worst.number > c.number:
                            worst = c
                self.playedcards.append([worst])
                self.remove_card(worst, game)
        else:
            if self.hands[last_card.suit]:
                card = self.hands[last_card.suit][-1] if not game.cmp_card(last_card, self.hands[last_card.suit][-1]) else self.hands[last_card.suit][0]
                self.playedcards.append([card])
                self.remove_card(card, game)
            elif self.hands[game.trump]:
                card = self.hands[game.trump][0]
                self.playedcards.append([card])
                self.remove_card(card, game)
            elif self.hands["Z"]:
                card = self.hands["Z"][0]
                self.playedcards.append([card])
                self.remove_card(card, game)
            else:
                worst = Card("Z", 15)
                for cards in self.hands.values():
                    for c in cards:
                        if worst.number > c.number:
                            worst = c
                self.playedcards.append([worst])
                self.remove_card(worst, game)

    def play_card_third(self, game):
        var = raw_input("Which card to play (enter to delegate): ")
        if var:
            card = Card().construct_from_str(var)
            self.playedcards.append([card])
            self.remove_card(card, game)

        last_card = game.players[game.last_player].playedcards[-1][0]
        if last_card.suit == "J" or last_card.suit == game.trump \
            or last_card.number == game.level:

            best = Card("Z", -1)
            worst = Card("Z", 15)

            if self.hands["Z"]:
                best = self.hands["Z"][0]
                worst = self.hands["Z"][0]
            elif self.hands[game.trump]:
                best = self.hands[game.trump][0]
                worst = self.hands[game.trump][0]
                
            if best.number != -1:
                for card in self.hands["Z"]:
                    if game.cmp_card(card, best):
                        best = card
                    if game.cmp_card(worst, card):
                        worst = card
                if not game.cmp_card(last_card, best):
                    self.playedcards.append([best])
                    self.remove_card(best, game)
                else:
                    self.playedcards.append([worst])
                    self.remove_card(worst, game)
            else:
                for cards in self.hands.values():
                    for c in cards:
                        if worst.number > c.number:
                            worst = c
                self.playedcards.append([worst])
                self.remove_card(worst, game)
        else:
            if self.hands[last_card.suit]:
                card = self.hands[last_card.suit][-1] if not game.cmp_card(last_card, self.hands[last_card.suit][-1]) else self.hands[last_card.suit][0]
                self.playedcards.append([card])
                self.remove_card(card, game)
            elif self.hands[game.trump]:
                card = self.hands[game.trump][0]
                self.playedcards.append([card])
                self.remove_card(card, game)
            elif self.hands["Z"]:
                card = self.hands["Z"][0]
                self.playedcards.append([card])
                self.remove_card(card, game)
            else:
                worst = Card("Z", 15)
                for cards in self.hands.values():
                    for c in cards:
                        if worst.number > c.number:
                            worst = c
                self.playedcards.append([worst])
                self.remove_card(worst, game)
                
    def play_card_fourth(self, game):
        var = raw_input("Which card to play (enter to delegate): ")
        if var:
            card = Card().construct_from_str(var)
            self.playedcards.append([card])
            self.remove_card(card, game)

        last_card = game.players[game.last_player].playedcards[-1][0]
        if last_card.suit == "J" or last_card.suit == game.trump \
            or last_card.number == game.level:

            best = Card("Z", -1)
            worst = Card("Z", 15)

            if self.hands["Z"]:
                best = self.hands["Z"][0]
                worst = self.hands["Z"][0]
            elif self.hands[game.trump]:
                best = self.hands[game.trump][0]
                worst = self.hands[game.trump][0]
                
            if best.number != -1:
                for card in self.hands["Z"]:
                    if game.cmp_card(card, best):
                        best = card
                    if game.cmp_card(worst, card):
                        worst = card
                if not game.cmp_card(last_card, best):
                    self.playedcards.append([best])
                    self.remove_card(best, game)
                else:
                    self.playedcards.append([worst])
                    self.remove_card(worst, game)
            else:
                for cards in self.hands.values():
                    for c in cards:
                        if worst.number > c.number:
                            worst = c
                self.playedcards.append([worst])
                self.remove_card(worst, game)
        else:
            if self.hands[last_card.suit]:
                card = self.hands[last_card.suit][-1] if not game.cmp_card(last_card, self.hands[last_card.suit][-1]) else self.hands[last_card.suit][0]
                self.playedcards.append([card])
                self.remove_card(card, game)
            elif self.hands[game.trump]:
                card = self.hands[game.trump][0]
                self.playedcards.append([card])
                self.remove_card(card, game)
            elif self.hands["Z"]:
                card = self.hands["Z"][0]
                self.playedcards.append([card])
                self.remove_card(card, game)
            else:
                worst = Card("Z", 15)
                for cards in self.hands.values():
                    for c in cards:
                        if worst.number > c.number:
                            worst = c
                self.playedcards.append([worst])
                self.remove_card(worst, game)
                
    def __str__(self):
        s = ""
        for v in self.hands.values():
            if v: s += ", ".join([str(e) for e in v]) + "; "
        return s

    def print_hands(self):
        s = ""
        for v in self.hands.values():
            if v: s += ", ".join([str(e) for e in v]) + "\n"
        print s

    def print_played_cards(self):
        print ", ".join(["|".join([str(e) for e in v]) for v in self.playedcards])

class Game:
    def __init__(self, level):
        """initialize game
        Arguments:
        - `self`:
        """
        self.carddeck = CardDeck(2)
        self.players = [Player() for i in range(4)]
        self.level = level
        self.dealer = 0
        self.last_player = -1
        self.trump = "Z"
        self.trump_card = None
        self.oddscore = 0
        self.evenscore = 0

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
        
    def cmp_card(self, card1, card2):
        """
        compare cards taking into accoutn of zhu
        """
        if self.trump != "Z":
            if card1.suit == "J":
                return True if card2.suit != "J" else card1.number >= card2.number
            if card2.suit == "J": return False

            if card1.number == self.level:
                return True if card2.level != self.level else (card1.suit == self.trump or not card2.suit == self.trump)
            if card2.number == self.level: return False

            if card1.suit == self.trump:
                return True if card2.suit != self.trump else card1.number >= card2.number
            if card2.suit == self.trump: return False

            return True if card1.suit != card2.suit else card1.number >= card2.number
        else:  # WU ZHU
            if card1.suit == "J":
                return True if card1.suit != "J" else card1.number >= card2.number
            if card2.suit == "J": return False
            if card1.number == self.level: return True
            if card2.number == self.level: return False
            return True if card1.suit != card2.suit else card1.number >= card2.number
            
    def play_round(self):
        self.players[self.dealer].play_card_first(self)
        self.last_player = self.dealer

        self.players[(self.dealer + 1) % 4].play_card_second(self)
        self.last_player = (self.dealer + 1) % 4

        self.players[(self.dealer + 2) % 4].play_card_second(self)
        self.last_player = (self.dealer + 2) % 4

        self.players[(self.dealer + 3) % 4].play_card_second(self)
        self.last_player = (self.dealer + 3) % 4
        
        self.last_player = -1
            
        ## determine winner
        winner = self.dealer
        score = self.players[winner].playedcards[-1][0].get_score()
        for p in range(self.dealer + 1, self.dealer + 4):
            score += self.players[p % 4].playedcards[-1][0].get_score()
            if not self.cmp_card(self.players[winner].playedcards[-1][0], self.players[p % 4].playedcards[-1][0]):
                winner = p % 4
        
        if winner % 2 == 0:
            self.evenscore += score
        else:
            self.oddscore += score
        self.dealer = winner % 4

        print "Winner={:d}, N/S={:d}, E/W={:d}".format(self.dealer, 
                                                       self.oddscore,
                                                       self.evenscore) 
        for p in range(self.dealer, self.dealer + 4):
            print p%4, ":", self.players[p % 4]
        for p in range(self.dealer, self.dealer + 4):
            sys.stdout.write(str(p%4) + ": ")
            self.players[p % 4].print_played_cards()
        

    def play_game(self):
        while self.players[self.dealer].hands:
            self.play_round()
        

def main():
    g = Game(2)
    g.deal_cards()
    g.play_game()


if __name__ == "__main__":
    main()




        
        
        

	
	
