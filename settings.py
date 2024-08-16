# Display settings
WIDTH = 800
HEIGHT = 600
PIXEL_DOUBLING = True

# Mandelbrot set parameters
MAX_ITER = 512
COASTLINE_ITER = 256
ZOOM_FACTOR = 0.5

# Colors
OCEAN_DEEP_COLOUR = (0, 0, 96)  # Dark blue for deep ocean
OCEAN_SHALLOW_COLOUR = (32, 64, 128)  # Lighter blue for underwater detail
LAND_COLOUR = (245, 222, 179)  # Wheat colour for land
OUTLINE_COLOUR = (128, 192, 224)
VOID_COLOUR = (128, 128, 128)  # Grey for void when dragging
TEXT_COLOUR = LAND_COLOUR
TEXT_BG_COLOUR = (128, 96, 32)

PIXEL_FONT_SIZE = 8
NORMAL_FONT_SIZE = 24

MOUSE_TEXT_DISPLAY_TIME = 3  # seconds to display mouse text after movement

# Wave texture settings
WAVE_SIZE = 32
WAVE_COLOUR = OCEAN_SHALLOW_COLOUR  # Wave crests

# Markers
MARKERS = [
    {"x": -1.39918, "y": 0.00251, "zoom": 2048, "label": "Village"},
    {"x": -1.396855, "y": 0.0, "zoom": 256, "label": "Bay"},
    {"x": -1.394155, "y": 0.001225, "zoom": 512, "label": "South peninsula"},
    {"x": 0.3968, "y": 0.2291, "zoom": 256, "label": "Great city"},
]

MARKER_COLOR = (255, 0, 0)  # Red
MARKER_SIZE = 5  # Pixels
MARKER_LABEL_OFFSET = (5, 5)  # Offset for label from marker
MARKER_TEXT_COLOUR = TEXT_COLOUR
MARKER_TEXT_BG_COLOUR = (16, 24, 32)
DEFAULT_MARKER_ZOOM = 128

# Initial view settings
INITIAL_X_MIN, INITIAL_X_MAX = -2.0, 1.0
INITIAL_Y_RANGE = (INITIAL_X_MAX - INITIAL_X_MIN) / (WIDTH / HEIGHT)
INITIAL_Y_MIN, INITIAL_Y_MAX = -INITIAL_Y_RANGE / 2, INITIAL_Y_RANGE / 2
