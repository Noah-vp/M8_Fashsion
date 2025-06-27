import pygame
import sys
import os
import gif_pygame # type: ignore    
import serial # type: ignore
import time
import json

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((1920, 1080))
pygame.display.toggle_fullscreen()
pygame.display.set_caption("Washing Machine Visualization")

# Load the GIF
gif = gif_pygame.load(os.path.join(os.path.dirname(__file__), "assets", "water2d.gif"))

# Load the font
font = pygame.font.Font(None, 36)

# Initialize serial connection
ser = None
try:
    with open("db/com_ports.json", "r") as f:
        com_ports = json.load(f)
        ser = serial.Serial(com_ports["washingmachine_buttons"], 9600, timeout=1)
        time.sleep(2)  # Wait for connection to establish
        print(f"Serial connection established on {com_ports['washingmachine_buttons']}")
except Exception as e:
    print(f"Warning: Could not connect to serial port {com_ports['washingmachine_buttons']}: {e}")
    print("PyGame visualization will run without serial communication")
    ser = None

# Main game loop
running = True
clock = pygame.time.Clock()

water_height = 0
impact_data = None 
update_km = False

# Water fill boundaries
WATER_Y_MIN = 200  # Top (full)
WATER_Y_MAX = 1450  # Bottom (empty)
WATER_PIXEL_RANGE = WATER_Y_MAX - WATER_Y_MIN
GIF_OFFSET = 100


def calculate_washing_impact(cycles_per_week, temp):
    # kWh per cycle for each temperature
    energy_per_cycle = {
        "10": 0.12,
        "20": 0.40,
        "30": 0.60,
        "40": 0.75,
        "60": 1.30,
        "90": 1.90
    }

    # Water per cycle (liters)
    water_per_cycle = 60.54

    # Electric vehicle energy efficiency
    car_kwh_per_km = 0.19

    # Validate temperature
    temp = str(temp).lower()
    if temp not in energy_per_cycle:
        raise ValueError("Invalid temperature. Choose from: 10, 20, 30, 40, 60, 90")

    # Calculate
    cycles_per_year = cycles_per_week * 52
    total_kwh = energy_per_cycle[temp] * cycles_per_year
    total_liters = water_per_cycle * cycles_per_year
    equivalent_km = total_kwh / car_kwh_per_km
    current_km = 0

    return {
        "liters": round(total_liters, 2),
        "km": round(equivalent_km, 1),
        "energy_usage": round(total_kwh, 2),
    }

def decode_command(command):
    global impact_data, water_height, update_km
    while True:
        try:
            with open("db/lastcommand_wash.txt", "w") as f:
                if command.startswith("N|"):
                    f.write(f"N|{impact_data['energy_usage']},{impact_data['liters']}")
                else:
                    f.write(f"{command}")
            break
        except IOError:
            time.sleep(0.1)
    if command.startswith("C|"):
        # Parse the command
        parts = command.split("|")[1].split(",")
        impact_data = calculate_washing_impact(float(parts[0]), parts[1])
        print(f"Calculated impact: {impact_data}")
    elif command.startswith("R|"):	
        if impact_data:
            if is_water_full():
                print("Water is full")
            else:
                water_height += 20
    elif command.startswith("N|"):
        print("New user")
        water_height = 0
        update_km = False
    elif command.startswith("RESET|"):
        print("Reset washing machine")
        water_height = 0
        update_km = False
    else:
        print(f"Unknown command: {command}")

def draw_guide_lines():
    for liters in range(0, 35000+1, 5000):
        # Map liters to the new y-coordinate range
        y = int(WATER_Y_MAX - (liters / 35000) * WATER_PIXEL_RANGE)
        pygame.draw.line(screen, (180,180,180), (0, y), (screen.get_width(), y), 2)
        label = font.render(f"{liters} L", True, (120,120,120))
        label_rect = label.get_rect(center=(screen.get_width()//2, y))
        screen.blit(label, label_rect)

def display_final_message():
    
    text = font.render(f"Your washing habits use {(int(impact_data['liters'])/1000):.2f}k liters of water per year", True, (0,0,0))
    text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(text, text_rect)
    

def is_water_full():
    global impact_data, water_height
    if impact_data:
        # Convert the liters to pixels in the new range
        liters_to_pixels = impact_data['liters'] / 35000 * WATER_PIXEL_RANGE
        return water_height >= liters_to_pixels
    return False


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                GIF_OFFSET += 1
            if event.key == pygame.K_UP:
                GIF_OFFSET -= 1
    try:
        if ser and ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            decode_command(line)
    except Exception as e:
        print(f"Error: {e}")

    #print(f"Debug: Water height: {water_height}, impact_data: {impact_data}")

    screen.fill((255, 255, 255))
    # Calculate the current y and height for the water rectangle
    if impact_data:
        max_water_height = impact_data['liters'] / 35000 * WATER_PIXEL_RANGE
    else:
        max_water_height = WATER_PIXEL_RANGE
    current_y = WATER_Y_MAX - min(water_height, max_water_height)
    rect_height = WATER_Y_MAX - current_y
    pygame.draw.rect(screen, (45, 255, 232), (0, current_y, screen.get_width(), rect_height))
    if gif and rect_height > 0:
        gif_width = screen.get_width()
        gif_height = int(gif_width * (gif.blit_ready().get_height() / gif.blit_ready().get_width()))  # Maintain aspect ratio
        # Scale the GIF to the width of the screen and the height of the water rectangle
        scaled_gif = pygame.transform.scale(gif.blit_ready(), (gif_width, gif_height))
        # Blit the GIF at the top of the water rectangle
        screen.blit(scaled_gif, (0, current_y - GIF_OFFSET))
    if impact_data and is_water_full(): 
        display_final_message()
        if not update_km:
            current_km = 0
            with open("db/total_km.txt", "r") as f:
                current_km = int(f.read())
            with open("db/total_km.txt", "w") as f:
                print(f"Adding {impact_data['km']} to {current_km}")
                f.write(f"{int(current_km + impact_data['km'])}")
            update_km = True
            with open("db/com_ports.json", "r") as f:
                com_ports = json.load(f)
            ser2 = serial.Serial(com_ports["washingmachine_car"], 9600, timeout=1)
            ser2.write(f"E|{impact_data['km']}".encode())
            ser2.close()
    elif impact_data:
        draw_guide_lines()

    pygame.display.flip()
    clock.tick(60)
