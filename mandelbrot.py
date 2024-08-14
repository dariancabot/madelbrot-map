import pygame
import numpy as np
import threading
from settings import *  # Import all settings from the settings.py file

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mandelbrot Map")

# Initial view
ASPECT_RATIO = WIDTH / HEIGHT
INITIAL_X_RANGE = 3.0
INITIAL_Y_RANGE = INITIAL_X_RANGE / ASPECT_RATIO
x_min, x_max = -2.0, 1.0
y_min, y_max = -INITIAL_Y_RANGE / 2, INITIAL_Y_RANGE / 2


def mandelbrot(height, width, x_min, x_max, y_min, y_max):
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    c = x[:, np.newaxis] + 1j * y[np.newaxis, :]
    z = np.zeros_like(c)
    div_time = np.zeros_like(z, dtype=int)

    for i in range(MAX_ITER):
        z = z**2 + c
        diverge = np.abs(z) > 2
        div_now = diverge & (div_time == 0)
        div_time[div_now] = i + 1
        z[diverge] = 2

    return div_time


def create_mandelbrot_surface(array):
    color_array = np.zeros((array.shape[0], array.shape[1], 3), dtype=np.uint8)
    color_array[:, :] = LAND_COLOUR
    color_array[array == 0] = OCEAN_DEEP_COLOUR  # Main Mandelbrot set
    color_array[(array > COASTLINE_ITER) & (
        array <= MAX_ITER)] = OCEAN_SHALLOW_COLOUR
    return pygame.surfarray.make_surface(color_array)


def calculate_zoom(x_min, x_max, y_min, y_max):
    current_x_range = x_max - x_min
    current_y_range = y_max - y_min
    zoom_x = INITIAL_X_RANGE / current_x_range
    zoom_y = INITIAL_Y_RANGE / current_y_range
    return max(zoom_x, zoom_y)


def screen_to_complex(x, y, x_min, x_max, y_min, y_max):
    re = x_min + (x_max - x_min) * x / WIDTH
    im = y_min + (y_max - y_min) * y / HEIGHT
    return re, im


def draw_calc_msg(screen):
    font = pygame.font.Font(None, 24)
    loading_text = "Calculating..."
    text_surface = font.render(loading_text, True, TEXT_COLOUR)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)


def calculate_mandelbrot_async(height, width, x_min, x_max, y_min, y_max):
    global mandelbrot_set, mandelbrot_surface, is_calc, drag_offset
    mandelbrot_set = mandelbrot(height, width, x_min, x_max, y_min, y_max)
    mandelbrot_surface = create_mandelbrot_surface(mandelbrot_set)
    is_calc = False
    drag_offset = (0, 0)  # Reset drag_offset after calculation


def main():
    global x_min, x_max, y_min, y_max, mandelbrot_set, mandelbrot_surface, is_calc, drag_offset

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    running = True
    dragging = False
    start_pos = None
    drag_offset = (0, 0)

    # Create initial Mandelbrot set surface
    mandelbrot_set = mandelbrot(HEIGHT, WIDTH, x_min, x_max, y_min, y_max)
    mandelbrot_surface = create_mandelbrot_surface(mandelbrot_set)
    is_calc = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    dragging = True
                    start_pos = event.pos
                    drag_offset = (0, 0)
                elif event.button == 4 and not is_calc:  # Scroll up (zoom in)
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    center_x, center_y = screen_to_complex(
                        mouse_x - drag_offset[0], mouse_y - drag_offset[1], x_min, x_max, y_min, y_max)
                    x_min = center_x + (x_min - center_x) * ZOOM_FACTOR
                    x_max = center_x + (x_max - center_x) * ZOOM_FACTOR
                    y_min = center_y + (y_min - center_y) * ZOOM_FACTOR
                    y_max = center_y + (y_max - center_y) * ZOOM_FACTOR
                    is_calc = True
                    threading.Thread(target=calculate_mandelbrot_async, args=(
                        HEIGHT, WIDTH, x_min, x_max, y_min, y_max)).start()
                # Scroll down (zoom out)
                elif event.button == 5 and not is_calc:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    center_x, center_y = screen_to_complex(
                        mouse_x - drag_offset[0], mouse_y - drag_offset[1], x_min, x_max, y_min, y_max)
                    x_min = center_x + (x_min - center_x) / ZOOM_FACTOR
                    x_max = center_x + (x_max - center_x) / ZOOM_FACTOR
                    y_min = center_y + (y_min - center_y) / ZOOM_FACTOR
                    y_max = center_y + (y_max - center_y) / ZOOM_FACTOR
                    is_calc = True
                    threading.Thread(target=calculate_mandelbrot_async, args=(
                        HEIGHT, WIDTH, x_min, x_max, y_min, y_max)).start()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging:
                    dragging = False
                    # Update the view coordinates based on the total drag
                    dx = (x_max - x_min) * drag_offset[0] / WIDTH
                    dy = (y_max - y_min) * drag_offset[1] / HEIGHT
                    x_min -= dx
                    x_max -= dx
                    y_min -= dy
                    y_max -= dy
                    if not is_calc:
                        is_calc = True
                        threading.Thread(target=calculate_mandelbrot_async, args=(
                            HEIGHT, WIDTH, x_min, x_max, y_min, y_max)).start()
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    current_pos = event.pos
                    drag_offset = (
                        current_pos[0] - start_pos[0], current_pos[1] - start_pos[1])

        screen.fill(VOID_COLOUR)  # Fill the screen with 'void' color

        # Draw the Mandelbrot set with the current drag offset
        screen.blit(mandelbrot_surface, drag_offset)

        # Calculate and display coordinates and zoom
        zoom = calculate_zoom(x_min, x_max, y_min, y_max)
        coord_text = f"Center: X: {(x_min + x_max) / 2:.3f}, Y: {(y_min + y_max) / 2:.3f}, Zoom: {zoom:.2f}x"
        text_surface = font.render(coord_text, True, TEXT_COLOUR)
        screen.blit(text_surface, (10, 10))

        # Display mouse coordinates
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_complex_x, mouse_complex_y = screen_to_complex(
            mouse_x - drag_offset[0], mouse_y - drag_offset[1], x_min, x_max, y_min, y_max)
        mouse_text = f"Mouse: X: {mouse_complex_x:.3f}, Y: {mouse_complex_y:.3f}"
        mouse_surface = font.render(mouse_text, True, TEXT_COLOUR)
        screen.blit(mouse_surface, (10, 30))

        if is_calc:
            draw_calc_msg(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
