import sys
import pygame

def init_gui(screen, font, width, height, size):

    pygame.init()
    width, height = 1300, 1200

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Wizard!!!")
    font = pygame.font.SysFont("liberationserif", 50, bold=True)

    size = (width, height)

    return screen, font, width, height, size


def draw_button(screen, font, text, x, y, w, h, color, text_color):
    rect = pygame.Rect(x, y, w, h)
    background_rect = pygame.Rect(x - 2, y - 2, w + 4, h + 4)
    pygame.draw.rect(screen, (0, 0, 0), background_rect, border_radius=10)
    pygame.draw.rect(screen, color, rect, border_radius=10)
    label = font.render(text, True, text_color)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
    return rect
