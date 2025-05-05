import sys
import pygame
from typing import Optional
from scenes import init_gui, draw_button

screen: Optional[pygame.Surface] = None
font: Optional[pygame.font.Font] = None
width: Optional[int] = None
height: Optional[int] = None
size = None
isClient = True


def draw_screen(connected_count, max_clients, ready_states):
    btn_w = 275
    btn_h = 60

    screen.fill((237, 232, 218))
    if not isClient:
        ready_btn = draw_button(screen, font, "Ready Up!", (width - 600), (height - 100), btn_w, btn_h, (92, 184, 92), (255, 255, 255))
        start_btn = draw_button(screen, font, "Start Game", (width - 300), (height - 100), btn_w, btn_h, (15, 64, 197), (255, 255, 255))
    else:
        ready_btn = draw_button(screen, font, "Ready Up!", (width - 300), (height - 100), btn_w, btn_h, (92, 184, 92), (255, 255, 255))
        start_btn = None

    for i in range(connected_count + 1):
        if i > 2:
            box_x_pos = 700
            box_y_pos = 200 * (i - 2) + 100
        else:
            box_x_pos = 200
            box_y_pos = 200 * i + 100

        player_rect = pygame.Rect(box_x_pos, box_y_pos, 400, 100)
        pygame.draw.rect(screen, (0, 0, 0), player_rect, width=3)

        # Draw player label
        player_text_font = pygame.font.SysFont(None, 80)
        player_text = player_text_font.render(f"Player {i + 1}", True, (0, 0, 0))
        screen.blit(player_text, (box_x_pos + 15, box_y_pos + 25))

        #Draw status image
        if i < len(ready_states) and ready_states[i]:
            ready_img = pygame.image.load("assets/is_ready.png")
            ready_img = pygame.transform.scale(ready_img, (70, 70))
            screen.blit(ready_img, (box_x_pos + 300, box_y_pos + 15))
        else:
            not_ready_img = pygame.image.load("assets/not_ready.png")
            not_ready_img = pygame.transform.scale(not_ready_img, (70, 70))
            screen.blit(not_ready_img, (box_x_pos + 300, box_y_pos + 15))

    # Display connection count
    status_font = pygame.font.SysFont(None, 60)
    status_text = status_font.render(f"{connected_count + 1} / {max_clients + 1} players connected", True, (0, 0, 0))
    screen.blit(status_text, (20, height - 90))

    pygame.display.flip()
    return ready_btn, start_btn



def create_lobby(server):
    global screen, font, width, height, size, isClient
    screen, font, width, height, size = init_gui(screen, font, width, height, size)
    isClient = False

    while True:
        connected_count = len(server.connected_clients)
        print(f"Ready Statuses is: {server.ready_statuses}")
        for i, client in enumerate(server.connected_clients):
            try:
                client.send("status")
                response = client.recieve()
                server.ready_statuses[i + 1] = response.strip()
            except:
                temp = 0

        ready_btn, start_btn = draw_screen(connected_count, server.max_clients, server.ready_statuses)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ready_btn.collidepoint(event.pos):
                    server.ready_statuses[0] = True
                elif start_btn.collidepoint(event.pos):
                    length = len(server.ready_statuses)
                    if length < 3:
                        continue
                    for i in range(length):
                        if not server.ready_statuses[i]:
                            continue
                    return 0


def create_client_lobby(client):
    global screen, font, width, height, size, isClient
    screen, font, width, height, size = init_gui(screen, font, width, height, size)

    while True:
        try:
            ready_states = request_ready_states(client)
            connected_count = len(ready_states)
        except:
            ready_states = [False]
            connected_count = 1

        ready_btn, _ = draw_screen(connected_count - 1, 5, ready_states)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if ready_btn.collidepoint(mouse_pos):
                    client.send("ready")


def request_ready_states(client):
    try:
        client.send("request_ready_states")
        response = client.receive()

        if response.startswith("update_ready_states:"):
            ready_states_str = response[len("update_ready_states:"):]
            # Convert the string back into a list of booleans
            ready_states = [state == "True" for state in ready_states_str.split(',')]
            return ready_states
        else:
            return []
    except Exception as e:
        print(f"Error receiving ready states: {e}")
        return []
