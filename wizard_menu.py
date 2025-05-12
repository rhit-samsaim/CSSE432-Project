import sys
import pygame
from typing import Optional
from scenes import init_gui, draw_button

# This is SOLELY to remove yellow highlighting errors that are like "This is set to Nona, may error"
screen: Optional[pygame.Surface] = None
font: Optional[pygame.font.Font] = None
width: Optional[int] = None
height: Optional[int] = None

size = None
get_IP = None
text_input = ''
active = False
color_cycle = 1
color1 = 255
color2 = 0
color3 = 0
logo_width = 0
logo_height = 0
logo_growing = True


def draw_menu():
    global color1, color2, color3, logo_width, logo_height, logo_growing
    btn_color = (255, 255, 255)
    adjust_color()
    background_color = (color1, color2, color3)
    btn_w = 300
    btn_h = 100

    screen.fill(background_color)
    host_btn = draw_button(screen, font, "Host Game", (width / 2 - btn_w / 2), (height / 2 + 100), btn_w, btn_h, btn_color, (0, 0, 0))
    join_btn = draw_button(screen, font, "Join Game", (width / 2 - btn_w / 2), (height / 2 + 300), btn_w, btn_h, btn_color, (0, 0, 0))

    if logo_growing:
        logo_width += 1
        logo_height += 0.5
        if logo_width == 200:
            logo_growing = False
    else:
        logo_width -= 1
        logo_height -= 0.5
        if logo_width == 0:
            logo_growing = True

    logo = pygame.image.load("assets/wizard-logo.png")
    logo = pygame.transform.scale(logo, (800 + logo_width, 400 + logo_height))
    screen.blit(logo, ((width / 2) - (400 + logo_width/2), 150 - logo_height/2))

    if get_IP:
        rect1 = pygame.Rect((width / 2 - 250), (height / 2 - 50), 500, 200)
        text_box = pygame.Rect((width / 2 - 230), (height / 2 + 20), 460, 100)
        pygame.draw.rect(screen, (187, 187, 187), rect1)
        pygame.draw.rect(screen, (238, 238, 238), text_box)

        # Draw text input
        text_caption = font.render("Enter Host IP Below:", True, (0, 0, 0))
        screen.blit(text_caption, ((width / 2 - 250) + 10, (height / 2 - 50) + 10))
        input_surface = font.render(text_input, True, (0, 0, 0))
        screen.blit(input_surface, (text_box.x + 10, text_box.y + 30))

    # Update entire screen with new content
    pygame.display.flip()
    return host_btn, join_btn


def main_menu():
    global get_IP, text_input, screen, font, width, height, size
    screen, font, width, height, size = init_gui(screen, font, width, height, size)
    get_IP = False
    clock = pygame.time.Clock()

    while True:
        host_btn, join_btn = draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not get_IP:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if host_btn.collidepoint(event.pos):
                        return -1
                    elif join_btn.collidepoint(event.pos):
                        get_IP = True
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        print(f"Typed IP: {text_input}")
                        return text_input
                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]
                    else:
                        text_input += event.unicode



def adjust_color():
    global color_cycle, color1, color2, color3
    if color_cycle == 1:
        if color2 != 255:
            color2 += 1
        else:
            color_cycle = 2
            color1 -= 1
    elif color_cycle == 2:
        if color1 != 0:
            color1 -= 1
        else:
            color_cycle = 3
            color3 += 1
    elif color_cycle == 3:
        if color3 != 255:
            color3 += 1
        else:
            color_cycle = 4
            color2 -= 1
    elif color_cycle == 4:
        if color2 != 0:
            color2 -= 1
        else:
            color_cycle = 5
            color1 += 1
    elif color_cycle == 5:
        if color1 != 255:
            color1 += 1
        else:
            color_cycle = 6
            color3 -= 1
    else:
        if color3 != 0:
            color3 -= 1
        else:
            color_cycle = 1
            color2 += 1
