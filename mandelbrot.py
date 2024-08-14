import pygame
import numpy as np
import threading
import time
from settings import *  # Import all settings from the settings.py file

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mandelbrot Map")

# Load the pixel font
try:
    if PIXEL_DOUBLING:
        PIXEL_FONT_SIZE *= 2
    pixel_font = pygame.font.Font(
        "assets/PressStart2P-Regular.ttf", PIXEL_FONT_SIZE)
except:
    print("Pixel font not found. Using default font.")
    pixel_font = pygame.font.Font(None, NORMAL_FONT_SIZE)

# Calculate actual dimensions for rendering
RENDER_WIDTH = WIDTH // 2 if PIXEL_DOUBLING else WIDTH
RENDER_HEIGHT = HEIGHT // 2 if PIXEL_DOUBLING else HEIGHT

# Initial view
ASPECT_RATIO = WIDTH / HEIGHT
INITIAL_X_RANGE = 3.0
INITIAL_Y_RANGE = INITIAL_X_RANGE / ASPECT_RATIO
x_min, x_max = -2.0, 1.0
y_min, y_max = -INITIAL_Y_RANGE / 2, INITIAL_Y_RANGE / 2


def create_wave_texture():
    texture = np.zeros((WAVE_SIZE, WAVE_SIZE, 3), dtype=np.uint8)
    texture[:, :] = OCEAN_DEEP_COLOUR

    # First wave
    texture[0, 2] = WAVE_COLOUR
    texture[1, 2] = WAVE_COLOUR
    texture[2, 2] = WAVE_COLOUR
    texture[3, 1] = WAVE_COLOUR
    texture[4, 1] = WAVE_COLOUR
    texture[5, 0] = WAVE_COLOUR
    texture[6, 1] = WAVE_COLOUR
    texture[7, 1] = WAVE_COLOUR
    texture[8, 2] = WAVE_COLOUR
    texture[9, 2] = WAVE_COLOUR
    texture[10, 2] = WAVE_COLOUR

    # Second wave
    texture[16, 18] = WAVE_COLOUR
    texture[17, 18] = WAVE_COLOUR
    texture[18, 18] = WAVE_COLOUR
    texture[19, 17] = WAVE_COLOUR
    texture[20, 17] = WAVE_COLOUR
    texture[21, 16] = WAVE_COLOUR
    texture[22, 17] = WAVE_COLOUR
    texture[23, 17] = WAVE_COLOUR
    texture[24, 18] = WAVE_COLOUR
    texture[25, 18] = WAVE_COLOUR
    texture[26, 18] = WAVE_COLOUR
    return texture


wave_texture = create_wave_texture()


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
    height, width = array.shape
    color_array = np.zeros((height, width, 3), dtype=np.uint8)

    # Apply wave texture to the deep ocean (Mandelbrot set)
    deep_ocean = array == 0
    for i in range(height):
        for j in range(width):
            if deep_ocean[i, j]:
                color_array[i, j] = wave_texture[i % WAVE_SIZE, j % WAVE_SIZE]
            elif array[i, j] > COASTLINE_ITER:
                color_array[i, j] = OCEAN_SHALLOW_COLOUR
            else:
                color_array[i, j] = LAND_COLOUR

    surface = pygame.surfarray.make_surface(color_array)

    if PIXEL_DOUBLING:
        return pygame.transform.scale(surface, (WIDTH, HEIGHT))
    else:
        return surface


def calculate_mandelbrot_async(height, width, x_min, x_max, y_min, y_max):
    global mandelbrot_set, mandelbrot_surface, is_calc, drag_offset
    mandelbrot_set = mandelbrot(height, width, x_min, x_max, y_min, y_max)
    mandelbrot_surface = create_mandelbrot_surface(mandelbrot_set)

    # Draw markers directly on the mandelbrot surface
    draw_markers(mandelbrot_surface, x_min, x_max, y_min, y_max)

    is_calc = False
    drag_offset = (0, 0)  # Reset drag_offset after calculation


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


def render_text_with_background(text, font, text_color, bg_color):
    text_surface = font.render(text, True, text_color)
    text_w, text_h = text_surface.get_size()
    bg_surface = pygame.Surface((text_w + 4, text_h + 4), pygame.SRCALPHA)
    bg_surface.fill(bg_color)
    bg_surface.blit(text_surface, (2, 2))
    return bg_surface


def draw_calc_msg(screen):
    loading_text = "Calculating..."
    text_surface = render_text_with_background(
        loading_text, pixel_font, TEXT_COLOUR, (*TEXT_BG_COLOUR, 180))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)


def complex_to_screen(x, y, x_min, x_max, y_min, y_max):
    screen_x = (x - x_min) / (x_max - x_min) * WIDTH
    screen_y = (y - y_min) / (y_max - y_min) * HEIGHT
    return int(screen_x), int(screen_y)


def draw_markers(screen, x_min, x_max, y_min, y_max):
    for marker in MARKERS:
        screen_x, screen_y = complex_to_screen(
            marker['x'], marker['y'], x_min, x_max, y_min, y_max)

        # Draw the marker
        pygame.draw.circle(screen, MARKER_COLOR,
                           (screen_x, screen_y), MARKER_SIZE)

        # Render the label
        label_surface = render_text_with_background(
            marker['label'], pixel_font, MARKER_TEXT_COLOUR, (*MARKER_TEXT_BG_COLOUR, 180))
        label_pos = (
            screen_x + MARKER_LABEL_OFFSET[0], screen_y + MARKER_LABEL_OFFSET[1])
        screen.blit(label_surface, label_pos)


def jump_to_marker(index):
    global x_min, x_max, y_min, y_max, is_calc
    if 0 <= index < len(MARKERS):
        marker = MARKERS[index]
        center_x, center_y = marker['x'], marker['y']

        # Use the marker's zoom level if specified, otherwise use the default
        zoom_level = marker.get('zoom', DEFAULT_MARKER_ZOOM)

        # Calculate the view range based on the zoom level
        initial_range = INITIAL_X_MAX - INITIAL_X_MIN
        new_range = initial_range / zoom_level

        half_width = new_range / 2
        half_height = half_width / (WIDTH / HEIGHT)

        x_min, x_max = center_x - half_width, center_x + half_width
        y_min, y_max = center_y - half_height, center_y + half_height

        is_calc = True
        threading.Thread(target=calculate_mandelbrot_async, args=(
            RENDER_HEIGHT, RENDER_WIDTH, x_min, x_max, y_min, y_max)).start()


def reset_view():
    global x_min, x_max, y_min, y_max, is_calc
    x_min, x_max = INITIAL_X_MIN, INITIAL_X_MAX
    y_min, y_max = INITIAL_Y_MIN, INITIAL_Y_MAX
    is_calc = True
    threading.Thread(target=calculate_mandelbrot_async, args=(
        RENDER_HEIGHT, RENDER_WIDTH, x_min, x_max, y_min, y_max)).start()


def main():
    global x_min, x_max, y_min, y_max, mandelbrot_set, mandelbrot_surface, is_calc, drag_offset

    clock = pygame.time.Clock()
    running = True
    dragging = False
    start_pos = None
    drag_offset = (0, 0)

    # Create initial Mandelbrot set surface
    mandelbrot_set = mandelbrot(
        RENDER_HEIGHT, RENDER_WIDTH, x_min, x_max, y_min, y_max)
    mandelbrot_surface = create_mandelbrot_surface(mandelbrot_set)
    draw_markers(mandelbrot_surface, x_min, x_max, y_min, y_max)
    is_calc = False

    # Keep track of the previous view state
    prev_view = (x_min, x_max, y_min, y_max)

    # Variables for mouse text display
    last_mouse_move_time = time.time()
    mouse_text = ""

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    reset_view()
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    # Convert key to 0-based index
                    jump_to_marker(event.key - pygame.K_1)
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
                        RENDER_HEIGHT, RENDER_WIDTH, x_min, x_max, y_min, y_max)).start()
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
                        RENDER_HEIGHT, RENDER_WIDTH, x_min, x_max, y_min, y_max)).start()
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
                    # Check if the view has actually changed
                    current_view = (x_min, x_max, y_min, y_max)
                    if current_view != prev_view and not is_calc:
                        is_calc = True
                        threading.Thread(target=calculate_mandelbrot_async, args=(
                            RENDER_HEIGHT, RENDER_WIDTH, x_min, x_max, y_min, y_max)).start()
                    prev_view = current_view
            elif event.type == pygame.MOUSEMOTION:
                last_mouse_move_time = time.time()
                if dragging:
                    current_pos = event.pos
                    drag_offset = (
                        current_pos[0] - start_pos[0], current_pos[1] - start_pos[1])

                # Update mouse text
                mouse_x, mouse_y = event.pos
                mouse_complex_x, mouse_complex_y = screen_to_complex(
                    mouse_x - drag_offset[0], mouse_y - drag_offset[1], x_min, x_max, y_min, y_max)
                mouse_text = f"Mouse: X:{mouse_complex_x:.6f} Y:{mouse_complex_y:.6f}"

        screen.fill(VOID_COLOUR)  # Fill the screen with 'void' color

        # Draw the Mandelbrot set with the current drag offset
        screen.blit(mandelbrot_surface, drag_offset)

        # Calculate and display coordinates and zoom
        zoom = calculate_zoom(x_min, x_max, y_min, y_max)
        coord_text = f"Center: X:{(x_min + x_max) / 2:.6f} Y:{(y_min + y_max) / 2:.6f}, Zoom: {zoom:.0f}x"
        coord_surface = render_text_with_background(
            coord_text, pixel_font, TEXT_COLOUR, (*TEXT_BG_COLOUR, 180))
        screen.blit(coord_surface, (10, 10))

        # Display mouse coordinates if recently moved
        if time.time() - last_mouse_move_time < MOUSE_TEXT_DISPLAY_TIME:
            mouse_surface = render_text_with_background(
                mouse_text, pixel_font, TEXT_COLOUR, (*TEXT_BG_COLOUR, 180))
            screen.blit(mouse_surface, (10, 30))

        if is_calc:
            draw_calc_msg(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
