import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import io
import random
import math
import zipfile
from datetime import datetime
import json
import os

# Preferences file path
PREFERENCES_FILE = "user_preferences.json"

def load_preferences():
    """Load user mark type preferences from file."""
    default_prefs = {
        'blob': 1.0,
        'water_stain': 1.0,
        'fingerprint': 1.0,
        'dust': 1.0,
        'streak': 1.0,
        'bleeding_ink': 1.0,
        'faded_ink': 1.0,
        'smudged_calligraphy': 1.0,
        'moisture_damage': 1.0,
        'soot_stain': 1.0,
        'atmospheric_grime': 1.0,
        'coffee_mark': 1.0,
        'muddy_mark': 1.0,
        'heavy_ink_blotch': 1.0,
        'age_rings': 1.0,
        'ink_halo': 1.0,
        'foxing_spots': 1.0,
        'uneven_fading': 1.0,
        'text_area_smudge': 1.0,
        'rust_stains': 1.0,
        'dark_damage': 1.0
    }
    
    if os.path.exists(PREFERENCES_FILE):
        try:
            with open(PREFERENCES_FILE, 'r') as f:
                prefs = json.load(f)
                # Merge with defaults to handle new mark types
                default_prefs.update(prefs)
                return default_prefs
        except:
            return default_prefs
    return default_prefs

def save_preferences(preferences):
    """Save user preferences to file."""
    with open(PREFERENCES_FILE, 'w') as f:
        json.dump(preferences, f, indent=2)

def adjust_preferences(mark_types_used, liked):
    """Adjust mark type weights based on user feedback."""
    preferences = load_preferences()
    
    # Adjust weights for used mark types
    for mark_type in mark_types_used:
        if mark_type in preferences:
            if liked:
                preferences[mark_type] *= 1.3  # Increase by 30% if liked
            else:
                preferences[mark_type] *= 0.7  # Decrease by 30% if disliked
                preferences[mark_type] = max(0.1, preferences[mark_type])  # Minimum 0.1
    
    # Normalize so they average to 1.0
    avg_pref = sum(preferences.values()) / len(preferences)
    preferences = {k: v / avg_pref for k, v in preferences.items()}
    
    save_preferences(preferences)
    return preferences

def generate_similar_images(image, liked_marks, num_variations=3, num_smudges=8, intensity=0.7, aging_level='medium'):
    """
    Generate multiple variations biased toward the liked mark types.
    
    Args:
        image: Original PIL Image
        liked_marks: List of mark types the user liked
        num_variations: How many similar images to generate
        num_smudges: Number of marks per image
        intensity: Mark intensity
        aging_level: Aging level setting
    
    Returns:
        List of (processed_image, marks_used) tuples
    """
    results = []
    for _ in range(num_variations):
        # Temporarily boost preferences for liked marks
        preferences = load_preferences()
        boosted = preferences.copy()
        for mark in liked_marks:
            if mark in boosted:
                boosted[mark] *= 3.0  # Triple the weight for liked types
        
        # Normalize
        avg = sum(boosted.values()) / len(boosted)
        boosted = {k: v / avg for k, v in boosted.items()}
        
        # Temporarily save boosted preferences
        save_preferences(boosted)
        
        # Generate image
        processed, marks_used = apply_smudges(
            image, num_smudges=num_smudges,
            intensity=intensity, aging_level=aging_level
        )
        results.append((processed, marks_used))
        
        # Restore original preferences
        save_preferences(preferences)
    
    return results

# Page configuration
st.set_page_config(
    page_title="Ancient Manuscript Authenticator",
    page_icon="📜",
    layout="wide"
)

# Initialize session state for feedback tracking
if 'feedback_given' not in st.session_state:
    st.session_state['feedback_given'] = {}  # {idx: 'like' or 'dislike'}
if 'similar_images' not in st.session_state:
    st.session_state['similar_images'] = {}  # {idx: [list of similar processed images]}
if 'generation_mode' not in st.session_state:
    st.session_state['generation_mode'] = 'random'  # 'random' or 'preferred'

# Custom CSS for academic/historical styling
st.markdown("""
<style>
    .main {
        background-color: #f5f1e8;
    }
    .stTitle {
        color: #4a3c2a;
        font-family: 'Georgia', serif;
    }
    .stMarkdown {
        font-family: 'Georgia', serif;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📜 Ancient Manuscript Authenticator")
st.markdown("""
*Transform modern text into authentically weathered historical documents*

This tool applies **randomized, organic aging effects** to clean manuscript images, creating unique 
centuries-old appearances. Each processing generates a different pattern using varied mark types, 
colors, shapes, and natural placement. Perfect for Devanagari and Sanskrit texts.

**✨ New Features:**
- 🖼️ **Batch Processing**: Process up to 10 images simultaneously
- 📥 **Multiple Formats**: Download in PNG, JPEG, BMP, or TIFF
- 🎯 **DPI Control**: Choose resolution for screen (72 DPI), print (300 DPI), or archival (600 DPI)
- ⬇️ **Bulk Download**: Download all processed images as a ZIP file in one click
- 👍👎 **Like/Dislike Feedback**: Rate each result — liked mark types appear more often in future generations
- 🔄 **Generate Similar**: After liking an image, instantly generate more variations with the same mark types
""")

def draw_irregular_shape(draw, bbox, fill=None, outline=None, width=1, num_points=None):
    """Draw an irregular, organic shape instead of a perfect ellipse.
    Uses many control points with strong randomised wobble, random aspect
    ratio skew, and per-point jitter so no two shapes look alike.
    Only filled shapes are drawn — outline parameter is accepted but ignored
    to prevent geometric semi-circle artefacts.
    """
    x0, y0, x1, y1 = bbox
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    rx = (x1 - x0) / 2.0
    ry = (y1 - y0) / 2.0
    
    if rx < 3 or ry < 3:
        if fill is not None:
            draw.ellipse(bbox, fill=fill)
        return
    
    # Randomise aspect ratio so shapes are never perfectly round/square
    aspect_skew = random.uniform(0.55, 1.45)
    rx *= aspect_skew
    ry *= (2.0 - aspect_skew)  # inverse stretch on other axis
    
    if num_points is None:
        num_points = random.randint(18, 32)  # more points = smoother organic edge
    
    # Multiple harmonics for complex wobble
    num_harmonics = random.randint(3, 5)
    freqs = [random.uniform(1.0, 6.0) for _ in range(num_harmonics)]
    phases = [random.uniform(0, 6.28) for _ in range(num_harmonics)]
    amps = [random.uniform(0.06, 0.22) for _ in range(num_harmonics)]
    
    # Optional rotation of the whole shape
    rot = random.uniform(0, 6.28)
    cos_rot = math.cos(rot)
    sin_rot = math.sin(rot)
    
    points = []
    step = 6.2831853 / num_points
    for i in range(num_points):
        a = step * i + random.uniform(-0.25, 0.25)  # stronger angular jitter
        # Sum multiple harmonics
        r = 1.0
        for h in range(num_harmonics):
            r += amps[h] * math.sin(freqs[h] * a + phases[h])
        # Per-point random jitter
        r *= random.uniform(0.72, 1.22)
        r = max(0.3, min(r, 1.5))
        # Local coordinates
        lx = rx * r * math.cos(a)
        ly = ry * r * math.sin(a)
        # Apply rotation
        px = cx + lx * cos_rot - ly * sin_rot
        py = cy + lx * sin_rot + ly * cos_rot
        points.append((px, py))
    
    if fill is not None:
        draw.polygon(points, fill=fill)

def create_organic_blob(size, irregularity=0.3):
    """Create an organic, irregular blob-shaped smudge with varied aspect ratios."""
    canvas_size = int(size * 2.5)
    smudge = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(smudge)
    
    center = canvas_size // 2
    num_circles = random.randint(10, 20)
    
    for _ in range(num_circles):
        offset_x = random.randint(-int(size * irregularity * 1.3), int(size * irregularity * 1.3))
        offset_y = random.randint(-int(size * irregularity * 1.3), int(size * irregularity * 1.3))
        # Randomise width and height independently for non-circular sub-shapes
        radius_x = random.randint(int(size * 0.2), int(size * 0.8))
        radius_y = random.randint(int(size * 0.15), int(size * 0.7))
        
        x0 = center + offset_x - radius_x
        y0 = center + offset_y - radius_y
        x1 = center + offset_x + radius_x
        y1 = center + offset_y + radius_y
        
        opacity = random.randint(60, 160)
        draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)
    
    smudge = smudge.filter(ImageFilter.GaussianBlur(radius=size * 0.20))
    smudge = smudge.filter(ImageFilter.GaussianBlur(radius=size * 0.12))
    
    smudge_array = np.array(smudge)
    noise = np.random.randint(-25, 25, smudge_array.shape)
    smudge_array = np.clip(smudge_array.astype(int) + noise, 0, 255).astype(np.uint8)
    smudge = Image.fromarray(smudge_array)
    
    # Random rotation so blob is never axis-aligned
    angle = random.randint(0, 360)
    smudge = smudge.rotate(angle, expand=False, fillcolor=0)
    
    return smudge

def create_water_stain(size):
    """Create a water stain with wick/tide-line effect — darker concentrated
    borders where liquid evaporated, semi-transparent interior, and variable
    opacity zones (dense opaque areas + ghost regions)."""
    canvas_size = int(size * 3.0)
    stain = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(stain)
    
    center = canvas_size // 2
    
    # --- 1. Build interior fill: variable transparency pools ---
    num_pools = random.randint(6, 14)
    for i in range(num_pools):
        pool_rx = random.randint(int(size * 0.20), int(size * 0.85))
        pool_ry = random.randint(int(size * 0.15), int(size * 0.80))
        
        for _ in range(random.randint(3, 6)):
            offset_x = random.randint(-int(size * 0.55), int(size * 0.55))
            offset_y = random.randint(-int(size * 0.55), int(size * 0.55))
            
            # Variable transparency: some pools are dense/opaque, others are ghost-faint
            if random.random() < 0.3:
                # Dense opaque region — obscures text
                opacity = random.randint(120, 200)
            elif random.random() < 0.5:
                # Medium — text partially visible
                opacity = random.randint(55, 119)
            else:
                # Ghost stain — text remains visible
                opacity = random.randint(18, 54)
            
            x0 = center + offset_x - pool_rx
            y0 = center + offset_y - pool_ry
            x1 = center + offset_x + pool_rx
            y1 = center + offset_y + pool_ry
            
            draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)
    
    # --- 2. Wick / tide-line effect: scattered filled blobs along the perimeter ---
    # (Using filled blobs instead of outline rings to avoid geometric semi-circle appearance)
    num_tide_blobs = random.randint(30, 70)
    for _ in range(num_tide_blobs):
        # Place blobs in a band around the stain perimeter
        tide_angle = random.uniform(0, 6.28)
        tide_rx = random.randint(int(size * 0.55), int(size * 1.1))
        tide_ry = random.randint(int(size * 0.45), int(size * 1.0))
        # Scatter along the perimeter with some variance
        tide_dist_x = tide_rx * (1.0 + random.gauss(0, 0.12))
        tide_dist_y = tide_ry * (1.0 + random.gauss(0, 0.12))
        tx = int(center + tide_dist_x * math.cos(tide_angle))
        ty = int(center + tide_dist_y * math.sin(tide_angle))
        # Small filled blobs for the tide line
        tr_x = random.randint(max(2, int(size * 0.02)), max(4, int(size * 0.08)))
        tr_y = random.randint(max(2, int(size * 0.02)), max(4, int(size * 0.07)))
        tide_opacity = random.randint(100, 200)
        if 0 < tx < canvas_size and 0 < ty < canvas_size:
            draw_irregular_shape(draw,
                [tx - tr_x, ty - tr_y, tx + tr_x, ty + tr_y],
                fill=tide_opacity
            )
    
    # --- 3. Spatter dots around the stain edges ---
    num_droplets = random.randint(8, 25)
    for _ in range(num_droplets):
        angle = random.uniform(0, 6.28)
        dist = random.gauss(size * 0.8, size * 0.3)
        dx = int(center + dist * math.cos(angle))
        dy = int(center + dist * math.sin(angle))
        dot_r = random.randint(1, max(2, int(size * 0.04)))
        dot_opacity = random.randint(80, 190)
        if 0 < dx < canvas_size and 0 < dy < canvas_size:
            draw_irregular_shape(draw,
                [dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r],
                fill=dot_opacity)
    
    stain = stain.filter(ImageFilter.GaussianBlur(radius=size * 0.22))
    # Random rotation for unique orientation
    angle = random.randint(0, 360)
    stain = stain.rotate(angle, expand=False, fillcolor=0)
    return stain

def create_bleeding_ink(size):
    """Create a soft, feathered ink bleed."""
    canvas_size = int(size * 2.2)
    bleed = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(bleed)

    center = canvas_size // 2
    num_blobs = random.randint(8, 16)

    for _ in range(num_blobs):
        offset_x = random.randint(-int(size * 0.6), int(size * 0.6))
        offset_y = random.randint(-int(size * 0.6), int(size * 0.6))
        radius_x = random.randint(int(size * 0.2), int(size * 0.85))
        radius_y = random.randint(int(size * 0.15), int(size * 0.75))

        x0 = center + offset_x - radius_x
        y0 = center + offset_y - radius_y
        x1 = center + offset_x + radius_x
        y1 = center + offset_y + radius_y

        opacity = random.randint(50, 130)
        draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)

    bleed = bleed.filter(ImageFilter.GaussianBlur(radius=size * 0.30))
    bleed = bleed.filter(ImageFilter.GaussianBlur(radius=size * 0.15))
    angle = random.randint(0, 360)
    bleed = bleed.rotate(angle, expand=False, fillcolor=0)
    return bleed

def create_coffee_ring(size):
    """Create a coffee ring stain with a darker edge."""
    canvas_size = int(size * 2.6)
    ring = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(ring)

    center = canvas_size // 2
    outer_x = int(size * random.uniform(0.9, 1.3))
    outer_y = int(size * random.uniform(0.7, 1.2))
    inner_x = int(outer_x * random.uniform(0.5, 0.75))
    inner_y = int(outer_y * random.uniform(0.5, 0.75))

    for _ in range(random.randint(6, 12)):
        jitter_x = random.randint(-size // 3, size // 3)
        jitter_y = random.randint(-size // 3, size // 3)

        draw_irregular_shape(draw,
            [center + jitter_x - outer_x, center + jitter_y - outer_y,
             center + jitter_x + outer_x, center + jitter_y + outer_y],
            fill=random.randint(50, 120)
        )
        draw_irregular_shape(draw,
            [center + jitter_x - inner_x, center + jitter_y - inner_y,
             center + jitter_x + inner_x, center + jitter_y + inner_y],
            fill=random.randint(10, 45)
        )

    ring = ring.filter(ImageFilter.GaussianBlur(radius=size * 0.25))
    angle = random.randint(0, 360)
    ring = ring.rotate(angle, expand=False, fillcolor=0)
    return ring

def create_soot_stain(size):
    """Create a smoky soot stain."""
    canvas_size = int(size * 2.4)
    soot = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(soot)

    center = canvas_size // 2
    num_clouds = random.randint(12, 24)

    for _ in range(num_clouds):
        offset_x = random.randint(-int(size * 0.8), int(size * 0.8))
        offset_y = random.randint(-int(size * 0.8), int(size * 0.8))
        radius_x = random.randint(int(size * 0.15), int(size * 0.6))
        radius_y = random.randint(int(size * 0.1), int(size * 0.55))
        opacity = random.randint(35, 90)

        x0 = center + offset_x - radius_x
        y0 = center + offset_y - radius_y
        x1 = center + offset_x + radius_x
        y1 = center + offset_y + radius_y

        draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)

    soot = soot.filter(ImageFilter.GaussianBlur(radius=size * 0.40))
    angle = random.randint(0, 360)
    soot = soot.rotate(angle, expand=False, fillcolor=0)
    return soot

def create_heavy_ink_blotch(size):
    """Create a large, irregular ink blotch with variable transparency,
    darker wick borders, and splatter droplets around the edges."""
    canvas_size = int(size * 2.8)
    blot = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(blot)

    center = canvas_size // 2
    base_radius = int(size * 0.9)

    # Core blob with variable transparency
    for _ in range(random.randint(12, 22)):
        offset_x = random.randint(-int(size * 0.6), int(size * 0.6))
        offset_y = random.randint(-int(size * 0.6), int(size * 0.6))
        radius_x = random.randint(int(base_radius * 0.3), int(base_radius * 0.95))
        radius_y = random.randint(int(base_radius * 0.25), int(base_radius * 0.9))
        # Variable transparency — safe with multiply blend
        if random.random() < 0.35:
            opacity = random.randint(170, 245)  # dense core
        elif random.random() < 0.5:
            opacity = random.randint(90, 169)   # semi-transparent
        else:
            opacity = random.randint(30, 89)    # ghost stain

        draw_irregular_shape(draw,
            [center + offset_x - radius_x, center + offset_y - radius_y,
             center + offset_x + radius_x, center + offset_y + radius_y],
            fill=opacity
        )

    # Wick effect: scattered filled blobs along the border (not outline rings)
    num_wick_blobs = random.randint(25, 55)
    for _ in range(num_wick_blobs):
        wick_angle = random.uniform(0, 6.28)
        wick_rx = base_radius * random.uniform(0.75, 1.3)
        wick_ry = base_radius * random.uniform(0.65, 1.2)
        wx = int(center + wick_rx * math.cos(wick_angle) * (1.0 + random.gauss(0, 0.1)))
        wy = int(center + wick_ry * math.sin(wick_angle) * (1.0 + random.gauss(0, 0.1)))
        wr_x = random.randint(max(2, int(size * 0.02)), max(4, int(size * 0.07)))
        wr_y = random.randint(max(2, int(size * 0.015)), max(4, int(size * 0.06)))
        wick_opacity = random.randint(120, 220)
        if 0 < wx < canvas_size and 0 < wy < canvas_size:
            draw_irregular_shape(draw,
                [wx - wr_x, wy - wr_y, wx + wr_x, wy + wr_y],
                fill=wick_opacity
            )

    # Splatter droplets — small dots scattered around the stain edges
    for _ in range(random.randint(15, 35)):
        angle = random.uniform(0, 6.28)
        dist = random.gauss(base_radius * 1.1, base_radius * 0.3)
        dot_x = int(center + dist * math.cos(angle))
        dot_y = int(center + dist * math.sin(angle))
        dot_size = random.randint(1, max(2, int(size * 0.04)))
        opacity = random.randint(80, 200)
        if 0 < dot_x < canvas_size and 0 < dot_y < canvas_size:
            draw_irregular_shape(draw, [dot_x - dot_size, dot_y - dot_size, dot_x + dot_size, dot_y + dot_size], fill=opacity)

    blot = blot.filter(ImageFilter.GaussianBlur(radius=size * 0.22))
    angle = random.randint(0, 360)
    blot = blot.rotate(angle, expand=False, fillcolor=0)
    return blot

def create_atmospheric_grime(size):
    """Create a diffuse grime patch with soft texture."""
    canvas_size = int(size * 2.4)
    grime = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(grime)

    center = canvas_size // 2
    num_spots = random.randint(15, 28)

    for _ in range(num_spots):
        offset_x = random.randint(-int(size * 0.9), int(size * 0.9))
        offset_y = random.randint(-int(size * 0.9), int(size * 0.9))
        radius_x = random.randint(int(size * 0.12), int(size * 0.55))
        radius_y = random.randint(int(size * 0.10), int(size * 0.50))
        opacity = random.randint(25, 80)

        x0 = center + offset_x - radius_x
        y0 = center + offset_y - radius_y
        x1 = center + offset_x + radius_x
        y1 = center + offset_y + radius_y

        draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)

    grime = grime.filter(ImageFilter.GaussianBlur(radius=size * 0.35))
    angle = random.randint(0, 360)
    grime = grime.rotate(angle, expand=False, fillcolor=0)
    return grime

def create_torn_paper_edge(width, height):
    """Create torn/ragged paper edges along document borders. Fast numpy version."""
    torn_array = np.full((height, width), 255, dtype=np.float32)

    max_tear = 25
    # Top edge: random tear depth per column
    tear_offsets = np.random.randint(0, max_tear + 1, size=width)
    tear_intensities = np.random.randint(80, 201, size=width).astype(np.float32)
    rows = np.arange(height).reshape(-1, 1)  # (H, 1)
    top_mask = rows < tear_offsets.reshape(1, -1)  # (H, W)
    torn_array[top_mask] = np.broadcast_to(tear_intensities, (height, width))[top_mask]

    # Bottom edge
    tear_offsets = np.random.randint(0, max_tear + 1, size=width)
    tear_intensities = np.random.randint(80, 201, size=width).astype(np.float32)
    bottom_mask = rows > (height - 1 - tear_offsets).reshape(1, -1)
    torn_array[bottom_mask] = np.broadcast_to(tear_intensities, (height, width))[bottom_mask]

    # Left edge
    cols = np.arange(width).reshape(1, -1)  # (1, W)
    tear_offsets = np.random.randint(0, max_tear + 1, size=height)
    tear_intensities = np.random.randint(80, 201, size=height).astype(np.float32)
    left_mask = cols < tear_offsets.reshape(-1, 1)
    torn_array[left_mask] = np.broadcast_to(tear_intensities.reshape(-1, 1), (height, width))[left_mask]

    # Right edge
    tear_offsets = np.random.randint(0, max_tear + 1, size=height)
    tear_intensities = np.random.randint(80, 201, size=height).astype(np.float32)
    right_mask = cols > (width - 1 - tear_offsets).reshape(-1, 1)
    torn_array[right_mask] = np.broadcast_to(tear_intensities.reshape(-1, 1), (height, width))[right_mask]

    # Add irregular jagged noise
    edge_noise = np.random.randint(-30, 30, (height, width), dtype=np.int16)
    torn_array = np.clip(torn_array + edge_noise * 0.3, 0, 255)

    torn = Image.fromarray(torn_array.astype(np.uint8))
    torn = torn.filter(ImageFilter.GaussianBlur(radius=1.5))
    return torn

def create_age_rings(size):
    """Create irregular age staining — overlapping organic blobs with variable
    opacity that mimic the mottled discolouration seen on old manuscripts.
    No concentric circles or sinusoidal rings — purely organic shapes."""
    canvas_size = int(size * 2.2)
    center = canvas_size // 2
    base_radius = int(size * 0.7)
    
    age = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(age)
    
    # Layer 1: large soft blotches for overall staining
    num_large = random.randint(6, 14)
    for _ in range(num_large):
        angle = random.uniform(0, 6.28)
        dist = abs(random.gauss(0, base_radius * 0.5))
        bx = int(center + dist * math.cos(angle))
        by = int(center + dist * math.sin(angle))
        br = random.randint(int(base_radius * 0.15), int(base_radius * 0.45))
        fade = max(0.2, 1.0 - dist / base_radius)
        opacity = int(random.randint(30, 75) * fade)
        x0, y0 = bx - br, by - br
        x1, y1 = bx + br, by + br
        draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)
    
    # Layer 2: medium patches for variation
    num_med = random.randint(10, 25)
    for _ in range(num_med):
        angle = random.uniform(0, 6.28)
        dist = abs(random.gauss(0, base_radius * 0.6))
        bx = int(center + dist * math.cos(angle))
        by = int(center + dist * math.sin(angle))
        br = random.randint(int(base_radius * 0.06), int(base_radius * 0.22))
        fade = max(0.15, 1.0 - dist / base_radius)
        opacity = int(random.randint(20, 55) * fade)
        x0, y0 = bx - br, by - br
        x1, y1 = bx + br, by + br
        draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)
    
    # Layer 3: tiny speckles for texture
    num_tiny = random.randint(20, 50)
    for _ in range(num_tiny):
        tx = random.randint(center - base_radius, center + base_radius)
        ty = random.randint(center - base_radius, center + base_radius)
        tr = random.randint(1, max(3, int(base_radius * 0.05)))
        dist_from_ctr = math.sqrt((tx - center)**2 + (ty - center)**2)
        if dist_from_ctr < base_radius:
            fade = max(0.1, 1.0 - dist_from_ctr / base_radius)
            opacity = int(random.randint(15, 45) * fade)
            draw.ellipse([tx - tr, ty - tr, tx + tr, ty + tr], fill=opacity)
    
    age = age.filter(ImageFilter.GaussianBlur(radius=size * 0.15))
    # Random rotation for variety
    age = age.rotate(random.randint(0, 360), expand=False, fillcolor=0)
    return age

def create_ink_halo(size):
    """Create a soft ink seepage halo around text. Fast numpy version."""
    canvas_size = int(size * 2.4)
    center = canvas_size // 2
    base_radius = int(size * 0.8)
    
    # Build radial gradient with numpy
    y_idx, x_idx = np.ogrid[:canvas_size, :canvas_size]
    dist = np.sqrt((x_idx - center)**2 + (y_idx - center)**2).astype(np.float32)
    
    # Soft halo: opacity falls off from centre
    halo_array = np.zeros((canvas_size, canvas_size), dtype=np.float32)
    within = dist < base_radius
    halo_array[within] = 80 * (1.0 - dist[within] / base_radius) ** 0.8
    
    # Add noise
    noise = np.random.randint(-8, 8, halo_array.shape, dtype=np.int16)
    halo_array = np.clip(halo_array + noise, 0, 255).astype(np.uint8)
    
    halo = Image.fromarray(halo_array)
    halo = halo.filter(ImageFilter.GaussianBlur(radius=size * 0.35))
    return halo

def create_foxing_spots(size):
    """Create foxing - brown aging spots common in old manuscripts."""
    canvas_size = int(size * 2)
    foxing = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(foxing)
    
    center = canvas_size // 2
    num_spots = random.randint(4, 10)
    
    for _ in range(num_spots):
        offset_x = random.randint(-int(size * 0.5), int(size * 0.5))
        offset_y = random.randint(-int(size * 0.5), int(size * 0.5))
        spot_rx = random.randint(int(size * 0.10), int(size * 0.45))
        spot_ry = random.randint(int(size * 0.08), int(size * 0.40))
        opacity = random.randint(70, 130)
        
        x0 = center + offset_x - spot_rx
        y0 = center + offset_y - spot_ry
        x1 = center + offset_x + spot_rx
        y1 = center + offset_y + spot_ry
        
        draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)
    
    foxing = foxing.filter(ImageFilter.GaussianBlur(radius=size * 0.20))
    return foxing

def create_moisture_tide_mark(width, height):
    """Create horizontal tide marks from water damage."""
    tide = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(tide)
    
    # Create 1-3 horizontal bands
    num_bands = random.randint(1, 3)
    for _ in range(num_bands):
        y_pos = random.randint(int(height * 0.2), int(height * 0.8))
        band_height = random.randint(15, 40)
        opacity_start = random.randint(60, 120)
        
        # Gradient from top to bottom of band
        for offset in range(band_height):
            opacity = int(opacity_start * (1 - offset / band_height) ** 1.5)
            if opacity > 10:
                draw.line(
                    [(0, y_pos + offset), (width, y_pos + offset)],
                    fill=opacity,
                    width=1
                )
    
    tide = tide.filter(ImageFilter.GaussianBlur(radius=2))
    return tide

def create_uneven_fading(size):
    """Create patches of uneven fading - lighter/darker areas."""
    canvas_size = int(size * 2.6)
    fade = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(fade)
    
    center = canvas_size // 2
    num_patches = random.randint(5, 12)
    
    for _ in range(num_patches):
        offset_x = random.randint(-int(size * 0.8), int(size * 0.8))
        offset_y = random.randint(-int(size * 0.8), int(size * 0.8))
        patch_rx = random.randint(int(size * 0.2), int(size * 0.75))
        patch_ry = random.randint(int(size * 0.15), int(size * 0.7))
        opacity = random.randint(30, 85)
        
        x0 = center + offset_x - patch_rx
        y0 = center + offset_y - patch_ry
        x1 = center + offset_x + patch_rx
        y1 = center + offset_y + patch_ry
        
        draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)
    
    fade = fade.filter(ImageFilter.GaussianBlur(radius=size * 0.40))
    angle = random.randint(0, 360)
    fade = fade.rotate(angle, expand=False, fillcolor=0)
    return fade

def create_rust_stains(width, height):
    """Create rust/oxidation stains on margins and edges."""
    rust = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(rust)
    
    # Rust stains primarily on left/right edges and corners
    for _ in range(random.randint(3, 7)):
        edge_choice = random.choice(['left', 'right', 'corner'])
        
        if edge_choice == 'left':
            x_start = random.randint(0, int(width * 0.15))
            y_start = random.randint(0, height)
        elif edge_choice == 'right':
            x_start = random.randint(int(width * 0.85), width)
            y_start = random.randint(0, height)
        else:  # corner
            corner = random.choice(['top-left', 'top-right', 'bottom-left', 'bottom-right'])
            if corner == 'top-left':
                x_start = random.randint(0, int(width * 0.2))
                y_start = random.randint(0, int(height * 0.2))
            elif corner == 'top-right':
                x_start = random.randint(int(width * 0.8), width)
                y_start = random.randint(0, int(height * 0.2))
            elif corner == 'bottom-left':
                x_start = random.randint(0, int(width * 0.2))
                y_start = random.randint(int(height * 0.8), height)
            else:
                x_start = random.randint(int(width * 0.8), width)
                y_start = random.randint(int(height * 0.8), height)
        
        # Create stain spread
        stain_width = random.randint(20, 80)
        stain_height = random.randint(30, 150)
        
        for _ in range(random.randint(5, 12)):
            offset_x = random.randint(-stain_width, stain_width)
            offset_y = random.randint(-stain_height, stain_height)
            spot_radius = random.randint(5, 20)
            opacity = random.randint(60, 140)
            
            cx = x_start + offset_x
            cy = y_start + offset_y
            
            if 0 <= cx < width and 0 <= cy < height:
                draw_irregular_shape(draw, [cx - spot_radius, cy - spot_radius, cx + spot_radius, cy + spot_radius], fill=int(opacity * 0.5))
    
    rust = rust.filter(ImageFilter.GaussianBlur(radius=5))
    return rust

def create_text_area_smudge(size):
    """Create smudges and halos around text areas."""
    canvas_size = int(size * 2.5)
    smudge = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(smudge)
    
    center = canvas_size // 2
    
    # Create irregular text-like smudge pattern
    num_marks = random.randint(5, 12)
    for _ in range(num_marks):
        mark_x = random.randint(int(center * 0.3), int(center * 1.7))
        mark_y = random.randint(int(center * 0.1), int(center * 1.9))
        mark_width = random.randint(int(size * 0.2), int(size * 0.9))
        mark_height = random.randint(int(size * 0.1), int(size * 0.6))
        opacity = random.randint(30, 90)
        
        draw_irregular_shape(draw, [mark_x - mark_width, mark_y - mark_height, mark_x + mark_width, mark_y + mark_height], fill=opacity)
    
    smudge = smudge.filter(ImageFilter.GaussianBlur(radius=size * 0.35))
    angle = random.randint(0, 360)
    smudge = smudge.rotate(angle, expand=False, fillcolor=0)
    return smudge

def create_edge_darkening(width, height):
    """Create dramatic organic edge darkening simulating oxidation and handling.
    Produces wide, irregular gradients shifting from cream to near-black at the
    very edges, with heavy corner blotches — matching authentic aged manuscripts."""
    min_dim = min(width, height)
    edge_width = random.randint(int(min_dim * 0.06), int(min_dim * 0.20))
    
    # Build distance-from-edge map
    y_coords = np.arange(height).reshape(-1, 1).astype(np.float32)
    x_coords = np.arange(width).reshape(1, -1).astype(np.float32)
    
    dist_top = y_coords
    dist_bottom = (height - 1) - y_coords
    dist_left = x_coords
    dist_right = (width - 1) - x_coords
    
    min_dist = np.minimum(np.minimum(dist_top, dist_bottom), np.minimum(dist_left, dist_right))
    
    # Organic wobble via coarse noise
    noise_h = max(4, height // 28)
    noise_w = max(4, width // 28)
    coarse_noise = np.random.uniform(-0.5, 0.5, (noise_h, noise_w)).astype(np.float32)
    noise_img = Image.fromarray(((coarse_noise + 0.5) * 255).astype(np.uint8), mode='L')
    noise_img = noise_img.resize((width, height), Image.BILINEAR)
    noise_full = (np.array(noise_img).astype(np.float32) / 255.0 - 0.5) * 2.0
    
    wobble_amplitude = edge_width * 0.6
    warped_dist = min_dist + noise_full * wobble_amplitude
    
    # Convert to opacity: fade from 230 at edge → 0 at interior
    edge_mask = np.clip(1.0 - warped_dist / edge_width, 0, 1)
    edge_arr = (edge_mask ** 1.3) * 230
    
    # Fine noise for organic grain
    fine_noise = np.random.randint(-15, 16, (height, width)).astype(np.float32)
    edge_arr = np.clip(edge_arr + fine_noise * edge_mask, 0, 255)
    
    edges = Image.fromarray(edge_arr.astype(np.uint8), mode='L')
    draw = ImageDraw.Draw(edges)
    
    # Heavy corner blotches — much larger with higher opacity
    corner_radius = int(min_dim * random.uniform(0.08, 0.22))
    for (cx, cy) in [(0, 0), (width, 0), (0, height), (width, height)]:
        num_blobs = random.randint(8, 18)
        for _ in range(num_blobs):
            bx = cx + random.randint(-corner_radius, corner_radius)
            by = cy + random.randint(-corner_radius, corner_radius)
            br = random.randint(corner_radius // 3, corner_radius)
            bop = random.randint(120, 240)
            x0 = max(0, bx - br)
            y0 = max(0, by - br)
            x1 = min(width, bx + br)
            y1 = min(height, by + br)
            if x1 > x0 + 2 and y1 > y0 + 2:
                draw_irregular_shape(draw, [x0, y0, x1, y1], fill=bop)
    
    edges = edges.filter(ImageFilter.GaussianBlur(radius=max(3, edge_width // 4)))
    return edges

def create_fingerprint_mark(size):
    """Create a fingerprint/touch mark - smeared, elongated."""
    canvas_size = int(size * 2)
    mark = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(mark)
    
    center = canvas_size // 2
    # Create fingerprint-like ridges
    num_ridges = random.randint(4, 7)
    
    for i in range(num_ridges):
        offset = random.randint(-size // 4, size // 4)
        width = random.randint(int(size * 0.1), int(size * 0.2))
        length = int(size * random.uniform(0.6, 1.2))
        
        x0 = center - length // 2
        y0 = center + offset - width // 2
        x1 = center + length // 2
        y1 = center + offset + width // 2
        
        opacity = random.randint(35, 80)
        draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)
    
    mark = mark.filter(ImageFilter.GaussianBlur(radius=size * 0.15))
    # Random rotation
    angle = random.randint(0, 360)
    mark = mark.rotate(angle, expand=False)
    
    return mark

def create_dust_speckles(size):
    """Create tiny dust spots or foxing marks."""
    canvas_size = int(size * 2)
    speckles = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(speckles)
    
    # Random tiny spots
    num_spots = random.randint(10, 25)
    
    for _ in range(num_spots):
        x = random.randint(0, canvas_size)
        y = random.randint(0, canvas_size)
        spot_size = random.randint(1, 4)
        opacity = random.randint(40, 90)
        
        draw_irregular_shape(draw, [x - spot_size, y - spot_size, x + spot_size, y + spot_size], fill=opacity)
    
    speckles = speckles.filter(ImageFilter.GaussianBlur(radius=2))
    return speckles

def create_streak_mark(size):
    """Create a streak or smear mark."""
    canvas_size = int(size * 2)
    streak = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(streak)
    
    center = canvas_size // 2
    # Create streaky pattern
    num_streaks = random.randint(3, 8)
    
    for _ in range(num_streaks):
        start_x = random.randint(center - size // 2, center + size // 2)
        start_y = random.randint(center - size // 2, center + size // 2)
        
        length = random.randint(int(size * 0.3), int(size * 0.8))
        angle = random.uniform(0, 360)
        
        end_x = start_x + int(length * np.cos(np.radians(angle)))
        end_y = start_y + int(length * np.sin(np.radians(angle)))
        
        width = random.randint(2, 6)
        opacity = random.randint(70, 140)
        
        draw.line([start_x, start_y, end_x, end_y], fill=opacity, width=width)
    
    streak = streak.filter(ImageFilter.GaussianBlur(radius=size * 0.12))
    return streak

def create_corner_aging(width, height, corner_position):
    """Create corner darkening/aging effect."""
    aging = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(aging)
    
    corner_size = random.randint(min(width, height) // 6, min(width, height) // 4)
    
    # Determine corner position
    corners = {
        'top-left': (0, 0),
        'top-right': (width - corner_size, 0),
        'bottom-left': (0, height - corner_size),
        'bottom-right': (width - corner_size, height - corner_size)
    }
    
    x_start, y_start = corners[corner_position]
    
    # Create gradient effect
    for i in range(corner_size):
        opacity = int(100 * (1 - i / corner_size) ** 2)
        if opacity > 5:
            # Draw from corner
            if 'left' in corner_position:
                x0 = x_start
                x1 = x_start + corner_size - i
            else:
                x0 = x_start + i
                x1 = x_start + corner_size
            
            if 'top' in corner_position:
                y0 = y_start
                y1 = y_start + corner_size - i
            else:
                y0 = y_start + i
                y1 = y_start + corner_size
            
            draw.rectangle([x0, y0, x1, y1], fill=opacity)
    
    aging = aging.filter(ImageFilter.GaussianBlur(radius=corner_size * 0.2))
    return aging

def create_paper_grain(width, height, intensity=0.5):
    """Create paper texture/grain effect."""
    grain = np.random.randint(-30, 30, (height, width), dtype=np.int16)
    grain = (grain * intensity).astype(np.int16)
    return grain

def apply_grain_to_overlay(overlay, intensity=0.4):
    """Apply grain to mark colors while preserving transparency."""
    overlay_rgba = overlay.convert('RGBA')
    rgb = overlay_rgba.convert('RGB')

    img_array = np.array(rgb).astype(np.int16)
    grain = create_paper_grain(rgb.width, rgb.height, intensity=intensity)
    img_array[:, :, 0] = np.clip(img_array[:, :, 0] + grain, 0, 255)
    img_array[:, :, 1] = np.clip(img_array[:, :, 1] + grain, 0, 255)
    img_array[:, :, 2] = np.clip(img_array[:, :, 2] + grain, 0, 255)

    rgb_grain = Image.fromarray(img_array.astype(np.uint8))
    r, g, b = rgb_grain.split()
    _, _, _, a = overlay_rgba.split()
    return Image.merge('RGBA', (r, g, b, a))

def create_vignette(width, height, strength=0.5):
    """Create vignette/edge darkening effect. Fast numpy version."""
    center_x, center_y = width / 2.0, height / 2.0
    max_dist = math.sqrt(center_x**2 + center_y**2)
    
    y_idx, x_idx = np.ogrid[:height, :width]
    dist = np.sqrt((x_idx - center_x)**2 + (y_idx - center_y)**2)
    vignette_array = np.clip((dist / max_dist) * 180 * strength, 0, 200).astype(np.uint8)
    
    vignette = Image.fromarray(vignette_array)
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=max(width, height) * 0.1))
    return vignette

def create_fold_line(width, height, vertical=True):
    """Create a fold/crease line."""
    fold = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(fold)
    
    if vertical:
        # Vertical fold
        center = random.randint(int(width * 0.3), int(width * 0.7))
        for y in range(height):
            offset = random.randint(-3, 3)
            x = center + offset
            thickness = random.randint(2, 5)
            opacity = random.randint(60, 120)
            draw.line([(x - thickness, y), (x + thickness, y)], fill=opacity, width=thickness)
    else:
        # Horizontal fold
        center = random.randint(int(height * 0.3), int(height * 0.7))
        for x in range(width):
            offset = random.randint(-3, 3)
            y = center + offset
            thickness = random.randint(2, 5)
            opacity = random.randint(60, 120)
            draw.line([(x, y - thickness), (x, y + thickness)], fill=opacity, width=thickness)
    
    fold = fold.filter(ImageFilter.GaussianBlur(radius=2))
    return fold

def create_crack_pattern(width, height):
    """Create small cracks or tears in the paper."""
    crack = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(crack)
    
    # Random starting point
    x = random.randint(int(width * 0.2), int(width * 0.8))
    y = random.randint(int(height * 0.2), int(height * 0.8))
    
    # Create branching crack
    length = random.randint(30, 100)
    angle = random.uniform(0, 360)
    
    for i in range(length):
        angle += random.uniform(-15, 15)
        step_x = int(np.cos(np.radians(angle)) * 2)
        step_y = int(np.sin(np.radians(angle)) * 2)
        
        x += step_x
        y += step_y
        
        if 0 <= x < width and 0 <= y < height:
            thickness = random.randint(1, 3)
            opacity = random.randint(80, 150)
            draw.ellipse([x - thickness, y - thickness, x + thickness, y + thickness], fill=opacity)
            
            # Random branching
            if random.random() < 0.1:
                branch_length = random.randint(10, 30)
                branch_angle = angle + random.uniform(-60, 60)
                bx, by = x, y
                for j in range(branch_length):
                    bx += int(np.cos(np.radians(branch_angle)) * 2)
                    by += int(np.sin(np.radians(branch_angle)) * 2)
                    if 0 <= bx < width and 0 <= by < height:
                        draw.point((bx, by), fill=opacity // 2)
    
    crack = crack.filter(ImageFilter.GaussianBlur(radius=0.5))
    return crack

def create_algae_growth(width, height):
    """Create algae/mold growth patches — greenish-brown organic spread
    common on ancient manuscripts stored in humid environments."""
    algae = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(algae)

    # 1-4 algae colonies, each spreading organically from a seed point
    num_colonies = random.randint(1, 4)
    for _ in range(num_colonies):
        # Seed near edges/corners (algae grows from where moisture enters)
        edge = random.choice(['top', 'bottom', 'left', 'right', 'corner'])
        if edge == 'top':
            cx = random.randint(int(width * 0.1), int(width * 0.9))
            cy = random.randint(0, int(height * 0.2))
        elif edge == 'bottom':
            cx = random.randint(int(width * 0.1), int(width * 0.9))
            cy = random.randint(int(height * 0.8), height)
        elif edge == 'left':
            cx = random.randint(0, int(width * 0.2))
            cy = random.randint(int(height * 0.1), int(height * 0.9))
        elif edge == 'right':
            cx = random.randint(int(width * 0.8), width)
            cy = random.randint(int(height * 0.1), int(height * 0.9))
        else:
            corner = random.choice([(0.1, 0.1), (0.9, 0.1), (0.1, 0.9), (0.9, 0.9)])
            cx = int(width * corner[0]) + random.randint(-30, 30)
            cy = int(height * corner[1]) + random.randint(-30, 30)

        # Colony size based on image dimensions
        colony_radius = random.randint(min(width, height) // 8, min(width, height) // 3)

        # Build colony by random-walking many small blobs outward
        num_blobs = random.randint(30, 70)
        for _ in range(num_blobs):
            # Random walk from centre with bias toward edges
            angle = random.uniform(0, 2 * math.pi)
            dist = random.gauss(0, colony_radius * 0.4)
            bx = int(cx + dist * math.cos(angle))
            by = int(cy + dist * math.sin(angle))
            r = random.randint(int(colony_radius * 0.08), int(colony_radius * 0.35))
            opacity = random.randint(25, 90)
            x0, y0 = max(0, bx - r), max(0, by - r)
            x1, y1 = min(width, bx + r), min(height, by + r)
            if x1 > x0 and y1 > y0:
                draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)

        # Fine tendrils radiating outward
        num_tendrils = random.randint(4, 10)
        for _ in range(num_tendrils):
            angle = random.uniform(0, 2 * math.pi)
            length = random.randint(colony_radius // 3, colony_radius)
            tx, ty = cx, cy
            for step in range(length):
                angle += random.uniform(-0.3, 0.3)
                tx += int(math.cos(angle) * 2)
                ty += int(math.sin(angle) * 2)
                if 0 <= tx < width and 0 <= ty < height:
                    w = random.randint(1, 4)
                    op = random.randint(10, 40)
                    draw.line([(tx - w, ty), (tx + w, ty)], fill=op, width=w)

    algae = algae.filter(ImageFilter.GaussianBlur(radius=max(4, min(width, height) * 0.02)))
    return algae

def create_dark_damage_patch(width, height):
    """Create large, very dark irregular damage patches concentrated at edges/corners.
    Simulates severe water, smoke, or age damage where the parchment has turned
    very dark brown to near-black — matching authentic ancient manuscripts."""
    patch = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(patch)

    min_dim = min(width, height)

    # Choose 1-3 regions for damage (biased to corners/edges)
    num_patches = random.randint(1, 3)
    for _ in range(num_patches):
        corner = random.choice([
            (0, 0), (width, 0), (0, height), (width, height),
            (width // 2, 0), (width // 2, height),
            (0, height // 2), (width, height // 2)
        ])
        seed_x, seed_y = corner

        # Large spread — covers significant portion of the page
        spread = random.randint(int(min_dim * 0.25), int(min_dim * 0.65))

        # Dense core with many overlapping blobs for solid coverage
        num_blobs = random.randint(60, 150)
        for i in range(num_blobs):
            angle = random.uniform(0, 2 * math.pi)
            dist = abs(random.gauss(0, spread * 0.35))
            bx = int(seed_x + dist * math.cos(angle))
            by = int(seed_y + dist * math.sin(angle))

            max_r = int(spread * 0.30 * max(0.15, 1.0 - dist / spread))
            r = random.randint(max(5, max_r // 3), max(8, max_r))

            fade = max(0.3, 1.0 - (dist / spread) ** 0.6)
            opacity = int(random.randint(140, 240) * fade)

            x0, y0 = max(0, bx - r), max(0, by - r)
            x1, y1 = min(width, bx + r), min(height, by + r)
            if x1 > x0 + 2 and y1 > y0 + 2:
                draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)

        # Ghost outer fringe
        for _ in range(num_blobs // 3):
            angle = random.uniform(0, 2 * math.pi)
            dist = abs(random.gauss(spread * 0.5, spread * 0.25))
            bx = int(seed_x + dist * math.cos(angle))
            by = int(seed_y + dist * math.sin(angle))
            r = random.randint(max(3, spread // 12), max(6, spread // 5))
            fade = max(0.05, 1.0 - (dist / (spread * 1.2)) ** 0.5)
            opacity = int(random.randint(20, 60) * fade)
            x0, y0 = max(0, bx - r), max(0, by - r)
            x1, y1 = min(width, bx + r), min(height, by + r)
            if x1 > x0 + 2 and y1 > y0 + 2:
                draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)

        # Sharp tide line at the damage border
        tide_dist = spread * random.uniform(0.45, 0.75)
        num_tide = random.randint(50, 120)
        for _ in range(num_tide):
            ta = random.uniform(0, 2 * math.pi)
            td = tide_dist + random.gauss(0, spread * 0.07)
            tx = int(seed_x + td * math.cos(ta))
            ty = int(seed_y + td * math.sin(ta))
            tr = random.randint(max(3, spread // 15), max(6, spread // 6))
            tide_op = random.randint(160, 245)
            tx0, ty0 = max(0, tx - tr), max(0, ty - tr)
            tx1, ty1 = min(width, tx + tr), min(height, ty + tr)
            if tx1 > tx0 + 2 and ty1 > ty0 + 2:
                draw_irregular_shape(draw, [tx0, ty0, tx1, ty1], fill=tide_op)

    patch = patch.filter(ImageFilter.GaussianBlur(radius=max(3, min_dim * 0.012)))
    return patch

def create_ink_splatter(width, height):
    """Create scattered ink splatter dots across the page — many tiny 1-2px
    dots plus occasional dense clusters and larger blots."""
    splatter = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(splatter)

    # --- Tiny scattered dots (1-2px) — the majority of spatter ---
    num_tiny = random.randint(150, 500)
    for _ in range(num_tiny):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        r = random.randint(1, 2)
        opacity = random.randint(100, 230)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=opacity)

    # --- Medium scattered dots (3-8px) ---
    num_medium = random.randint(30, 100)
    for _ in range(num_medium):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        r = random.randint(3, 8)
        opacity = random.randint(130, 245)
        draw_irregular_shape(draw, [x - r, y - r, x + r, y + r], fill=opacity)

    # --- Occasional large blots (10-25px) ---
    num_large = random.randint(3, 15)
    for _ in range(num_large):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        r = random.randint(10, 25)
        opacity = random.randint(160, 250)
        draw_irregular_shape(draw, [x - r, y - r, x + r, y + r], fill=opacity)

    # --- Dense clusters (ink drips / bottle spills) ---
    num_clusters = random.randint(1, 3)
    for _ in range(num_clusters):
        cluster_x = random.randint(int(width * 0.05), int(width * 0.95))
        cluster_y = random.randint(int(height * 0.05), int(height * 0.95))
        cluster_spread = random.uniform(15, 50)
        cluster_dots = random.randint(30, 80)
        for _ in range(cluster_dots):
            dx = random.gauss(0, cluster_spread)
            dy = random.gauss(0, cluster_spread)
            cx, cy = int(cluster_x + dx), int(cluster_y + dy)
            if random.random() < 0.65:
                r = random.randint(1, 3)  # mostly tiny
            elif random.random() < 0.6:
                r = random.randint(3, 8)
            else:
                r = random.randint(8, 18)  # concentrated blot
            if 0 <= cx < width and 0 <= cy < height:
                if r <= 2:
                    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                                 fill=random.randint(140, 250))
                else:
                    draw_irregular_shape(draw, [cx - r, cy - r, cx + r, cy + r],
                                         fill=random.randint(160, 250))

    splatter = splatter.filter(ImageFilter.GaussianBlur(radius=0.5))
    return splatter

def create_edge_water_stain(width, height):
    """Create large organic water/moisture stain spreading inward from
    one or more edges — like real manuscripts with water damage from the sides.
    Produces soft, feathered, irregularly-shaped brownish patches."""
    stain = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(stain)

    # Choose 1-3 edges to spawn stains from
    num_stains = random.randint(1, 3)
    for _ in range(num_stains):
        edge = random.choice(['top', 'bottom', 'left', 'right',
                               'top-right', 'top-left', 'bottom-right', 'bottom-left'])

        # Determine seed region along chosen edge
        if edge == 'top':
            seed_x = random.randint(int(width * 0.1), int(width * 0.9))
            seed_y = 0
        elif edge == 'bottom':
            seed_x = random.randint(int(width * 0.1), int(width * 0.9))
            seed_y = height
        elif edge == 'left':
            seed_x = 0
            seed_y = random.randint(int(height * 0.1), int(height * 0.9))
        elif edge == 'right':
            seed_x = width
            seed_y = random.randint(int(height * 0.1), int(height * 0.9))
        elif edge == 'top-right':
            seed_x = width
            seed_y = 0
        elif edge == 'top-left':
            seed_x = 0
            seed_y = 0
        elif edge == 'bottom-right':
            seed_x = width
            seed_y = height
        else:
            seed_x = 0
            seed_y = height

        # Spread distance — how far the stain seeps inward
        spread = random.randint(min(width, height) // 3, int(min(width, height) * 0.75))

        # Build the stain from many overlapping irregular blobs
        num_blobs = random.randint(45, 100)
        for i in range(num_blobs):
            # Radial spread from seed, with distance-based opacity falloff
            angle = random.uniform(0, 2 * math.pi)
            dist = abs(random.gauss(0, spread * 0.45))
            bx = int(seed_x + dist * math.cos(angle))
            by = int(seed_y + dist * math.sin(angle))

            # Larger blobs near edge, smaller further in
            max_r = int(spread * 0.35 * max(0.2, 1.0 - dist / spread))
            r = random.randint(max(5, max_r // 3), max(8, max_r))

            # Opacity fades with distance from edge
            fade = max(0.20, 1.0 - (dist / spread) ** 0.7)
            opacity = int(random.randint(50, 140) * fade)

            x0 = max(0, bx - r)
            y0 = max(0, by - r)
            x1 = min(width, bx + r)
            y1 = min(height, by + r)
            if x1 > x0 + 2 and y1 > y0 + 2:
                draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)

        # Add a softer secondary spread for feathered edges (ghost regions)
        for _ in range(num_blobs // 2):
            angle = random.uniform(0, 2 * math.pi)
            dist = abs(random.gauss(0, spread * 0.6))
            bx = int(seed_x + dist * math.cos(angle))
            by = int(seed_y + dist * math.sin(angle))
            r = random.randint(spread // 10, spread // 4)
            fade = max(0.05, 1.0 - (dist / (spread * 1.3)) ** 0.6)
            opacity = int(random.randint(12, 45) * fade)
            x0 = max(0, bx - r)
            y0 = max(0, by - r)
            x1 = min(width, bx + r)
            y1 = min(height, by + r)
            if x1 > x0 + 2 and y1 > y0 + 2:
                draw_irregular_shape(draw, [x0, y0, x1, y1], fill=opacity)

        # --- Wick / tide-line effect: darker concentrated border at stain perimeter ---
        tide_dist = spread * random.uniform(0.5, 0.85)
        num_tide_pts = random.randint(40, 80)
        for _ in range(num_tide_pts):
            ta = random.uniform(0, 2 * math.pi)
            td = tide_dist + random.gauss(0, spread * 0.08)
            tx = int(seed_x + td * math.cos(ta))
            ty = int(seed_y + td * math.sin(ta))
            tr = random.randint(max(2, spread // 20), max(4, spread // 8))
            tide_opacity = random.randint(100, 200)
            tx0, ty0 = max(0, tx - tr), max(0, ty - tr)
            tx1, ty1 = min(width, tx + tr), min(height, ty + tr)
            if tx1 > tx0 + 2 and ty1 > ty0 + 2:
                draw_irregular_shape(draw, [tx0, ty0, tx1, ty1], fill=tide_opacity)

        # --- Ink spatter droplets around stain edges ---
        num_droplets = random.randint(10, 30)
        for _ in range(num_droplets):
            da = random.uniform(0, 2 * math.pi)
            dd = spread * random.uniform(0.6, 1.3)
            dx = int(seed_x + dd * math.cos(da))
            dy = int(seed_y + dd * math.sin(da))
            dr = random.randint(1, max(2, spread // 25))
            d_opacity = random.randint(80, 180)
            if 0 < dx < width and 0 < dy < height:
                draw_irregular_shape(draw, [dx - dr, dy - dr, dx + dr, dy + dr], fill=d_opacity)

    stain = stain.filter(ImageFilter.GaussianBlur(radius=max(5, min(width, height) * 0.025)))
    return stain

def apply_paper_yellowing(image, intensity=0.3):
    """Apply overall yellowing/sepia tint to simulate aging paper."""
    img_array = np.array(image).astype(np.float32)
    
    # Create sepia/yellow tint
    sepia_r = 1.0 + (0.3 * intensity)
    sepia_g = 1.0 + (0.15 * intensity)
    sepia_b = 1.0 - (0.2 * intensity)
    
    img_array[:, :, 0] = np.clip(img_array[:, :, 0] * sepia_r, 0, 255)
    img_array[:, :, 1] = np.clip(img_array[:, :, 1] * sepia_g, 0, 255)
    img_array[:, :, 2] = np.clip(img_array[:, :, 2] * sepia_b, 0, 255)
    
    return Image.fromarray(img_array.astype(np.uint8))

def apply_smudges(image, num_smudges=3, intensity=0.5, aging_level='medium'):
    """
    Apply varied organic aging effects to the image with multiple types and colors.
    
    Args:
        image: PIL Image to process
        num_smudges: Number of effects to apply
        intensity: Overall opacity of effects (0-1)
    
    Returns:
        Tuple of (PIL Image with aging effects applied, list of mark types used)
    """
    # Convert to RGBA if not already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Create a copy to work on
    result = image.copy()
    width, height = result.size
    
    # Create overlay layer
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Load user preferences for mark type weights
    user_preferences = load_preferences()
    
    # Define different mark types with their base probabilities
    base_mark_types = [
        ('blob', 0.06),
        ('water_stain', 0.14),
        ('fingerprint', 0.04),
        ('dust', 0.05),
        ('streak', 0.04),
        ('bleeding_ink', 0.04),
        ('faded_ink', 0.03),
        ('smudged_calligraphy', 0.03),
        ('moisture_damage', 0.08),
        ('soot_stain', 0.03),
        ('atmospheric_grime', 0.07),
        ('coffee_mark', 0.06),
        ('muddy_mark', 0.03),
        ('heavy_ink_blotch', 0.08),
        ('age_rings', 0.05),
        ('ink_halo', 0.04),
        ('foxing_spots', 0.08),
        ('uneven_fading', 0.05),
        ('text_area_smudge', 0.07),
        ('rust_stains', 0.03),
        ('algae_growth', 0.10),
        ('ink_splatter', 0.10),
        ('edge_water_stain', 0.12),
        ('dark_damage', 0.10)
    ]
    
    # Apply user preference multipliers
    mark_types = [(mark, weight * user_preferences.get(mark, 1.0)) for mark, weight in base_mark_types]
    
    # Track which mark types are used
    marks_used = []
    
    # Extended color palette for natural aging — manuscript-accurate tones
    aging_colors = [
        # Amber / Ochre / Light Tan (water stain tea-staining)
        (195, 155, 80), (185, 145, 75), (175, 140, 70), (200, 160, 90),
        (190, 150, 85), (180, 142, 78), (170, 135, 68),
        # Brown/Sepia tones (ink stains)
        (101, 67, 33), (92, 64, 51), (80, 60, 40), (70, 50, 30),
        # Grayish tones (mold, dirt, dust)
        (120, 115, 100), (100, 95, 85), (90, 85, 75),
        # Burnt Sienna / Rust (oxidation weathering)
        (160, 82, 45), (145, 75, 40), (170, 90, 50), (155, 80, 42),
        (130, 80, 50), (110, 70, 40), (140, 90, 60),
        # Greenish gray (moisture, mildew)
        (100, 110, 90), (85, 95, 80),
        # Dark grays (soot, dirt)
        (60, 55, 50), (75, 70, 65),
        # Paper-matching dark tan/brown (large water damage look)
        (140, 115, 75), (130, 105, 65), (120, 95, 60),
        (110, 90, 55), (150, 120, 80), (105, 85, 55),
        (95, 75, 50), (85, 70, 45)
    ]

    # Water stain colors — Amber / Ochre / Tan + darker damage browns
    water_stain_colors = [
        (195, 155, 80), (185, 145, 75), (200, 160, 90),
        (175, 140, 70), (190, 150, 85), (180, 142, 78),
        (170, 135, 68), (165, 130, 65), (160, 125, 60),
        (155, 120, 58), (150, 118, 55), (145, 112, 52),
        # Darker damage browns (for severe water staining)
        (120, 90, 48), (105, 75, 40), (90, 65, 35),
        (80, 58, 30), (110, 82, 42), (95, 68, 36)
    ]
    
    # Very dark damage colors — near-black browns for severe patches
    dark_damage_colors = [
        (55, 40, 28), (45, 35, 25), (65, 48, 32),
        (40, 30, 20), (50, 38, 25), (60, 42, 28),
        (70, 50, 30), (35, 28, 18), (75, 55, 35)
    ]

    # Ink smudge colors — Deep Charcoal, Sepia, Black (carbon-based ink)
    ink_colors = [
        (25, 22, 20), (35, 30, 28), (45, 40, 38), (55, 48, 42),
        (30, 28, 25), (40, 35, 30), (20, 18, 15), (50, 45, 40),
        (65, 55, 45), (75, 65, 50)  # sepia tones
    ]

    # Weathering/oxidation colors — Burnt Sienna, Rust
    weathering_colors = [
        (160, 82, 45), (145, 75, 40), (170, 90, 50), (155, 80, 42),
        (180, 95, 55), (150, 78, 38), (140, 72, 35), (165, 85, 48),
        (135, 68, 32), (175, 88, 52)
    ]

    coffee_colors = [
        (120, 80, 50), (110, 70, 40), (130, 85, 55), (145, 95, 60),
        (135, 82, 48), (125, 78, 45)
    ]

    grime_colors = [
        (90, 85, 75), (85, 80, 70), (100, 95, 85), (75, 70, 65),
        (95, 88, 78), (80, 75, 65)
    ]

    algae_colors = [
        # Dark olive / mold greens
        (75, 85, 50), (65, 80, 45), (80, 90, 55), (55, 70, 40),
        # Brownish-green (dried algae)
        (90, 85, 55), (80, 75, 50), (100, 90, 60),
        # Very dark green-grey (heavy mold)
        (50, 60, 40), (60, 65, 45)
    ]
    
    stain_types = {
        'water_stain',
        'moisture_damage',
        'atmospheric_grime',
        'coffee_mark',
        'age_rings',
        'foxing_spots',
        'text_area_smudge',
        'algae_growth',
        'edge_water_stain',
        'dark_damage'
    }

    # Apply random marks
    for i in range(num_smudges):
        # Choose random mark type based on weights
        mark_type = random.choices(
            [t[0] for t in mark_types],
            weights=[t[1] for t in mark_types]
        )[0]
        
        # Track this mark type
        if mark_type not in marks_used:
            marks_used.append(mark_type)
        
        # Variable size for each mark
        base_size = min(width, height)
        
        if mark_type == 'blob':
            smudge_size = random.randint(int(base_size * 0.15), int(base_size * 0.45))
            smudge_mask = create_organic_blob(smudge_size, irregularity=random.uniform(0.3, 0.6))
            color = random.choice(aging_colors)
            intensity_mod = random.uniform(1.1, 1.6)
            
        elif mark_type == 'water_stain':
            smudge_size = random.randint(int(base_size * 0.30), int(base_size * 0.70))
            smudge_mask = create_water_stain(smudge_size)
            # Amber / Ochre / Light Tan — tea-staining from aged moisture
            color = random.choice(water_stain_colors)
            intensity_mod = random.uniform(1.0, 1.6)
            
        elif mark_type == 'fingerprint':
            smudge_size = random.randint(int(base_size * 0.08), int(base_size * 0.20))
            smudge_mask = create_fingerprint_mark(smudge_size)
            color = random.choice([(80, 60, 40), (70, 50, 30), (90, 70, 50)])
            intensity_mod = random.uniform(0.8, 1.3)
            
        elif mark_type == 'dust':
            smudge_size = random.randint(int(base_size * 0.12), int(base_size * 0.30))
            smudge_mask = create_dust_speckles(smudge_size)
            color = random.choice(aging_colors)
            intensity_mod = random.uniform(0.9, 1.3)
            
        elif mark_type == 'streak':
            smudge_size = random.randint(int(base_size * 0.12), int(base_size * 0.35))
            smudge_mask = create_streak_mark(smudge_size)
            color = random.choice([(92, 64, 51), (80, 60, 40), (100, 95, 85), (110, 70, 40)])
            intensity_mod = random.uniform(0.8, 1.3)

        elif mark_type == 'bleeding_ink':
            smudge_size = random.randint(int(base_size * 0.08), int(base_size * 0.22))
            smudge_mask = create_bleeding_ink(smudge_size)
            # Deep Charcoal / Sepia / Black — carbon-based ink
            color = random.choice(ink_colors)
            intensity_mod = random.uniform(0.8, 1.3)

        elif mark_type == 'faded_ink':
            smudge_size = random.randint(int(base_size * 0.10), int(base_size * 0.28))
            smudge_mask = create_organic_blob(smudge_size, irregularity=random.uniform(0.2, 0.5))
            # Faded sepia/charcoal
            color = random.choice([(65, 55, 45), (75, 65, 50), (85, 75, 60), (95, 85, 70)])
            intensity_mod = random.uniform(0.8, 1.3)

        elif mark_type == 'smudged_calligraphy':
            smudge_size = random.randint(int(base_size * 0.10), int(base_size * 0.28))
            smudge_mask = create_streak_mark(smudge_size)
            # Deep Charcoal / Sepia — carbon ink smudge
            color = random.choice(ink_colors)
            intensity_mod = random.uniform(0.9, 1.4)

        elif mark_type == 'moisture_damage':
            smudge_size = random.randint(int(base_size * 0.30), int(base_size * 0.65))
            smudge_mask = create_water_stain(smudge_size)
            # Amber / Ochre moisture tones
            color = random.choice(water_stain_colors)
            intensity_mod = random.uniform(1.0, 1.5)

        elif mark_type == 'soot_stain':
            smudge_size = random.randint(int(base_size * 0.15), int(base_size * 0.35))
            smudge_mask = create_soot_stain(smudge_size)
            color = random.choice([(40, 40, 40), (55, 50, 50), (60, 60, 60)])
            intensity_mod = random.uniform(0.8, 1.3)

        elif mark_type == 'atmospheric_grime':
            smudge_size = random.randint(int(base_size * 0.18), int(base_size * 0.45))
            smudge_mask = create_atmospheric_grime(smudge_size)
            color = random.choice(grime_colors)
            intensity_mod = random.uniform(0.8, 1.3)

        elif mark_type == 'coffee_mark':
            smudge_size = random.randint(int(base_size * 0.18), int(base_size * 0.45))
            smudge_mask = create_coffee_ring(smudge_size)
            color = random.choice(coffee_colors)
            intensity_mod = random.uniform(0.9, 1.4)

        elif mark_type == 'muddy_mark':
            smudge_size = random.randint(int(base_size * 0.15), int(base_size * 0.40))
            smudge_mask = create_organic_blob(smudge_size, irregularity=random.uniform(0.4, 0.7))
            color = random.choice([(90, 70, 50), (100, 80, 55), (80, 60, 40), (120, 95, 60)])
            intensity_mod = random.uniform(0.9, 1.5)

        elif mark_type == 'heavy_ink_blotch':
            smudge_size = random.randint(int(base_size * 0.22), int(base_size * 0.55))
            smudge_mask = create_heavy_ink_blotch(smudge_size)
            # Deep black / charcoal — concentrated carbon ink
            color = random.choice([(15, 12, 10), (20, 18, 15), (25, 22, 20), (30, 28, 25), (10, 8, 6)])
            intensity_mod = random.uniform(1.1, 1.6)

        elif mark_type == 'age_rings':
            smudge_size = random.randint(int(base_size * 0.20), int(base_size * 0.45))
            smudge_mask = create_age_rings(smudge_size)
            color = random.choice([(150, 130, 100), (140, 120, 85), (160, 140, 110), (145, 125, 95)])
            intensity_mod = random.uniform(0.9, 1.4)

        elif mark_type == 'ink_halo':
            smudge_size = random.randint(int(base_size * 0.12), int(base_size * 0.30))
            smudge_mask = create_ink_halo(smudge_size)
            color = random.choice([(80, 70, 55), (70, 60, 45), (90, 80, 65)])
            intensity_mod = random.uniform(0.8, 1.2)

        elif mark_type == 'foxing_spots':
            smudge_size = random.randint(int(base_size * 0.18), int(base_size * 0.40))
            smudge_mask = create_foxing_spots(smudge_size)
            # Burnt Sienna / Rust — oxidation spots
            color = random.choice(weathering_colors)
            intensity_mod = random.uniform(0.9, 1.4)

        elif mark_type == 'uneven_fading':
            smudge_size = random.randint(int(base_size * 0.18), int(base_size * 0.45))
            smudge_mask = create_uneven_fading(smudge_size)
            color = random.choice([(110, 105, 95), (120, 115, 105), (100, 95, 85)])
            intensity_mod = random.uniform(0.8, 1.2)

        elif mark_type == 'text_area_smudge':
            smudge_size = random.randint(int(base_size * 0.15), int(base_size * 0.35))
            smudge_mask = create_text_area_smudge(smudge_size)
            color = random.choice([(70, 65, 55), (85, 80, 70), (65, 60, 50)])
            intensity_mod = random.uniform(0.8, 1.3)

        elif mark_type == 'rust_stains':
            # Rust stains are full-width — Burnt Sienna / Rust oxidation
            smudge_mask = create_rust_stains(width, height)
            color = random.choice(weathering_colors)
            intensity_mod = random.uniform(0.6, 1.1)
            # Skip position calculation for rust stains - they span the whole image
            rust_rgba = Image.new('RGBA', smudge_mask.size, color + (0,))
            mask_array = np.array(smudge_mask)
            adjusted_intensity = intensity * intensity_mod
            mask_array = (mask_array * adjusted_intensity).astype(np.uint8)
            rust_array = np.array(rust_rgba)
            rust_array[:, :, 3] = mask_array
            rust_rgba = Image.fromarray(rust_array)
            overlay = Image.alpha_composite(overlay, rust_rgba)
            continue

        elif mark_type == 'algae_growth':
            # Full-image algae/mold effect
            smudge_mask = create_algae_growth(width, height)
            color = random.choice(algae_colors)
            intensity_mod = random.uniform(0.7, 1.2)
            algae_rgba = Image.new('RGBA', smudge_mask.size, color + (0,))
            mask_array = np.array(smudge_mask).astype(np.float32)
            mask_array = np.clip(mask_array * intensity * intensity_mod, 0, 240).astype(np.uint8)
            algae_array = np.array(algae_rgba)
            algae_array[:, :, 3] = mask_array
            algae_rgba = Image.fromarray(algae_array)
            overlay = Image.alpha_composite(overlay, algae_rgba)
            continue

        elif mark_type == 'ink_splatter':
            # Full-image scattered ink dots — Deep Charcoal / Sepia / Black
            smudge_mask = create_ink_splatter(width, height)
            color = random.choice(ink_colors[:6])  # darker ink tones
            intensity_mod = random.uniform(0.7, 1.2)
            splat_rgba = Image.new('RGBA', smudge_mask.size, color + (0,))
            mask_array = np.array(smudge_mask).astype(np.float32)
            mask_array = np.clip(mask_array * intensity * intensity_mod, 0, 245).astype(np.uint8)
            splat_array = np.array(splat_rgba)
            splat_array[:, :, 3] = mask_array
            splat_rgba = Image.fromarray(splat_array)
            overlay = Image.alpha_composite(overlay, splat_rgba)
            continue

        elif mark_type == 'edge_water_stain':
            # Full-image edge-spreading water stain — Amber to dark brown
            smudge_mask = create_edge_water_stain(width, height)
            color = random.choice(water_stain_colors)
            intensity_mod = random.uniform(1.0, 1.6)
            ews_rgba = Image.new('RGBA', smudge_mask.size, color + (0,))
            mask_array = np.array(smudge_mask).astype(np.float32)
            mask_array = np.clip(mask_array * intensity * intensity_mod, 0, 245).astype(np.uint8)
            ews_array = np.array(ews_rgba)
            ews_array[:, :, 3] = mask_array
            ews_rgba = Image.fromarray(ews_array)
            overlay = Image.alpha_composite(overlay, ews_rgba)
            continue

        elif mark_type == 'dark_damage':
            # Full-image severe damage patches — very dark, concentrated at edges
            smudge_mask = create_dark_damage_patch(width, height)
            color = random.choice(dark_damage_colors)
            intensity_mod = random.uniform(0.9, 1.4)
            dd_rgba = Image.new('RGBA', smudge_mask.size, color + (0,))
            mask_array = np.array(smudge_mask).astype(np.float32)
            mask_array = np.clip(mask_array * intensity * intensity_mod, 0, 245).astype(np.uint8)
            dd_array = np.array(dd_rgba)
            dd_array[:, :, 3] = mask_array
            dd_rgba = Image.fromarray(dd_array)
            overlay = Image.alpha_composite(overlay, dd_rgba)
            continue
        # Calculate maximum valid positions
        max_x = max(0, width - smudge_mask.width)
        max_y = max(0, height - smudge_mask.height)
        
        # Calculate margin with safety checks
        edge_bias = random.uniform(0.7, 1.8) if mark_type in stain_types else random.uniform(0.4, 1.2)
        margin = int(smudge_size * edge_bias)
        margin = max(0, min(margin, min(width, height) // 4))
        
        # Sometimes place marks near edges or corners for natural look
        edge_prob = 0.6 if mark_type in stain_types else 0.25
        if random.random() < edge_prob and max_x > 0 and max_y > 0:  # bias stains to edges/corners
            if mark_type in stain_types:
                smudge_size = int(smudge_size * random.uniform(1.05, 1.25))
            if random.random() < 0.5:
                # Place on left or right edge
                if random.random() < 0.5 and margin > 0:
                    # Left edge
                    pos_x = random.randint(0, min(margin, max_x))
                else:
                    # Right edge
                    left_edge = max(0, width - margin - smudge_mask.width)
                    if left_edge <= max_x:
                        pos_x = random.randint(left_edge, max_x)
                    else:
                        pos_x = random.randint(0, max_x)
                pos_y = random.randint(0, max_y)
            else:
                # Place on top or bottom edge
                pos_x = random.randint(0, max_x)
                if random.random() < 0.5 and margin > 0:
                    # Top edge
                    pos_y = random.randint(0, min(margin, max_y))
                else:
                    # Bottom edge
                    top_edge = max(0, height - margin - smudge_mask.height)
                    if top_edge <= max_y:
                        pos_y = random.randint(top_edge, max_y)
                    else:
                        pos_y = random.randint(0, max_y)
        else:
            # Normal placement - avoid edges if possible
            min_x = min(margin, max_x)
            min_y = min(margin, max_y)
            
            # Calculate safe range
            safe_max_x = max(min_x, max_x - margin)
            safe_max_y = max(min_y, max_y - margin)
            
            # Ensure valid range
            if min_x <= safe_max_x:
                pos_x = random.randint(min_x, safe_max_x)
            else:
                pos_x = random.randint(0, max_x) if max_x > 0 else 0
            
            if min_y <= safe_max_y:
                pos_y = random.randint(min_y, safe_max_y)
            else:
                pos_y = random.randint(0, max_y) if max_y > 0 else 0
        
        # Create colored mark with alpha
        smudge_rgba = Image.new('RGBA', smudge_mask.size, color + (0,))
        
        # Apply the mask as alpha channel with intensity adjustment
        mask_array = np.array(smudge_mask).astype(np.float32)
        adjusted_intensity = intensity * intensity_mod
        mask_array = mask_array * adjusted_intensity
        # Cap maximum alpha
        max_alpha = 245
        mask_array = np.clip(mask_array, 0, max_alpha).astype(np.uint8)
        
        # Set alpha channel
        smudge_array = np.array(smudge_rgba)
        smudge_array[:, :, 3] = mask_array
        smudge_rgba = Image.fromarray(smudge_array)
        
        # Paste onto overlay layer
        overlay.paste(smudge_rgba, (pos_x, pos_y), smudge_rgba)
    
    # Aging level-based effects
    # Light: basic smudges only
    # Medium: add corners, grain, slight yellowing
    # Heavy: add all effects including folds, cracks, vignette, strong yellowing
    # Extreme: maximum intensity of all effects
    
    # Randomly add corner aging (probability based on aging level)
    corner_prob = {
        'light': 0.2,
        'medium': 0.4,
        'heavy': 0.6,
        'extreme': 0.9
    }.get(aging_level, 0.4)
    
    for corner in ['top-left', 'top-right', 'bottom-left', 'bottom-right']:
        if random.random() < corner_prob:
            corner_aging = create_corner_aging(width, height, corner)
            corner_color = random.choice([(80, 70, 55), (90, 80, 65), (70, 60, 50), (60, 50, 40)])
            corner_rgba = Image.new('RGBA', (width, height), corner_color + (0,))
            
            corner_intensity_mult = 0.6 if aging_level != 'extreme' else 0.9
            corner_array = np.array(corner_rgba)
            corner_mask = np.array(corner_aging)
            corner_array[:, :, 3] = (corner_mask * intensity * corner_intensity_mult).astype(np.uint8)
            corner_rgba = Image.fromarray(corner_array)
            
            overlay = Image.alpha_composite(overlay, corner_rgba)
    
    # Note: vignette removed to preserve original page color
    
    # Add cracks (heavy and extreme)
    if aging_level in ['heavy', 'extreme']:
        num_cracks = random.randint(0, 2) if aging_level == 'heavy' else random.randint(2, 4)
        for _ in range(num_cracks):
            crack = create_crack_pattern(width, height)
            crack_color = random.choice([(60, 50, 40), (70, 60, 50), (50, 40, 30)])
            crack_rgba = Image.new('RGBA', (width, height), crack_color + (0,))
            
            crack_intensity_mult = 0.8 if aging_level == 'heavy' else 1.1
            crack_array = np.array(crack_rgba)
            crack_array[:, :, 3] = (np.array(crack) * intensity * crack_intensity_mult).astype(np.uint8)
            crack_rgba = Image.fromarray(crack_array)
            
            overlay = Image.alpha_composite(overlay, crack_rgba)
    
    # Add moisture tide marks (heavy and extreme)
    if aging_level in ['heavy', 'extreme']:
        if random.random() < (0.4 if aging_level == 'heavy' else 0.7):
            tide = create_moisture_tide_mark(width, height)
            tide_color = random.choice([(120, 110, 90), (115, 105, 85), (130, 120, 100)])
            tide_rgba = Image.new('RGBA', (width, height), tide_color + (0,))
            
            tide_intensity_mult = 0.5 if aging_level == 'heavy' else 0.7
            tide_array = np.array(tide_rgba)
            tide_array[:, :, 3] = (np.array(tide) * intensity * tide_intensity_mult).astype(np.uint8)
            tide_rgba = Image.fromarray(tide_array)
            
            overlay = Image.alpha_composite(overlay, tide_rgba)
    
    # Apply low contrast and grain to marks only so base paper color stays intact
    # Add torn edge effect to result (on corners/edges)
    if aging_level in ['heavy', 'extreme']:
        if random.random() < (0.5 if aging_level == 'heavy' else 0.8):
            torn_edges = create_torn_paper_edge(width, height)
            torn_color = random.choice([(70, 60, 50), (80, 65, 50), (60, 50, 40)])
            torn_rgba = Image.new('RGBA', (width, height), torn_color + (0,))

            torn_intensity_mult = 0.6 if aging_level == 'heavy' else 0.9
            torn_array = np.array(torn_rgba)
            torn_mask = (255 - np.array(torn_edges)).astype(np.uint8)
            torn_array[:, :, 3] = (torn_mask * intensity * torn_intensity_mult / 255).astype(np.uint8)
            torn_rgba = Image.fromarray(torn_array)

            overlay = Image.alpha_composite(overlay, torn_rgba)
    
    # Add edge darkening with very dark brown / burnt sienna oxidation
    if random.random() < (0.5 if aging_level == 'light' else 0.7 if aging_level == 'medium' else 0.90):
        edge_dark = create_edge_darkening(width, height)
        edge_color = random.choice([
            (55, 40, 28), (45, 35, 25), (65, 48, 32),   # very dark brown
            (75, 55, 35), (50, 38, 25), (60, 45, 30),   # dark umber
            (40, 30, 20), (70, 50, 30), (80, 58, 38),   # near-black brown
        ])
        edge_rgba = Image.new('RGBA', (width, height), edge_color + (0,))
        
        edge_intensity_mult = 0.4 if aging_level == 'light' else 0.6 if aging_level == 'medium' else 0.8 if aging_level == 'heavy' else 1.0
        edge_array = np.array(edge_rgba)
        edge_array[:, :, 3] = np.clip(
            np.array(edge_dark).astype(np.float32) * intensity * edge_intensity_mult, 0, 245
        ).astype(np.uint8)
        edge_rgba = Image.fromarray(edge_array)
        
        overlay = Image.alpha_composite(overlay, edge_rgba)
    
    # Apply low contrast and grain to marks only so base paper color stays intact
    contrast_factor = {
        'light': 0.95,
        'medium': 0.92,
        'heavy': 0.88,
        'extreme': 0.85
    }.get(aging_level, 0.92)

    overlay_rgb = overlay.convert('RGB')
    overlay_rgb = ImageEnhance.Contrast(overlay_rgb).enhance(contrast_factor)
    overlay = Image.merge('RGBA', (*overlay_rgb.split(), overlay.split()[3]))

    grain_intensity = {
        'light': 0.2,
        'medium': 0.3,
        'heavy': 0.4,
        'extreme': 0.5
    }.get(aging_level, 0.3)

    overlay = apply_grain_to_overlay(overlay, intensity=grain_intensity)

    # --- MULTIPLY BLEND COMPOSITING ---
    # Multiply blend darkens paper while preserving text contrast:
    # result = original * (overlay_color / 255)
    # Text (dark) stays dark; paper (light) picks up stain color.
    # This keeps text readable even at maximum intensity.
    result_arr = np.array(result).astype(np.float32)
    overlay_arr = np.array(overlay).astype(np.float32)
    
    # The overlay alpha channel controls WHERE and HOW MUCH blending occurs
    alpha = overlay_arr[:, :, 3:4] / 255.0
    overlay_rgb = overlay_arr[:, :, :3]
    original_rgb = result_arr[:, :, :3]
    
    # Multiply blend: result = (original * overlay_color) / 255
    multiplied = (original_rgb * overlay_rgb) / 255.0
    
    # Blend using alpha: where alpha=0 → original; where alpha=1 → multiply result
    final_rgb = original_rgb * (1.0 - alpha) + multiplied * alpha
    
    result_arr[:, :, :3] = np.clip(final_rgb, 0, 255)
    result = Image.fromarray(result_arr.astype(np.uint8))
    
    return result, marks_used

# Sidebar controls
st.sidebar.header("⚙️ Aging Parameters")
st.sidebar.markdown("---")

aging_level = st.sidebar.select_slider(
    "Aging Level",
    options=['light', 'medium', 'heavy', 'extreme'],
    value='medium',
    help="Choose the overall aging intensity. Base page color stays unchanged; only localized marks and damage are applied."
)

num_smudges = st.sidebar.slider(
    "Number of Marks",
    min_value=1,
    max_value=40,
    value=15,
    help="How many aging marks to randomly apply (stains, smudges, dust, etc.)"
)

intensity = st.sidebar.slider(
    "Mark Intensity",
    min_value=0.2,
    max_value=1.5,
    value=1.0,
    step=0.1,
    help="Opacity/darkness of individual marks (0.2 = very faint, 1.5 = very dark)"
)

st.sidebar.markdown("---")
st.sidebar.header("📥 Download Options")

download_format = st.sidebar.selectbox(
    "Output Format",
    options=['PNG', 'JPEG', 'BMP', 'TIFF'],
    help="Choose the format for downloaded images"
)

dpi = st.sidebar.slider(
    "DPI (Resolution)",
    min_value=72,
    max_value=600,
    value=300,
    step=50,
    help="Dots per inch for high-quality printing (72=screen, 300=print, 600=high-quality print)"
)

st.sidebar.caption("Each download is automatically compressed to stay under 1 MB per image.")

st.sidebar.markdown("---")
st.sidebar.header("🎯 Learning Preferences")

# Generation mode toggle
generation_mode = st.sidebar.radio(
    "Generation Mode",
    options=['🎲 Random', '⭐ Use My Preferences'],
    index=0 if st.session_state.get('generation_mode', 'random') == 'random' else 1,
    help="Random: equal chance for all mark types. Preferences: biases generation toward your liked mark types."
)
st.session_state['generation_mode'] = 'random' if generation_mode == '🎲 Random' else 'preferred'

if st.session_state['generation_mode'] == 'preferred':
    preferences = load_preferences()
    # Find top 5 preferred marks
    sorted_top = sorted(preferences.items(), key=lambda x: x[1], reverse=True)[:5]
    top_names = [m for m, _ in sorted_top]
    st.sidebar.caption(f"**Top preferred:** {', '.join(top_names)}")

# Reset preferences button
if st.sidebar.button("🔄 Reset All Preferences"):
    if os.path.exists(PREFERENCES_FILE):
        os.remove(PREFERENCES_FILE)
    st.session_state['feedback_given'] = {}
    st.session_state['similar_images'] = {}
    st.sidebar.success("Preferences reset to defaults!")
    st.rerun()

# Show current preferences
with st.sidebar.expander("📊 View your mark type preferences"):
    preferences = load_preferences()
    # Sort by preference value (descending)
    sorted_prefs = sorted(preferences.items(), key=lambda x: x[1], reverse=True)
    
    pref_text = ""
    for mark_type, pref_value in sorted_prefs:
        bar_length = int(min(pref_value * 20, 40))  # Scale to 20 characters, cap at 40
        bar = "█" * bar_length + "░" * max(0, 20 - bar_length)
        emoji = "🔥" if pref_value > 1.3 else "👍" if pref_value > 1.0 else "👎" if pref_value < 0.7 else ""
        pref_text += f"{mark_type:25} {bar} ({pref_value:.2f}) {emoji}\n"
    
    st.code(pref_text, language="")
    st.caption("🔥 = Highly preferred | 👍 = Liked | 👎 = Disliked. Like/dislike results to adjust these.")

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📖 Aging Levels
**Light**: Basic stains and marks only
- Ink blobs, water stains, dust
- Minimal corner darkening

**Medium**: + Stronger localized marks
- More corner aging
- Denser stains and marks
- Age rings and foxing spots

**Heavy**: + Structural damage
- Fold/crease lines (40% chance)
- Small cracks (random)
- Torn paper edges (50% chance)
- Moisture tide marks (40% chance)
- Ink halos and uneven fading
- Maximum corner aging

**Extreme**: Maximum localized damage
- All heavy effects at max
- Multiple folds and cracks
- Torn edges (80% chance)
- Heavy moisture tide marks (70% chance)
- Intense age rings and foxing
- 90% corner darkening chance
- Perfect for ancient, heavily damaged look

💡 **Pro Tips:**
- Each run generates unique patterns
- Extreme + 15-20 marks = very aged look
- Try same settings multiple times for variety
""")


# Main content area
col1, col2 = st.columns(2)

# File uploader - accept multiple files (up to 10)
uploaded_files = st.file_uploader(
    "Upload your manuscript images (up to 10 files)",
    type=['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'],
    accept_multiple_files=True,
    help="Upload clean images with Devanagari or Sanskrit text (PNG, JPG, BMP, TIFF, WebP)"
)

def save_image_with_format(image, format_choice, dpi_value, max_bytes=1_000_000):
    """Save image in specified format with DPI settings under a size limit."""
    # Convert DPI setting to inches for quality
    pil_dpi = (dpi_value, dpi_value)

    def encode_png(img, compress_level=9, use_quantize=False):
        buf = io.BytesIO()
        if use_quantize:
            if img.mode in ['RGBA', 'LA']:
                base = Image.new('RGBA', img.size, (255, 255, 255, 0))
                base.paste(img)
                img = base
            img = img.convert('P', palette=Image.ADAPTIVE, colors=256)
        img.save(buf, format='PNG', dpi=pil_dpi, optimize=True, compress_level=compress_level)
        return buf.getvalue()

    def encode_jpeg(img, quality=95):
        buf = io.BytesIO()
        if img.mode == 'RGBA':
            rgb_image = Image.new('RGB', img.size, (255, 255, 255))
            rgb_image.paste(img, mask=img.split()[3])
            img = rgb_image
        img.save(buf, format='JPEG', quality=quality, dpi=pil_dpi, optimize=True)
        return buf.getvalue()

    def encode_bmp(img):
        buf = io.BytesIO()
        if img.mode == 'RGBA':
            rgb_image = Image.new('RGB', img.size, (255, 255, 255))
            rgb_image.paste(img, mask=img.split()[3])
            img = rgb_image
        img.save(buf, format='BMP', dpi=pil_dpi)
        return buf.getvalue()

    def encode_tiff(img, compression='tiff_deflate'):
        buf = io.BytesIO()
        img.save(buf, format='TIFF', dpi=pil_dpi, compression=compression)
        return buf.getvalue()

    def resize_down(img, scale):
        new_w = max(1, int(img.width * scale))
        new_h = max(1, int(img.height * scale))
        return img.resize((new_w, new_h), Image.LANCZOS)

    working = image.copy()
    extension = {'PNG': 'png', 'JPEG': 'jpg', 'BMP': 'bmp', 'TIFF': 'tif'}.get(format_choice, 'png')

    if format_choice == 'PNG':
        data = encode_png(working, compress_level=9, use_quantize=False)
        if len(data) > max_bytes:
            data = encode_png(working, compress_level=9, use_quantize=True)
        scale = 0.9
        while len(data) > max_bytes and min(working.size) > 400:
            working = resize_down(working, scale)
            data = encode_png(working, compress_level=9, use_quantize=True)

    elif format_choice == 'JPEG':
        quality = 95
        data = encode_jpeg(working, quality=quality)
        while len(data) > max_bytes and quality >= 50:
            quality -= 5
            data = encode_jpeg(working, quality=quality)
        scale = 0.9
        while len(data) > max_bytes and min(working.size) > 400:
            working = resize_down(working, scale)
            data = encode_jpeg(working, quality=max(50, quality))

    elif format_choice == 'BMP':
        data = encode_bmp(working)
        scale = 0.9
        while len(data) > max_bytes and min(working.size) > 400:
            working = resize_down(working, scale)
            data = encode_bmp(working)

    elif format_choice == 'TIFF':
        data = encode_tiff(working, compression='tiff_deflate')
        if len(data) > max_bytes:
            data = encode_tiff(working, compression='tiff_lzw')
        scale = 0.9
        while len(data) > max_bytes and min(working.size) > 400:
            working = resize_down(working, scale)
            data = encode_tiff(working, compression='tiff_deflate')

    else:
        data = encode_png(working, compress_level=9, use_quantize=False)
        extension = 'png'

    return data, extension

if uploaded_files and len(uploaded_files) <= 10:
    st.info(f"📄 {len(uploaded_files)} file(s) uploaded")
    
    # Process button
    mode_label = "⭐ Apply Preferred Aging" if st.session_state.get('generation_mode') == 'preferred' else "🎨 Apply Aging Effect to All"
    if st.button(mode_label, type="primary"):
        with st.spinner(f"Applying authentic aging effects to {len(uploaded_files)} image(s)..."):
            st.session_state['processed_images'] = []
            st.session_state['original_images'] = []
            st.session_state['marks_used'] = []  # Track marks for each image
            st.session_state['feedback_given'] = {}  # Reset feedback for new batch
            st.session_state['similar_images'] = {}  # Reset similar images
            
            for idx, uploaded_file in enumerate(uploaded_files):
                original_image = Image.open(uploaded_file)
                st.session_state['original_images'].append({
                    'name': uploaded_file.name,
                    'image': original_image
                })
                
                # Apply smudges and track mark types
                processed_image, marks_used = apply_smudges(
                    original_image,
                    num_smudges=num_smudges,
                    intensity=intensity,
                    aging_level=aging_level
                )
                
                st.session_state['processed_images'].append({
                    'name': uploaded_file.name,
                    'image': processed_image,
                    'marks_used': marks_used
                })
                st.session_state['marks_used'].append(marks_used)
        
        st.success(f"✨ {len(uploaded_files)} ancient manuscript(s) created successfully!")
    
    # Display images side-by-side if processed
    if 'processed_images' in st.session_state and len(st.session_state['processed_images']) > 0:
        st.markdown("---")
        st.subheader("Results")
        
        # Action buttons row
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            reapply_label = "⭐ Re-Apply Preferred Aging" if st.session_state.get('generation_mode') == 'preferred' else "🎨 Re-Apply Aging Effect to All"
            if st.button(reapply_label, type="primary", key="reapply_aging"):
                with st.spinner(f"Re-applying authentic aging effects to {len(st.session_state['original_images'])} image(s)..."):
                    st.session_state['processed_images'] = []
                    st.session_state['marks_used'] = []
                    st.session_state['feedback_given'] = {}
                    st.session_state['similar_images'] = {}
                    
                    for idx_r, orig_item in enumerate(st.session_state['original_images']):
                        processed_image, marks_used = apply_smudges(
                            orig_item['image'],
                            num_smudges=num_smudges,
                            intensity=intensity,
                            aging_level=aging_level
                        )
                        st.session_state['processed_images'].append({
                            'name': orig_item['name'],
                            'image': processed_image,
                            'marks_used': marks_used
                        })
                        st.session_state['marks_used'].append(marks_used)
                
                st.success(f"✨ {len(st.session_state['original_images'])} ancient manuscript(s) re-created successfully!")
                st.rerun()
        
        with col3:
            if st.button("⬇️ Download All", type="primary"):
                # Create a zip file with all processed images
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for item in st.session_state['processed_images']:
                        base_name = item['name'].rsplit('.', 1)[0]
                        image_data, ext = save_image_with_format(item['image'], download_format, dpi)
                        zip_file.writestr(f"{base_name}.{ext}", image_data)
                
                zip_buffer.seek(0)
                st.download_button(
                    label="📥 Zip File Ready",
                    data=zip_buffer.getvalue(),
                    file_name=f"aged_manuscripts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    type="primary"
                )
        
        st.markdown("---")
        
        # Display each image pair
        for idx, (orig_item, proc_item) in enumerate(zip(st.session_state['original_images'], st.session_state['processed_images'])):
            st.subheader(f"📜 Image {idx + 1}: {orig_item['name']}", divider="orange")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original Document**")
                st.image(orig_item['image'], width='stretch')
            
            with col2:
                st.markdown("**Aged Document**")
                st.image(proc_item['image'], width='stretch')
            
            # Show mark types used
            marks_used = proc_item.get('marks_used', [])
            if marks_used:
                mark_labels = ', '.join([f"`{m}`" for m in marks_used])
                st.caption(f"✨ Created with: {mark_labels}")
            
            # Like/Dislike feedback section with persistent state
            feedback_key = f"feedback_{idx}"
            current_feedback = st.session_state['feedback_given'].get(idx, None)
            
            st.markdown("#### Rate this effect")
            feedback_col1, feedback_col2, feedback_col3, feedback_col4 = st.columns([1, 1, 1, 2])
            
            with feedback_col1:
                like_disabled = current_feedback == 'like'
                like_type = "primary" if current_feedback != 'like' else "secondary"
                if st.button(
                    "👍 Like" if current_feedback != 'like' else "👍 Liked!",
                    key=f"like_{idx}",
                    disabled=like_disabled,
                    type=like_type
                ):
                    new_prefs = adjust_preferences(marks_used, liked=True)
                    st.session_state['feedback_given'][idx] = 'like'
                    st.rerun()
            
            with feedback_col2:
                dislike_disabled = current_feedback == 'dislike'
                dislike_type = "primary" if current_feedback != 'dislike' else "secondary"
                if st.button(
                    "👎 Dislike" if current_feedback != 'dislike' else "👎 Disliked",
                    key=f"dislike_{idx}",
                    disabled=dislike_disabled,
                    type=dislike_type
                ):
                    adjust_preferences(marks_used, liked=False)
                    st.session_state['feedback_given'][idx] = 'dislike'
                    # Clear any similar images for this index
                    if idx in st.session_state['similar_images']:
                        del st.session_state['similar_images'][idx]
                    st.rerun()
            
            with feedback_col3:
                # "Generate Similar" button - only appears after liking
                if current_feedback == 'like' and marks_used:
                    if st.button("🔄 More Like This", key=f"similar_{idx}", type="primary"):
                        with st.spinner("Generating similar images..."):
                            original_img = st.session_state['original_images'][idx]['image']
                            similar = generate_similar_images(
                                original_img,
                                liked_marks=marks_used,
                                num_variations=3,
                                num_smudges=num_smudges,
                                intensity=intensity,
                                aging_level=aging_level
                            )
                            st.session_state['similar_images'][idx] = similar
                        st.rerun()
            
            with feedback_col4:
                if current_feedback == 'like':
                    st.success("✨ Preferences updated! Future images will use more of these mark types.")
                elif current_feedback == 'dislike':
                    st.info("📝 Got it! These mark types will appear less in future generations.")
            
            # Display similar images if generated
            if idx in st.session_state.get('similar_images', {}) and st.session_state['similar_images'][idx]:
                st.markdown("---")
                st.markdown("##### 🎨 Similar Variations (based on your liked marks)")
                similar_cols = st.columns(3)
                
                for sim_idx, (sim_img, sim_marks) in enumerate(st.session_state['similar_images'][idx]):
                    with similar_cols[sim_idx]:
                        st.image(sim_img, caption=f"Variation {sim_idx + 1}", width='stretch')
                        sim_mark_labels = ', '.join([f"`{m}`" for m in sim_marks])
                        st.caption(f"Marks: {sim_mark_labels}")
                        
                        # Like button for similar images to further refine
                        sim_feedback_key = f"sim_feedback_{idx}_{sim_idx}"
                        sim_current = st.session_state['feedback_given'].get(sim_feedback_key, None)
                        
                        sim_like_col, sim_dislike_col = st.columns(2)
                        with sim_like_col:
                            if st.button(
                                "👍" if sim_current != 'like' else "✅",
                                key=f"sim_like_{idx}_{sim_idx}",
                                disabled=sim_current is not None
                            ):
                                adjust_preferences(sim_marks, liked=True)
                                st.session_state['feedback_given'][sim_feedback_key] = 'like'
                                st.rerun()
                        with sim_dislike_col:
                            if st.button(
                                "👎" if sim_current != 'dislike' else "❌",
                                key=f"sim_dislike_{idx}_{sim_idx}",
                                disabled=sim_current is not None
                            ):
                                adjust_preferences(sim_marks, liked=False)
                                st.session_state['feedback_given'][sim_feedback_key] = 'dislike'
                                st.rerun()
                        
                        # Download button for each similar image
                        sim_data, sim_ext = save_image_with_format(sim_img, download_format, dpi)
                        base_name = proc_item['name'].rsplit('.', 1)[0]
                        st.download_button(
                            label=f"📥 Download",
                            data=sim_data,
                            file_name=f"{base_name}.{sim_ext}",
                            mime=f"image/{sim_ext if sim_ext != 'jpg' else 'jpeg'}",
                            key=f"sim_download_{idx}_{sim_idx}"
                        )
                
                # Generate more similar button
                if st.button("🔄 Generate 3 More Variations", key=f"more_similar_{idx}"):
                    with st.spinner("Generating more similar images..."):
                        original_img = st.session_state['original_images'][idx]['image']
                        similar = generate_similar_images(
                            original_img,
                            liked_marks=marks_used,
                            num_variations=3,
                            num_smudges=num_smudges,
                            intensity=intensity,
                            aging_level=aging_level
                        )
                        st.session_state['similar_images'][idx] = similar
                    st.rerun()
            
            st.markdown("---")
            
            # Individual download button
            dl_col1, dl_col2 = st.columns(2)
            
            with dl_col1:
                image_data, ext = save_image_with_format(proc_item['image'], download_format, dpi)
                base_name = proc_item['name'].rsplit('.', 1)[0]
                
                st.download_button(
                    label=f"📥 Download Original Aged ({download_format.upper()})",
                    data=image_data,
                    file_name=f"{base_name}.{ext}",
                    mime=f"image/{ext if ext != 'jpg' else 'jpeg'}",
                    key=f"download_{idx}"
                )
            
            with dl_col2:
                st.caption(f"DPI: {dpi} | Format: {download_format}")
    else:
        # Show preview of originals
        if len(uploaded_files) > 0:
            st.markdown("---")
            st.subheader("Preview")
            
            for idx, uploaded_file in enumerate(uploaded_files):
                original_image = Image.open(uploaded_file)
                st.markdown(f"**Image {idx + 1}: {uploaded_file.name}**")
                st.image(original_image, width='stretch')
            
            st.info("👆 Click the button above to apply aging effects")

elif uploaded_files and len(uploaded_files) > 10:
    st.error("❌ Maximum 10 images allowed. Please remove some files and try again.")

else:
    # Instructions when no file is uploaded
    st.info("👆 Upload up to 10 PNG images to begin the authentication process")
    
    # Example instructions
    with st.expander("📚 How to use this tool"):
        st.markdown("""
        1. **Prepare your images**: Ensure you have clean PNG images of Devanagari or Sanskrit text (up to 10)
        2. **Upload**: Use the file uploader above to select your images
        3. **Adjust parameters**: Use the sidebar sliders and options to control the aging effect
           - **Aging Level**: Choose light, medium, heavy, or extreme weathering
           - **Number of Marks**: How many random stains/marks to apply (1-20)
           - **Mark Intensity**: Darkness of individual marks (0.2-1.5)
           - **Output Format**: PNG, JPEG, BMP, or TIFF
           - **DPI**: 72 (screen), 300 (print), 600 (high-quality print)
        4. **Process**: Click the "Apply Aging Effect to All" button
        5. **Download**: 
           - Download individual images using format-specific buttons
           - Download all images at once as a ZIP file
        
        **🎨 Aging Effects by Level:**
        
        **Light:**
        - 5 mark types (blobs, water stains, fingerprints, dust, streaks)
        - 15+ color variations
        - Basic corner darkening
        
        **Medium:**
        - All light effects PLUS:
        - Low contrast
        - Higher grain
        - More corner aging
        
        **Heavy:**
        - All medium effects PLUS:
        - Fold/crease lines (40% chance)
        - Small cracks (0-2)
        - Maximum corner aging
        
        **Extreme:**
        - ALL effects at maximum intensity!
        - Multiple folds (1-3)
        - Many cracks (2-4)
        - Intense grain and low contrast
        - 90% corner darkening chance
        - Perfect for ancient, heavily damaged look
        
        **📥 Download Format Guide:**
        
        - **PNG**: Best for web and preservation (lossless)
        - **JPEG**: Smallest file size, good for sharing
        - **BMP**: Uncompressed, highest quality but large files
        - **TIFF**: Professional quality, best for printing
        
        **💡 DPI Settings:**
        
        - **72 DPI**: Screen display and web use
        - **300 DPI**: Standard for printing (books, documents)
        - **600 DPI**: High-quality printing and archival
        
        **💡 Recommended Settings:**
        - **Light aging**: Light level, 3-5 marks, 0.4-0.6 intensity
        - **Moderate aging**: Medium level, 6-10 marks, 0.6-0.8 intensity
        - **Heavy aging**: Heavy level, 10-15 marks, 0.8-1.2 intensity
        - **Ancient/Damaged**: Extreme level, 15-20 marks, 1.0-1.5 intensity
        
        **✨ Features:**
        - Batch process up to 10 images at once
        - Each process creates unique random patterns
        - Download all images in one ZIP file
        - Support for multiple output formats
        - Adjustable DPI for printing and archival quality
        - Try multiple times with same settings for variety!
        """)

