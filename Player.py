#!/bin/python
#
# Chisne ShengJi card game
# Song, Qiang <keeyang@ustc.edu>
#
# player action and player strategies

from Card import Card

class Player:
    def __init__(self, _id = 0):
        self.hands = dict({"S":list(), "D":list(), "H":list(),
                           "C":list(), "Z":list()})
        self.playedcards = list()
        self.id = _id;

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
        var = raw_input("Player {:d} Which card to play (First play: enter to delegate): ".format(self.id))
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
        var = raw_input("Player {:d} Which card to play (enter to delegate): ".format(self.id))
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
        var = raw_input("Player {:d} Which card to play (enter to delegate): ".format(self.id))
        if var:
            card = Card().construct_from_str(var)
            self.play_card(card, game)
            return

        dealer_card = game.players[game.dealer].playedcards[-1][0] 
        prev_card = game.players[game.last_player].playedcards[-1][0]
        if dealer_card.suit == "J" or dealer_card.suit == game.trump \
            or dealer_card.number == game.level:

            if self.hands["Z"] or self.hands[game.trump]:
                ## dealer wants to score
                if game.cmp_card_single(dealer_card, prev_card):
                    if dealer_card.suit == "J" \
                        or dealer_card.number == game.level \
                        or dealer_card.number >= 10:
                        # add more score
                        score_5_cards = [card for card in self.hands["Z"] \
                                       + self.hands[game.trump] \
                                       if card.number == 5]
                        score_10_cards = [card for card in self.hands["Z"] \
                                       + self.hands[game.trump] \
                                       if card.number == 10]
                        score_K_cards = [card for card in self.hands["Z"] \
                                       + self.hands[game.trump] \
                                       if card.number == 13]
                        if score_5_cards or score_10_cards or score_K_cards:
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
                    if game.cmp_card_single(card, best_card):
                        best_card = card
                    if game.cmp_card([worst_card], [card]):
                        worst_card = card

                if not game.cmp_card([prev_card], [best_card]):
                    self.playedcards.append([best_card])
                    self.remove_card(best_card, game)
                else:
                    self.playedcards.append([worst_card])
                    self.remove_card(worst_card, game)
            else:
                ## dealer wants to score
                if game.cmp_card([dealer_card], [prev_card]):
                    if dealer_card.suit == "J" \
                        or dealer_card.number == game.level \
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
                        
                worst_card = Card("Z", 15)
                for cards in self.hands.values():
                    for c in cards:
                        if worst_card.number > c.number:
                            worst_card = c
                self.playedcards.append([worst_card])
                self.remove_card(worst_card, game)
        else:
            if self.hands[dealer_card.suit]:
                card = self.hands[dealer_card.suit][-1] if not game.cmp_card_single(dealer_card, self.hands[dealer_card.suit][-1]) else self.hands[dealer_card.suit][0]
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
        var = raw_input("Player {:d} Which card to play (enter to delegate): ".format(self.id))
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
                    if game.cmp_card([card], [best]):
                        best = card
                    if game.cmp_card([worst], [card]):
                        worst = card
                if not game.cmp_card([last_card], [best]):
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



