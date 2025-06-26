import pygame
import sys
import time
import os

# Window size
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1200

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("KM Flipper Counter")

# Fonts
pygame.font.init()
font = pygame.font.SysFont("Courier New", 130, bold=True)
small_font = pygame.font.SysFont("Segoe UI", 38, bold=True)
title_font = pygame.font.SysFont("Segoe UI", 54, bold=True)
sub_font = pygame.font.SysFont("Segoe UI", 32)

# Colors
bg_top = (218, 200, 170)
bg_bottom = (240, 240, 240)
flip_color = (30, 30, 30)
flip_gloss = (255, 255, 255, 40)
text_color = (255, 255, 255)

# File path for total km
TOTAL_KM_FILE = "db/total_km.txt"

# State
km = 0
km_target = 0
flip_delay = 10
update_delay = 0.5  # 0.5 second delay between file reads

def read_total_km():
    """Read the total km from the file"""
    try:
        if os.path.exists(TOTAL_KM_FILE):
            with open(TOTAL_KM_FILE, 'r') as f:
                content = f.read().strip()
                if content:
                    return int(content)
    except (ValueError, IOError) as e:
        print(f"Error reading total km: {e}")
    return 0

def draw_gradient_background():
    for y in range(WINDOW_HEIGHT):
        ratio = y / WINDOW_HEIGHT
        r = int(bg_top[0] * (1 - ratio) + bg_bottom[0] * ratio)
        g = int(bg_top[1] * (1 - ratio) + bg_bottom[1] * ratio)
        b = int(bg_top[2] * (1 - ratio) + bg_bottom[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

def draw_counter(km_str):
    digit_width = 120
    spacing = 25
    radius = 20
    total_width = len(km_str) * (digit_width + spacing) - spacing
    start_x = (WINDOW_WIDTH // 4 - total_width // 2)
    y = WINDOW_HEIGHT // 2 - 120

    # Header
    label = title_font.render("TOTAL KM TRAVELED TODAY", True, (30, 30, 30))
    screen.blit(label, (WINDOW_WIDTH // 4 - label.get_width() // 2, y - 130))

    # Digits
    for i, digit in enumerate(km_str):
        x = start_x + i * (digit_width + spacing)
        rect = pygame.Rect(x, y, digit_width, 180)
        shadow = rect.move(4, 6)

        pygame.draw.rect(screen, (0, 0, 0, 50), shadow, border_radius=radius)
        pygame.draw.rect(screen, flip_color, rect, border_radius=radius)

        gloss = pygame.Surface((digit_width, 70), pygame.SRCALPHA)
        pygame.draw.ellipse(gloss, flip_gloss, gloss.get_rect())
        screen.blit(gloss, rect.topleft)

        digit_surface = font.render(digit, True, text_color)
        digit_rect = digit_surface.get_rect(center=rect.center)
        screen.blit(digit_surface, digit_rect)

def draw_secondary_counter(count_str):
    digit_width = 120
    spacing = 25
    radius = 20
    total_width = len(count_str) * (digit_width + spacing) - spacing
    start_x = (3 * WINDOW_WIDTH // 4 - total_width // 2)
    y = WINDOW_HEIGHT // 2 - 120

    # Header
    label = title_font.render("TIMES DRIVEN TO DUBAI TODAY", True, (30, 30, 30))
    screen.blit(label, (3 * WINDOW_WIDTH // 4 - label.get_width() // 2, y - 130))

    # Digits
    for i, digit in enumerate(count_str):
        x = start_x + i * (digit_width + spacing)
        rect = pygame.Rect(x, y, digit_width, 180)
        shadow = rect.move(4, 6)

        pygame.draw.rect(screen, (0, 0, 0, 50), shadow, border_radius=radius)
        pygame.draw.rect(screen, flip_color, rect, border_radius=radius)

        gloss = pygame.Surface((digit_width, 70), pygame.SRCALPHA)
        pygame.draw.ellipse(gloss, flip_gloss, gloss.get_rect())
        screen.blit(gloss, rect.topleft)

        digit_surface = font.render(digit, True, text_color)
        digit_rect = digit_surface.get_rect(center=rect.center)
        screen.blit(digit_surface, digit_rect)

def draw_info_block():
    center_x = WINDOW_WIDTH // 2
    y = WINDOW_HEIGHT // 2 + 200  # lowered for breathing room

    text1 = sub_font.render("FROM AMSTERDAM TO DUBAI:", True, (50, 50, 50))
    text2 = sub_font.render("SKY WIDE = 5165.58 KM", True, (50, 50, 50))
    text3 = sub_font.render("DRIVING ROUTE = 6644.95 KM", True, (50, 50, 50))

    screen.blit(text1, (center_x - text1.get_width() // 2, y))
    screen.blit(text2, (center_x - text2.get_width() // 2, y + 40))
    screen.blit(text3, (center_x - text3.get_width() // 2, y + 80))

def render_screen():
    draw_gradient_background()
    draw_counter(str(km).rjust(6, '0'))
    dubai_count = km // 6645
    draw_secondary_counter(str(dubai_count).rjust(2, '0'))
    draw_info_block()
    pygame.display.flip()

# Initialize km from file
km = read_total_km()

# First frame
render_screen()

# Main loop
running = True
last_file_check = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    # Check file for updates every 0.5 seconds
    current_time = time.time()
    if current_time - last_file_check >= update_delay:
        new_km = read_total_km()
        if new_km != km_target:
            km_target = new_km
            print(f"Updated km: {km_target}")
        last_file_check = current_time
    
    if km < km_target:
        km += 1
    elif km > km_target:
        km -= 1

    render_screen()
    pygame.time.delay(flip_delay)

pygame.quit()
sys.exit()