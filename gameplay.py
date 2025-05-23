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
phase = "bidding"
taken_turn = False
bid_input = ''
num_players = 0


def draw_server_screen(server, hand, trump_card, played_cards, points):
    global phase

    # bg image setup
    background_image = pygame.image.load("assets/waiting_room.png")  # Replace with your filename
    background_scaled = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))
    screen.blit(background_scaled, (0, 0))

    draw_hand(hand, trump_card, 500)
    draw_hand(played_cards, None, 70)
    draw_points(server.points)
    draw_player_bids(server.player_bids, server.tricks_taken)

    if phase == "bidding" and server.current_player == server:
        draw_bidding_phase()
    elif phase == "players_bidding" or phase == "bidding":
        idle_message = font.render("Waiting For Players to Bid...", True, (0, 0, 0))
        screen.blit(idle_message, ((screen.get_width() / 2 - 300), (screen.get_height() / 4 - 100)))

    your_cards_msg = font.render("Your Cards:", True, (0, 0, 0))
    screen.blit(your_cards_msg, (45, 430))

    pygame.display.flip()


def draw_client_screen(client, hand, trump_card, played_cards, points):
    global phase

    # bg image setup
    background_image = pygame.image.load("assets/waiting_room.png")  # Replace with your filename
    background_scaled = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))
    screen.blit(background_scaled, (0, 0))

    draw_hand(hand, trump_card, 500)
    draw_points(client.points)
    draw_player_bids(client.player_bids, client.tricks_taken)

    if played_cards is not []:
        draw_hand(played_cards, None, 70)

    if phase == "bidding":
        client.send("bid?")
        data = client.receive()
        if data == "yes":
            draw_bidding_phase()
        else:
            idle_message = font.render("Waiting For Players to Bid...", True, (0, 0, 0))
            screen.blit(idle_message, ((screen.get_width() / 2 - 300), (screen.get_height() / 4 - 100)))

    your_cards_msg = font.render("Your Cards:", True, (0, 0, 0))
    screen.blit(your_cards_msg, (45, 430))

    pygame.display.flip()


def draw_points(points):
    points_caption = font.render(f"Points: {points}", True, (255, 255, 255))
    screen.blit(points_caption, (10, screen.get_height() - points_caption.get_height()))


def draw_player_bids(player_bids, tricks_taken):

    for i in range(len(player_bids)):
        bid_caption = font.render(f"Player {i + 1}:", True, (255, 255, 255))
        if player_bids[i] == -1:
            total_bids = font.render(f"{tricks_taken[i]} / ?", True, (255, 255, 255))
        else:
            total_bids = font.render(f"{tricks_taken[i]} / {player_bids[i]}", True, (255, 255, 255))
        screen.blit(bid_caption, (340 + (i*275), screen.get_height() - 120))
        screen.blit(total_bids, (340 + (i*275), screen.get_height() - 60))


def draw_bidding_phase():
    rect1 = pygame.Rect((screen.get_width() / 2 - 270), (screen.get_height() / 4 - 110), 540, 205)
    text_box = pygame.Rect((screen.get_width() / 2 - 250), (screen.get_height() / 4 - 30), 500, 100)
    pygame.draw.rect(screen, (187, 187, 187), rect1)
    pygame.draw.rect(screen, (238, 238, 238), text_box)

    # Draw text input
    text_caption = font.render("Enter Your Bid:", True, (0, 0, 0))
    screen.blit(text_caption, ((screen.get_width() / 2 - 255), (screen.get_height() / 4 - 100)))
    input_surface = font.render(bid_input, True, (0, 0, 0))
    screen.blit(input_surface, (text_box.x + 10, text_box.y + 30))


def create_host_game(server):
    global screen, font, width, height, size, phase, bid_input, taken_turn, num_players
    screen, font, width, height, size = init_gui(screen, font, width, height, size)
    num_players = len(server.connected_clients) + 1
    server.current_player = server
    server.player_points = [0] * (len(server.connected_clients) + 1)
    #server.num_rounds = 60 / (len(server.connected_clients) + 1)
    server.num_rounds = 2
    deck = Deck([server, *server.connected_clients])

    server_hand = start_round(server, deck)

    while True:
        if server.num_rounds < server.cur_round:
            server.game_over = True
            if max(server.player_points) == server.player_points[0]:
                handle_win()
                continue
            else:
                handle_lose()
                continue

        if phase == "players_bidding":
            if server.check_bids():
                phase = "game"

        if phase == "game":
            if server.current_player == server and not taken_turn:  # Server's turn
                draw_server_screen(server, server_hand, server.trump_card, server.played_cards, server.points)
                turn_msg = font.render("Please Select A Card", True, (0, 0, 0))
                screen.blit(turn_msg, (screen.get_width() / 2 - 250, 300))
                pygame.display.flip()
                card = choose_card(server_hand, server.played_cards)
                server.adjust_played_cards(card, server.current_player)
                server_hand.remove(card)
                taken_turn = True
                if server.check_all_went():  # Round ended
                    end_of_trick(server, deck, server_hand)
                else:
                    server.next_player()

            elif server.check_all_went():  # Round ended
                turn_msg = font.render("Waiting for Players...", True, (0, 0, 0))
                screen.blit(turn_msg, (screen.get_width() / 2 - 240, 300))
                pygame.display.flip()
                end_of_trick(server, deck, server_hand)

        check_server_inputs(server)
        draw_server_screen(server, server_hand, server.trump_card, server.played_cards, server.points)


def create_client_game(client):
    global screen, font, width, height, size, bid_input, phase, num_players
    screen, font, width, height, size = init_gui(screen, font, width, height, size)
    trump_card = None
    client.send("num_players?")
    num_players = ast.literal_eval(client.receive())

    while True:
        client.send("new-round?")
        response = client.receive()
        if response == "win":
            handle_win()
            continue
        if response == "lose":
            handle_lose()
            continue

        client.send("player-bids?")
        data = ast.literal_eval(client.receive())
        client.player_bids = data["player_bids"]
        client.tricks_taken = data["tricks_taken"]
        client.points = data["points"]

        if response == "yes":
            phase = "bidding"
            client.send("start-round")
            hand_and_trump = ast.literal_eval(client.receive())
            client.hand = hand_and_trump["hand"]
            trump_card = Card(*hand_and_trump["trump"])
            client.played_cards = hand_and_trump["played_cards"]

        check_client_inputs(client)

        if phase == "game":
            response = client.get_client_game_info()
            draw_client_screen(client, client.hand, trump_card, client.played_cards, client.points)
            pygame.display.flip()

            if response == "yes":
                turn_msg = font.render("Please Select A Card", True, (0, 0, 0))
                screen.blit(turn_msg, (screen.get_width() / 2 - 250, 300))
                pygame.display.flip()
                card = choose_card(client.hand, client.played_cards)
                client.send(f"new-played {card}")
                client.hand.remove(card)
                draw_client_screen(client, client.hand, trump_card, client.played_cards, client.points)
                pygame.display.flip()

            elif response == "no":
                draw_client_screen(client, client.hand, trump_card, client.played_cards, client.points)
                #turn_msg = font.render("Waiting for Players...", True, (0, 0, 0))

                #screen.blit(turn_msg, (screen.get_width() / 2 - 240, 300))
                pygame.display.flip()

        else:
            draw_client_screen(client, client.hand, trump_card, client.played_cards, client.points)
            pygame.display.flip()


def start_round(server, deck):
    deck.deal()
    server.initialize_hands()

    server_hand = [(card.ID, card.suit) for card in deck.hands[server]]

    server.trump_card = deck.trump_card
    server.setup_hands(deck)
    server.cur_round += 1

    return server_hand


def check_server_inputs(server):
    global bid_input, phase
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif phase == "bidding" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if bid_input.strip() != '':
                    server.player_bids[0] = bid_input
                    bid_input = ''
                    phase = "players_bidding"
                    server.next_player()
                    server.signal_new_round = False

            elif event.key == pygame.K_BACKSPACE:
                bid_input = bid_input[:-1]
            else:
                if event.unicode.isprintable():
                    bid_input += event.unicode


def check_client_inputs(client):
    global phase, bid_input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif phase == "bidding" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if bid_input.strip() != '':
                    client.send(f"Bid is: {bid_input}")
                    bid_input = ''
                    phase = "game"
            elif event.key == pygame.K_BACKSPACE:
                bid_input = bid_input[:-1]

            else:
                # Add this to handle regular typing input
                if event.unicode.isprintable():
                    bid_input += event.unicode


def choose_card(hand, played_cards):
    spacing = 160
    card_width = 150
    card_height = 300
    card_rects = []

    for i in range(len(hand)):
        if i > 9:
            card_x = 50 + (i - 10) * spacing
            card_y = 910
        else:
            card_x = 50 + i * spacing
            card_y = 600
        rect = pygame.Rect(card_x, card_y, card_width, card_height)
        card_rects.append(rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                for i, rect in enumerate(card_rects):
                    if rect.collidepoint(mouse_x, mouse_y):
                        selected_card = hand[i]
                        if is_valid_play(selected_card, hand, played_cards):
                            return selected_card
                        else:
                            print("Invalid play: You must follow suit!")


def draw_hand(hand, trump_card, y_pos):
    spacing = 160

    if trump_card is not None:
        # Draw Trump Card
        trump_caption = font.render("Trump:", True, (0, 0, 0))
        screen.blit(trump_caption, (screen.get_width() - 240, 0))
        trump = Card(trump_card.ID, trump_card.suit)
        trump_pic = pygame.image.load(trump.image)
        trump_pic = pygame.transform.scale(trump_pic, (150, 300))
        screen.blit(trump_pic, (screen.get_width() - 230, screen.get_height() - screen.get_height() + 80))

        # Draw Played_cards (just once so in this one is fine)
        played_caption = font.render("Played Cards:", True, (0, 0, 0))
        screen.blit(played_caption, (50, 0))

    for i, (ID, suit) in enumerate(hand):
        card = Card(ID, suit)
        try:
            card_pic = pygame.image.load(card.image)
            card_pic = pygame.transform.scale(card_pic, (150, 300))
            if i > 9:
                screen.blit(card_pic, (50 + (i - 10) * spacing, y_pos + 310))
            else:
                screen.blit(card_pic, (50 + i * spacing, y_pos))
        except pygame.error as e:
            print(f"Failed to load image for card ({ID}, {suit}): {e}")


def is_valid_play(card_to_play, hand, played_cards):
    card_id, suit_to_play = card_to_play

    # Wizards and Jesters can always be played
    if card_id == 0 or card_id == 14:
        return True

    # No cards played yet -> any card is valid
    if not played_cards or (len(played_cards) == num_players):
        return True

    # If the first card is a wizard, any card can be played
    first_card_id, _ = played_cards[0]
    if first_card_id == 14:
        return True

    lead_suit = None
    for c_id, suit in played_cards:
        if c_id != 0:  # not a jester
            lead_suit = suit
            break

    # If no lead suit could be determined or first card is a jester
    if lead_suit is None:
        return True

    # Check if the player has any cards of the lead suit (excluding jesters/wizards)
    # Looked up best way to do this AS FYI
    has_lead_suit = any(c_id not in (0, 14) and s == lead_suit for c_id, s in hand)

    if has_lead_suit:
        # If the player has a card of the lead suit
        return suit_to_play == lead_suit
    else:
        # If the player doesn't have the lead suit
        return True


def end_of_trick(server, deck, server_hand):
    global phase, taken_turn

    taken_turn = False
    server.prevent_trick = True

    # Get winner index from the played cards
    winner_index = get_round_winner(server.played_cards, server.trump_card.suit)

    # Determine players and the actual turn order of the trick
    winner = server.play_order[winner_index]

    # Increment tricks taken using the index in original player order
    if winner in server.connected_clients:
        client_index = server.connected_clients.index(winner)
        server.tricks_taken[client_index + 1] += 1
    else:
        server.tricks_taken[0] += 1

    # Check if all players have played all their cards (trick phase over)
    if len(server_hand) == 0 and all(len(hand) == 0 for hand in server.client_hands):
        players = [server]
        for c in server.connected_clients:
            players.append(c)
        calculate_scores(server, players)
        phase = "bidding"
        server_hand[:] = start_round(server, deck)

    else:
        # Update current player and clear played cards
        server.current_player = winner


def get_round_winner(played_cards, trump_suit):
    WIZARD = 14
    JESTER = 0
    best_index = -1
    best_card = None
    lead_suit = None

    for index, (card_id, suit) in enumerate(played_cards):
        # First non-jester card sets the lead suit (unless it's a wizard)
        if card_id == JESTER:
            continue
        if lead_suit is None and card_id not in (JESTER, WIZARD):
            lead_suit = suit

        if card_id == WIZARD:
            return index  # First wizard wins

        if best_card is None:
            best_card = (card_id, suit)
            best_index = index
        else:
            _, best_suit = best_card

            # Trump suit beats lead suit
            if suit == trump_suit and best_suit != trump_suit:
                best_card = (card_id, suit)
                best_index = index
            elif suit == best_suit and card_id > best_card[0]:
                best_card = (card_id, suit)
                best_index = index
            # Special condition for aces (we coded aces low on accident, but aces are high)
            elif suit == best_suit and card_id == 1:
                best_card = (card_id, suit)
                best_index = index

    return best_index


def calculate_scores(server, players):
    for p in players:
        player_index = players.index(p)
        diff = int(server.player_bids[player_index]) - int(server.tricks_taken[player_index])
        if diff == 0:
            server.player_points[player_index] += (20 + (int(server.tricks_taken[player_index]) * 10))
        else:
            server.player_points[player_index] -= (10 * abs(diff))
        if p == server:
            p.points = server.player_points[player_index]
    return

def handle_win():
    screen.fill((24, 38, 45))
    btn_font = pygame.font.SysFont("liberationserif", 50, bold=True)

    bg_img = pygame.image.load("assets/win_screen.png")
    bg_img = pygame.transform.scale(bg_img, (screen.get_width(), screen.get_height()))
    screen.blit(bg_img, (0, 0))

    # Draw “Main Menu” button
    btn_w, btn_h = 225, 70
    btn_x = ((screen.get_width() - btn_w) // 2) - 10
    btn_y = screen.get_height() - screen.get_height()//3
    main_btn = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    main_btn_border = pygame.Rect(btn_x - 5, btn_y - 5, btn_w + 10, btn_h + 10)
    pygame.draw.rect(screen, (29, 18, 11), main_btn_border, border_radius=10)      # button bg
    pygame.draw.rect(screen, (161, 96, 37), main_btn, border_radius=10)      # button bg
    btn_txt = btn_font.render("Exit", True, (43, 29, 11))
    screen.blit(btn_txt, (btn_x + (btn_w - btn_txt.get_width())//2,
                          btn_y + (btn_h - btn_txt.get_height())//1.5))
    pygame.display.flip()

    # Wait for click
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if main_btn.collidepoint(ev.pos):
                    pygame.quit()
                    exit()
                    return
def handle_lose():
    screen.fill((24, 38, 45))
    btn_font = pygame.font.SysFont("liberationserif", 50, bold=True)

    lose_img = pygame.image.load("assets/lose_screen.png")
    lose_img = pygame.transform.scale(lose_img, (screen.get_width(), screen.get_height()))
    screen.blit(lose_img, (0, 0))

    # Draw “Main Menu” button
    btn_w, btn_h = 225, 70
    btn_x = ((screen.get_width() - btn_w) // 2) - 10
    btn_y = screen.get_height() - screen.get_height()//3
    main_btn = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    main_btn_border = pygame.Rect(btn_x - 5, btn_y - 5, btn_w + 10, btn_h + 10)
    pygame.draw.rect(screen, (29, 18, 11), main_btn_border, border_radius=10)      # button bg
    pygame.draw.rect(screen, (161, 96, 37), main_btn, border_radius=10)      # button bg
    btn_txt = btn_font.render("Exit", True, (43, 29, 11))
    screen.blit(btn_txt, (btn_x + (btn_w - btn_txt.get_width())//2,
                          btn_y + (btn_h - btn_txt.get_height())//1.5))
    pygame.display.flip()

    # Wait for click
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if main_btn.collidepoint(ev.pos):
                    pygame.quit()
                    exit()
                    return
