import random

JESTER = 0
ACE = 1
JACK = 11
QUEEN = 12
KING = 13
WIZARD = 14

card_dict = {JESTER: "jester",
             ACE:    "ace",
             2:  "2",
             3:  "3",
             4:  "4",
             5:  "5",
             6:  "6",
             7:  "7",
             8:  "8",
             9:  "9",
             10: "10",
             JACK: "jack",
             QUEEN: "queen",
             KING: "king",
             WIZARD: "wizard",
             }

suit_dict = {0: "clubs",
             1: "spades",
             2: "hearts",
             3: "diamonds"}


class Deck:
    def __init__(self, players):
        self.players = players
        self.num_players = len(players)
        self.deck = []
        self.init_deck()
        self.round = 0
        self.num_rounds = 60 // self.num_players
        self.hands = {player: [] for player in players}
        self.trump_card = []

    def deal(self):
        self.hands = {player: [] for player in self.players}
        self.round += 1
        random.shuffle(self.deck)
        total_cards = self.round * self.num_players
        for i in range(total_cards):
            card = self.deck[i]
            player = self.players[i % self.num_players]
            self.hands[player].append(card)
        if total_cards < len(self.deck):
            self.trump_card = self.deck[total_cards]
        else:
            self.trump_card = None


    def init_deck(self):
        for i in range(0, 15):
            for k in range(4):
                card = Card(i, k)
                self.deck.append(card)


class Card:
    def __init__(self, ID, suit):
        self.ID = ID
        self.suit = suit
        if ID == 0:
            self.image = "assets/cards/jester.png"
        elif ID == 14:
            self.image = "assets/cards/wizard.png"
        else:
            self.image = f"assets/cards/{card_dict[ID]}_of_{suit_dict[suit]}.png"
