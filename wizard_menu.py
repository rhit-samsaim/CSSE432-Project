import sys
import threading
import pygame
from server import Server
from client import Client
from typing import Optional

# This is SOLELY to remove yellow highlighting errors that are like "This is set to Nona, may error"
screen: Optional[pygame.Surface] = None
font: Optional[pygame.font.Font] = None
width: Optional[int] = None
height: Optional[int] = None

size = None
get_IP = None
text_input = ''
active = False


def init_gui():
    global screen, font, width, height, size, get_IP

    pygame.init()
    width, height = 1200, 800

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Wizard Game Menu")
    font = pygame.font.SysFont("", 40)

    size = (width, height)
    get_IP = False


def draw_button(text, x, y, w, h, color):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, rect, border_radius=10)
    label = font.render(text, True, (255, 255, 255))
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
    return rect


def draw_menu():
    btn_color = (255, 36, 0)
    background_color = (19, 56, 190)
    btn_w = 200
    btn_h = 60

    screen.fill(background_color)
    host_btn = draw_button("Host Game", (width / 2 - btn_w / 2), (height / 2 + 100), btn_w, btn_h, btn_color)
    join_btn = draw_button("Join Game", (width / 2 - btn_w / 2), (height / 2 + 200), btn_w, btn_h, btn_color)

    logo = pygame.image.load("assets/wizard-logo.png")
    logo = pygame.transform.scale(logo, (600, 300))
    screen.blit(logo, (300, 100))

    if get_IP:
        rect1 = pygame.Rect((width / 2 - 150), (height / 2 - 50), 300, 100)
        text_box = pygame.Rect((width / 2 - 125), (height / 2 - 10), 250, 50)
        pygame.draw.rect(screen, (187, 187, 187), rect1)
        pygame.draw.rect(screen, (238, 238, 238), text_box)

        # Draw text input
        text_caption = font.render("Enter Host IP Below:", True, (0, 0, 0))
        screen.blit(text_caption, ((width / 2 - 200) + 60, (height / 2 - 40)))
        input_surface = font.render(text_input, True, (0, 0, 0))
        screen.blit(input_surface, (text_box.x + 10, text_box.y + 18))

    # Update entire screen with new content
    pygame.display.flip()
    return host_btn, join_btn

def main_menu():
    global get_IP, text_input
    init_gui()

    while True:
        host_btn, join_btn = draw_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not get_IP:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if host_btn.collidepoint(event.pos):
                        run_as_host()
                    elif join_btn.collidepoint(event.pos):
                        get_IP = True
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        print(f"Typed IP: {text_input}")
                        run_as_client(text_input)
                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]
                    else:
                        text_input += event.unicode

def run_as_host():
    print("starting as host...")
    server = Server()
    threading.Thread(target=server.start, daemon=True).start()
    server.start()


def run_as_client(ip):
    global get_IP
    client = Client(ip)
    did_connect = client.connect()
    if not did_connect:
        get_IP = False