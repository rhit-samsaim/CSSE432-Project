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
        screen.blit(player_text, (box_x_pos + 10, box_y_pos + 25))


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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        try:
            connected_count = len(server.connected_clients)

            # Build the list of ready states by pinging each client
            ready_states = []
            with server.lock:
                for client in server.connected_clients:
                    try:
                        client.sendall("status".encode("utf-8"))
                        response = client.recv(1024).decode("utf-8")
                        parts = response.split(",")
                        if len(parts) >= 3:
                            ready_states.append(parts[2] == "1")
                        else:
                            ready_states.append(False)
                    except:
                        ready_states.append(False)

            draw_screen(connected_count, server.max_clients, ready_states)

        except Exception as e:
            print(f"Error in create_lobby: {e}")
            draw_screen(0, server.max_clients, [])


def create_client_lobby(client):
    global screen, font, width, height, size, isClient
    screen, font, width, height, size = init_gui(screen, font, width, height, size)
    ready_clicked = False  # Track if client has clicked ready

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if ready_btn.collidepoint(mouse_pos) and not ready_clicked:
                    client.send("ready")
                    ready_clicked = True

        try:
            client.send("status")
            response = client.receive()
            parts = response.split(",")
            connected_count = int(parts[0])
            max_clients = int(parts[1])
            ready_states = [p == "1" for p in parts[2:]]
        except:
            connected_count, max_clients = 1, 5
            ready_states = [False]

        # Draw everything
        ready_btn, _ = draw_screen(connected_count, max_clients, ready_states)

