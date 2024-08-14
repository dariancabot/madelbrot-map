# Display settings
WIDTH = 800
HEIGHT = 600
PIXEL_DOUBLING = True

# Mandelbrot set parameters
MAX_ITER = 256
COASTLINE_ITER = 128
ZOOM_FACTOR = 0.5

# Colors
OCEAN_DEEP_COLOUR = (0, 0, 96)  # Dark blue for deep ocean
OCEAN_SHALLOW_COLOUR = (32, 64, 128)  # Lighter blue for underwater detail
LAND_COLOUR = (245, 222, 179)  # Wheat colour for land
VOID_COLOUR = (128, 128, 128)  # Grey for void when dragging
TEXT_COLOUR = LAND_COLOUR
TEXT_BG_COLOUR = (128, 96, 32)

PIXEL_FONT_SIZE = 8
NORMAL_FONT_SIZE = 24

# Wave texture settings
WAVE_SIZE = 32
WAVE_COLOUR = OCEAN_SHALLOW_COLOUR  # Wave crests

# Markers
MARKERS = [
    {"x": -0.75, "y": 0, "label": "Cardioid Center"},
    {"x": -1, "y": 0.25, "label": "Period-2 Bulb"},
    {"x": -0.125, "y": 0.744, "label": "Mini Mandelbrot"},
]

MARKER_COLOR = (255, 0, 0)  # Red
MARKER_SIZE = 5  # Pixels
MARKER_LABEL_OFFSET = (5, 5)  # Offset for label from marker
MARKER_TEXT_COLOUR = TEXT_COLOUR
MARKER_TEXT_BG_COLOUR = (16, 24, 32)
