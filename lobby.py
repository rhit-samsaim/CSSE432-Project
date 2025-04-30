import sys
import pygame
from typing import Optional
from scenes import init_gui, draw_button

screen: Optional[pygame.Surface] = None
font: Optional[pygame.font.Font] = None
width: Optional[int] = None
height: Optional[int] = None
size = None


def draw_screen(connected_count, max_clients):
    btn_w = 160
    btn_h = 40

    screen.fill((237, 232, 218))
    ready_btn = draw_button(screen, font, "Ready Up!", (width - 370), (height - 50), btn_w, btn_h, (92, 184, 92),
                            (255, 255, 255))
    start_btn = draw_button(screen, font, "Start Game", (width - 185), (height - 50), btn_w, btn_h, (15, 64, 197),
                            (255, 255, 255))

    # Display connection count
    status_font = pygame.font.SysFont(None, 24)
    status_text = status_font.render(f"{connected_count} / {max_clients} players connected", True, (0, 0, 0))
    screen.blit(status_text, (20, height - 40))

    # Update entire screen with new content
    pygame.display.flip()
    return ready_btn, start_btn


def create_lobby(server):
    global screen, font, width, height, size
    screen, font, width, height, size = init_gui(screen, font, width, height, size)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        connected_count = len(server.connected_clients)
        draw_screen(connected_count, server.max_clients)

def create_client_lobby(client):
    global screen, font, width, height, size
    screen, font, width, height, size = init_gui(screen, font, width, height, size)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        try:
            client.send("status")
            response = client.receive()
            connected_count, max_clients = map(int, response.split(","))
        except:
            connected_count, max_clients = 1, 5  # Fallback/default - Still confused why this is needed

        draw_screen(connected_count, max_clients)

