import ast
import sys
import pygame
from typing import Optional
from scenes import init_gui
from deck import Deck, Card

screen: Optional[pygame.Surface] = None
font: Optional[pygame.font.Font] = None
width: Optional[int] = None
height: Optional[int] = None
size = None
bidding_phase = True
bid_input = ''


def draw_server_screen(player_index, hand, trump_card):
    global bidding_phase
    screen.fill((0, 128, 0))
    draw_hand(hand, trump_card)

    if bidding_phase and player_index == 0:
        draw_bidding_phase()
    else:
        idle_message = font.render("Waiting For Players to Bid...", True, (0, 0, 0))
        screen.blit(idle_message, ((width / 2 - 300), (height / 4 - 100)))

    pygame.display.flip()


def draw_client_screen(client, hand, trump_card):
    global bidding_phase
    screen.fill((0, 128, 0))
    draw_hand(hand, trump_card)

    client.send("bid?")
    data = client.receive()
    if data == "yes":
        bidding_phase = True
        draw_bidding_phase()
    else:
        idle_message = font.render("Waiting For Players to Bid...", True, (0, 0, 0))
        screen.blit(idle_message, ((width / 2 - 300), (height / 4 - 100)))

    pygame.display.flip()


def draw_bidding_phase():
    rect1 = pygame.Rect((width / 2 - 270), (height / 4 - 100), 540, 200)
    text_box = pygame.Rect((width / 2 - 250), (height / 4 - 30), 500, 100)
    pygame.draw.rect(screen, (187, 187, 187), rect1)
    pygame.draw.rect(screen, (238, 238, 238), text_box)

    # Draw text input
    text_caption = font.render("Enter Your Bid Below:", True, (0, 0, 0))
    screen.blit(text_caption, ((width / 2 - 255), (height / 4 - 100)))
    input_surface = font.render(bid_input, True, (0, 0, 0))
    screen.blit(input_surface, (text_box.x + 10, text_box.y + 30))


def create_host_game(server):
    global screen, font, width, height, size, bidding_phase, bid_input
    screen, font, width, height, size = init_gui(screen, font, width, height, size)

    server.initialize_hands()
    player_index = 0 #random.randint(0, len(server.connected_clients))
    deck = Deck([server, *server.connected_clients])

    deck.deal()
    server_hand = [(card.ID, card.suit) for card in deck.hands[server]]
    if player_index == 0:
        server.current_player = server
    else:
        server.current_player = server.connected_clients[player_index - 1]

    server.trump_card = deck.trump_card
    print(server.trump_card)
    server.setup_hands(deck)

    server.player_bids = [-1] * (len(server.connected_clients) + 1)

    while True:
        if server.all_bid:  # Ends bidding phase
            print("TODO")
            # TODO: This is where we will actually start gameplay

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif bidding_phase and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if bid_input.strip() != '':
                        server.player_bids[player_index] = bid_input
                        bid_input = ''
                        if player_index + 1 == len(server.player_bids):
                            player_index = 0
                        else:
                            player_index += 1

                        if player_index == 0:
                            server.current_player = server
                        else:
                            server.current_player = server.connected_clients[player_index - 1]

                elif event.key == pygame.K_BACKSPACE:
                    bid_input = bid_input[:-1]
                else:
                    if event.unicode.isprintable():
                        bid_input += event.unicode

        draw_server_screen(player_index, server_hand, server.trump_card)


def create_client_game(client):
    global screen, font, width, height, size, bid_input, bidding_phase
    screen, font, width, height, size = init_gui(screen, font, width, height, size)
    dealt_cards, bidding_phase = False, False
    trump_card = None

    while True:
        if not dealt_cards:
            client.send("hand-please")
            client.hand = ast.literal_eval(client.receive())  # Converts string to int safely

            client.send("trump-card")
            trump_data = ast.literal_eval(client.receive())
            trump_card = Card(trump_data[0], trump_data[1])
            dealt_cards = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif bidding_phase and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if bid_input.strip() != '':
                        client.send(f"Bid is: {bid_input}")
                        bid_input = ''
                        bidding_phase = False
                elif event.key == pygame.K_BACKSPACE:
                    bid_input = bid_input[:-1]

                else:
                    # Add this to handle regular typing input
                    if event.unicode.isprintable():
                        bid_input += event.unicode

        draw_client_screen(client, client.hand, trump_card)


def draw_hand(hand, trump_card):
    spacing = 80

    # Draw Trump Card
    trump = Card(trump_card.ID, trump_card.suit)
    trump_pic = pygame.image.load(trump.image)
    trump_pic = pygame.transform.scale(trump_pic, (200, 400))
    screen.blit(trump_pic, (width - 250, 50))

    for i, (ID, suit) in enumerate(hand):
        card = Card(ID, suit)
        try:
            card_pic = pygame.image.load(card.image)
            card_pic = pygame.transform.scale(card_pic, (200, 400))
            screen.blit(card_pic, (50 + i * spacing, 600))
        except pygame.error as e:
            print(f"Failed to load image for card ({ID}, {suit}): {e}")
