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

    def has_better_card_single(self, card, game):
        if (card.suit == game.trump or card.number == game.level): 
            if self.hands["Z"]:
                for c in self.hands["Z"]:
                    if not game.cmp_card_single(card, c):
                        return True
        else:
            if self.hands[card.suit] \
              and not game.cmp_card_single(card, self.hands[card.suit][-1]):
                return True
        return False

    def has_better_card_pair(self, cards, game):
        if (cards[0].suit == game.trump or cards[0].number == game.level): 
            if self.hands["Z"]:
                for i in range(len(self.hands["Z"]) - 1):
                    if self.hands["Z"][i].is_pair(self.hands["Z"][i+1]) and \
                        not game.cmp_card(cards[0], self.hands["Z"][i]):
                        return True
        else:
            if self.hands[cards[0].suit]: 
                for i in range(len(self.hands[cards[0].suit]) - 1):
                    if self.hands[cards[0].suit][i].is_pair(self.hands[cards[0].suit][i+1]) and \
                        not game.cmp_card(cards[0], self.hands[cards[0].suit][i]):
                        return True
        return False

    def has_better_card_tuolaji(self, cards, game):
        if (cards[0].suit == game.trump or cards[0].number == game.level): 
            print "NOT IMPLEMENTED YET"
        else:
            if self.hands[cards[0].suit]: 
                for i in range(len(self.hands[cards[0].suit]) - 3):
                    if game.is_tuolaji(self.hands[cards[0].suit][i:(i+4)]) and \
                        not game.cmp_card(cards[0], self.hands[cards[0].suit][i]):
                        return True
        return False

    def has_better_card(self, cards, game):
        cards.sort()
        i = 0
        while i < len(cards):
            if game.is_pair(cards[i:(i+2)]):
                if game.is_tuolaji(cards[i:(i+4)]):
                    if self.has_better_card_tuolaji(cards[i:(i+4)], game):
                        return True
                    else:
                        i += 4
                elif self.has_better_card_pair(cards[i:(i+2)], game):
                    return True
                else:
                    i += 2
            elif self.has_better_card_single(cards[i], game):
                return True
            else:
                i += 1
        return False
                    
    def play_card(self, card, game):
        self.playedcards.append([card])
        if card.number == game.level or card.suit == "J":
            self.hands["Z"].remove(card)
        else:
            self.hands[card.suit].remove(card)
            
    def play_card_first(self, game):
        var = raw_input("Which card to play (First play: enter to delegate): ")
        if var:
            card = Card().construct_from_str(var)
            self.play_card(card, game)
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
            self.play_card(card, game)
            return

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
                    if game.cmp_card_single(card, best):
                        best = card
                    if game.cmp_card_single(worst, card):
                        worst = card
                if not game.cmp_card_single(last_card, best):
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
                card = self.hands[last_card.suit][-1] if not game.cmp_card_single(last_card, self.hands[last_card.suit][-1]) else self.hands[last_card.suit][0]
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
            self.play_card(card, game)
            return

        dealer_card = game.players[game.dealer].playedcards[-1][0] 
        prev_card = game.players[game.last_player].playedcards[-1][0]
        if dealer_card.suit == "J" or dealer_card.suit == game.trump \
            or dealer_card.number == game.level:

            if self.hands["Z"] or self.hands[self.trump]:
                ## dealer wants to score
                if game.cmp_card(dealer_card, prev_card):
                    if dealer_card.suit == "J" \
                        or dealer_card.number == self.level \
                        or dealer_card.number >= 10:
                        # add more score
                        score_5_cards = [card for card in self.hands["Z"] \
                                       + self.hands[self.trump] \
                                       if card.number == 5]
                        score_10_cards = [card for card in self.hands["Z"] \
                                       + self.hands[self.trump] \
                                       if card.number == 10]
                        score_K_cards = [card for card in self.hands["Z"] \
                                       + self.hands[self.trump] \
                                       if card.number == 13]

                        score_card = score_10_cards[0] if score_10_cards else (score_K_cards[0] if score_K_cards else score_5_cards[0])
                        self.play_card(score_card, game)
                        return
                        
                ## dealer wants to turn over control   
                best_card = Card("Z", -1)
                worst_card = Card("Z", 15)

                if self.hands["Z"]:
                    best_card = self.hands["Z"][0]
                    worst_card = self.hands["Z"][0]
                elif self.hands[game.trump]:
                    best_card = self.hands[game.trump][0]
                    worst_card = self.hands[game.trump][0]
                
                for card in self.hands["Z"]:
                    if game.cmp_card(card, best_card):
                        best_card = card
                    if game.cmp_card(worst_card, card):
                        worst_card = card

                if not game.cmp_card(prev_card, best_card):
                    self.playedcards.append([best_card])
                    self.remove_card(best_card, game)
                else:
                    self.playedcards.append([worst_card])
                    self.remove_card(worst_card, game)
            else:
                ## dealer wants to score
                if game.cmp_card(dealer_card, prev_card):
                    if dealer_card.suit == "J" \
                        or dealer_card.number == self.level \
                        or dealer_card.number >= 10:
                        # add more score
                        score_5_cards = [card for card in self.hands["H"] \
                                       + self.hands["S"] + self.hands["C"] \
                                       + self.hands["D"] if card.number == 5]
                        score_10_cards = [card for card in self.hands["H"] \
                                       + self.hands["S"] + self.hands["C"] \
                                       + self.hands["D"] if card.number == 10]
                        score_K_cards = [card for card in self.hands["H"] \
                                       + self.hands["S"] + self.hands["C"] \
                                       + self.hands["D"] if card.number == 13]

                        score_card = score_10_cards[0] if score_10_cards else (score_K_cards[0] if score_K_cards else score_5_cards[0])
                        self.play_card(score_card, game)
                        return

                for cards in self.hands.values():
                    for c in cards:
                        if worst.number > c.number:
                            worst = c
                self.playedcards.append([worst])
                self.remove_card(worst, game)
        else:
            if self.hands[dealer_card.suit]:
                card = self.hands[dealer_card.suit][-1] if not game.cmp_card(dealer_card, self.hands[dealer_card.suit][-1]) else self.hands[dealer_card.suit][0]
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
            return

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
        return len(cards) == 2 and cards[0] == cards[1]
    
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
        cards1.sort(key = self.get_key)
        cards2.sort(key = self.get_key)
        i = 0
        if self.is_tuolaji(cards1[i:(i+4)]):
            if self.is_tuolaji(cards2[i:(i+4)]):
                return self.cmp_card_tuolaji(cards1[i:(i+4)], cards2[i:(i+4)])
            else:
                return True
        elif self.is_pair(cards1[i:(i+2)]):
            if self.is_pair(cards2[i:(i+2)]): 
                return self.cmp_card_pair(cards1[i:(i+2)], cards2[i:(i+2)])
            else:
                return True
        else:
            return self.cmp_card_single(cards1[i], cards2[i])
        
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

        self.players[(self.dealer + 2) % 4].play_card_second(self)
        self.last_player = (self.dealer + 2) % 4

        self.players[(self.dealer + 3) % 4].play_card_second(self)
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




        
        
        

	
	
