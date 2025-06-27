import pygame
import os
import time

# Initialize Pygame
pygame.init()

# Get the screen info and set up fullscreen
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# Set up the display
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Persona Display")

# Colors
BLACK = (0, 0, 0)

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Clear screen with black background
    screen.fill(BLACK)
    
    # Try to read the persona number from the file
    persona_number = None
    try:
        with open("db/current_persona", "r") as f:
            content = f.read().strip()
            if content.isdigit():
                persona_number = int(content)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error reading persona file: {e}")
    
    # If we have a valid persona number, try to display the image
    if persona_number is not None:
        image_path = f"assets/{persona_number}.png"
        try:
            # Load and display the image
            image = pygame.image.load(image_path)
            
            # Scale image to fit screen while maintaining aspect ratio
            image_rect = image.get_rect()
            screen_rect = screen.get_rect()
            
            # Calculate scaling factor
            scale_x = screen_width / image_rect.width
            scale_y = screen_height / image_rect.height
            scale = min(scale_x, scale_y)
            
            # Scale the image
            new_width = int(image_rect.width * scale)
            new_height = int(image_rect.height * scale)
            scaled_image = pygame.transform.scale(image, (new_width, new_height))
            
            # Center the image on screen
            scaled_rect = scaled_image.get_rect()
            scaled_rect.center = screen_rect.center
            
            # Draw the image
            screen.blit(scaled_image, scaled_rect)
            
        except pygame.error as e:
            print(f"Error loading image {image_path}: {e}")
            # If image loading fails, keep black background
            pass
        except Exception as e:
            print(f"Unexpected error with image {image_path}: {e}")
            # If any other error occurs, keep black background
            pass
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(30)

# Clean up
pygame.quit()
