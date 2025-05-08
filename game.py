import pygame
import random

JESTER = 0
ACE = 1
JACK = 11
QUEEN = 12
KING = 13
WIZARD = 14

card_dict = {JESTER: "JESTER",
             ACE:    "ACE",
             JACK:   "JACK",
             QUEEN:  "QUEEN",
             KING:   "KING",
             WIZARD: "WIZARD",
             2:  "2",
             3:  "3",
             4:  "4",
             5:  "5",
             6:  "6",
             7:  "7",
             8:  "8",
             9:  "9",
             10: "10"}

suit_dict = {0: "CLUB",
             1: "SPADE",
             2: "HEART",
             3: "DIAMOND"}

class Game:
    def __init__(self, players):
        self.players = players
        self.num_players = 4
        self.player_hands = []
        self.deck = []
        self.init_deck()
        self.print_cards(self.deck)
        self.round = 1
        self.num_rounds = 60 // self.num_players
        self.simulate_game()

    def deal(self):
        card_idx = 0
        random.shuffle(self.deck)
        for i in range(self.num_players):
            self.player_hands.append([])
        while card_idx < self.num_players*self.round:
            self.player_hands[card_idx % self.num_players].append(self.deck[card_idx])
            card_idx += 1

    def init_deck(self):
        for i in range(0, 15):
            for k in range(4):
                card = Card(i, k, None)
                self.deck.append(card)

    def execute_round(self):
        self.player_hands = []
        self.deal()
        i = 1
        for hand in self.player_hands:
            print(f"PLAYER {i}:")
            self.print_cards(hand)
            i += 1

    def simulate_game(self):
        for i in range(1, self.num_rounds + 1):
            print(f"************ROUND {i}************")
            self.execute_round()
            self.round += 1

# for the sake of debugging
    def print_cards(self, cards):
        for c in cards:
            print("\t", c.to_string())

class Card:
    def __init__(self, ID, suit, image):
        self.ID = ID
        self.suit = suit
        self.image = image

    def to_string(self): # for debugging
        return f"ID = {card_dict[self.ID]} suit = {suit_dict[self.suit]}"

class Player:
    def __init__(self, ID, cli_sock):
        self.ID = ID
        self.cli_sock = cli_sock
        print("implement Player")
