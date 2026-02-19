import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import io
import random
import zipfile
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Ancient Manuscript Authenticator",
    page_icon="📜",
    layout="wide"
)

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
""")

def create_organic_blob(size, irregularity=0.3):
    """Create an organic, irregular blob-shaped smudge."""
    canvas_size = int(size * 2)
    smudge = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(smudge)
    
    center = canvas_size // 2
    num_circles = random.randint(8, 15)
    
    for _ in range(num_circles):
        offset_x = random.randint(-int(size * irregularity), int(size * irregularity))
        offset_y = random.randint(-int(size * irregularity), int(size * irregularity))
        radius = random.randint(int(size * 0.3), int(size * 0.7))
        
        x0 = center + offset_x - radius
        y0 = center + offset_y - radius
        x1 = center + offset_x + radius
        y1 = center + offset_y + radius
        
        opacity = random.randint(100, 200)
        draw.ellipse([x0, y0, x1, y1], fill=opacity)
    
    smudge = smudge.filter(ImageFilter.GaussianBlur(radius=size * 0.15))
    smudge = smudge.filter(ImageFilter.GaussianBlur(radius=size * 0.1))
    
    smudge_array = np.array(smudge)
    noise = np.random.randint(-20, 20, smudge_array.shape)
    smudge_array = np.clip(smudge_array.astype(int) + noise, 0, 255).astype(np.uint8)
    smudge = Image.fromarray(smudge_array)
    
    return smudge

def create_water_stain(size):
    """Create a water stain effect - large, very faint, irregular."""
    canvas_size = int(size * 2.5)
    stain = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(stain)
    
    center = canvas_size // 2
    # Create ring-like water stain
    num_rings = random.randint(3, 6)
    
    for i in range(num_rings):
        ring_size = int(size * (0.5 + i * 0.3))
        opacity = random.randint(30, 80) // (i + 1)  # Fainter as rings go outward
        
        for _ in range(random.randint(5, 10)):
            offset_x = random.randint(-ring_size // 3, ring_size // 3)
            offset_y = random.randint(-ring_size // 3, ring_size // 3)
            
            x0 = center + offset_x - ring_size
            y0 = center + offset_y - ring_size
            x1 = center + offset_x + ring_size
            y1 = center + offset_y + ring_size
            
            draw.ellipse([x0, y0, x1, y1], fill=opacity)
    
    stain = stain.filter(ImageFilter.GaussianBlur(radius=size * 0.3))
    return stain

def create_bleeding_ink(size):
    """Create a soft, feathered ink bleed."""
    canvas_size = int(size * 2.2)
    bleed = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(bleed)

    center = canvas_size // 2
    num_blobs = random.randint(6, 12)

    for _ in range(num_blobs):
        offset_x = random.randint(-int(size * 0.5), int(size * 0.5))
        offset_y = random.randint(-int(size * 0.5), int(size * 0.5))
        radius = random.randint(int(size * 0.3), int(size * 0.8))

        x0 = center + offset_x - radius
        y0 = center + offset_y - radius
        x1 = center + offset_x + radius
        y1 = center + offset_y + radius

        opacity = random.randint(60, 140)
        draw.ellipse([x0, y0, x1, y1], fill=opacity)

    bleed = bleed.filter(ImageFilter.GaussianBlur(radius=size * 0.35))
    bleed = bleed.filter(ImageFilter.GaussianBlur(radius=size * 0.2))
    return bleed

def create_coffee_ring(size):
    """Create a coffee ring stain with a darker edge."""
    canvas_size = int(size * 2.6)
    ring = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(ring)

    center = canvas_size // 2
    outer = int(size * 1.1)
    inner = int(size * 0.7)

    for _ in range(random.randint(5, 9)):
        jitter_x = random.randint(-size // 4, size // 4)
        jitter_y = random.randint(-size // 4, size // 4)

        draw.ellipse(
            [center + jitter_x - outer, center + jitter_y - outer,
             center + jitter_x + outer, center + jitter_y + outer],
            fill=random.randint(60, 120)
        )
        draw.ellipse(
            [center + jitter_x - inner, center + jitter_y - inner,
             center + jitter_x + inner, center + jitter_y + inner],
            fill=random.randint(20, 60)
        )

    ring = ring.filter(ImageFilter.GaussianBlur(radius=size * 0.2))
    return ring

def create_soot_stain(size):
    """Create a smoky soot stain."""
    canvas_size = int(size * 2.4)
    soot = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(soot)

    center = canvas_size // 2
    num_clouds = random.randint(10, 18)

    for _ in range(num_clouds):
        offset_x = random.randint(-int(size * 0.7), int(size * 0.7))
        offset_y = random.randint(-int(size * 0.7), int(size * 0.7))
        radius = random.randint(int(size * 0.2), int(size * 0.6))
        opacity = random.randint(40, 110)

        x0 = center + offset_x - radius
        y0 = center + offset_y - radius
        x1 = center + offset_x + radius
        y1 = center + offset_y + radius

        draw.ellipse([x0, y0, x1, y1], fill=opacity)

    soot = soot.filter(ImageFilter.GaussianBlur(radius=size * 0.4))
    return soot

def create_heavy_ink_blotch(size):
    """Create a large, irregular ink blotch with darker edge and splatter."""
    canvas_size = int(size * 2.8)
    blot = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(blot)

    center = canvas_size // 2
    base_radius = int(size * 0.9)

    # Core blob
    for _ in range(random.randint(10, 16)):
        offset_x = random.randint(-int(size * 0.5), int(size * 0.5))
        offset_y = random.randint(-int(size * 0.5), int(size * 0.5))
        radius = random.randint(int(base_radius * 0.4), int(base_radius * 0.9))
        opacity = random.randint(120, 200)

        x0 = center + offset_x - radius
        y0 = center + offset_y - radius
        x1 = center + offset_x + radius
        y1 = center + offset_y + radius

        draw.ellipse([x0, y0, x1, y1], fill=opacity)

    # Darker edge ring
    for _ in range(random.randint(6, 10)):
        ring_radius = random.randint(int(base_radius * 0.9), int(base_radius * 1.2))
        jitter_x = random.randint(-int(size * 0.2), int(size * 0.2))
        jitter_y = random.randint(-int(size * 0.2), int(size * 0.2))
        opacity = random.randint(120, 200)

        draw.ellipse(
            [center + jitter_x - ring_radius, center + jitter_y - ring_radius,
             center + jitter_x + ring_radius, center + jitter_y + ring_radius],
            outline=opacity, width=random.randint(3, 8)
        )

    # Splatter dots
    for _ in range(random.randint(12, 20)):
        dot_x = random.randint(int(canvas_size * 0.15), int(canvas_size * 0.85))
        dot_y = random.randint(int(canvas_size * 0.15), int(canvas_size * 0.85))
        dot_size = random.randint(2, 7)
        opacity = random.randint(80, 160)
        draw.ellipse([dot_x - dot_size, dot_y - dot_size, dot_x + dot_size, dot_y + dot_size], fill=opacity)

    blot = blot.filter(ImageFilter.GaussianBlur(radius=size * 0.18))
    return blot

def create_atmospheric_grime(size):
    """Create a diffuse grime patch with soft texture."""
    canvas_size = int(size * 2.4)
    grime = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(grime)

    center = canvas_size // 2
    num_spots = random.randint(12, 20)

    for _ in range(num_spots):
        offset_x = random.randint(-int(size * 0.8), int(size * 0.8))
        offset_y = random.randint(-int(size * 0.8), int(size * 0.8))
        radius = random.randint(int(size * 0.15), int(size * 0.5))
        opacity = random.randint(30, 90)

        x0 = center + offset_x - radius
        y0 = center + offset_y - radius
        x1 = center + offset_x + radius
        y1 = center + offset_y + radius

        draw.ellipse([x0, y0, x1, y1], fill=opacity)

    grime = grime.filter(ImageFilter.GaussianBlur(radius=size * 0.35))
    return grime

def create_torn_paper_edge(width, height):
    """Create torn/ragged paper edges along document borders."""
    torn = Image.new('L', (width, height), 255)
    draw = ImageDraw.Draw(torn)

    # Top edge
    for x in range(width):
        tear_offset = random.randint(0, 25)
        tear_intensity = random.randint(80, 200)
        draw.line([(x, 0), (x, tear_offset)], fill=tear_intensity, width=random.randint(1, 3))

    # Bottom edge
    for x in range(width):
        tear_offset = random.randint(0, 25)
        tear_intensity = random.randint(80, 200)
        draw.line([(x, height - 1), (x, height - 1 - tear_offset)], fill=tear_intensity, width=random.randint(1, 3))

    # Left edge
    for y in range(height):
        tear_offset = random.randint(0, 25)
        tear_intensity = random.randint(80, 200)
        draw.line([(0, y), (tear_offset, y)], fill=tear_intensity, width=random.randint(1, 3))

    # Right edge
    for y in range(height):
        tear_offset = random.randint(0, 25)
        tear_intensity = random.randint(80, 200)
        draw.line([(width - 1, y), (width - 1 - tear_offset, y)], fill=tear_intensity, width=random.randint(1, 3))

    # Add irregular jagged pattern
    torn_array = np.array(torn, dtype=np.float32)
    edge_noise = np.random.randint(-30, 30, (height, width), dtype=np.int16)
    torn_array = np.clip(torn_array + edge_noise * 0.3, 0, 255)

    torn = Image.fromarray(torn_array.astype(np.uint8))
    torn = torn.filter(ImageFilter.GaussianBlur(radius=1.5))
    return torn

def create_age_rings(size):
    """Create concentric age rings - like water rings from aging."""
    canvas_size = int(size * 2.2)
    rings = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(rings)
    
    center = canvas_size // 2
    base_radius = int(size * 0.7)
    
    # Create concentric rings
    for i in range(base_radius, 0, -8):
        opacity = random.randint(40, 90)
        draw.ellipse(
            [center - i, center - i, center + i, center + i],
            outline=opacity,
            width=random.randint(2, 5)
        )
    
    rings = rings.filter(ImageFilter.GaussianBlur(radius=size * 0.15))
    return rings

def create_ink_halo(size):
    """Create a soft ink seepage halo around text."""
    canvas_size = int(size * 2.4)
    halo = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(halo)
    
    center = canvas_size // 2
    base_radius = int(size * 0.8)
    
    # Create soft radiating halo
    for radius in range(base_radius, 0, -2):
        opacity = int(120 * (1 - (base_radius - radius) / base_radius) ** 0.8)
        draw.ellipse(
            [center - radius, center - radius, center + radius, center + radius],
            fill=opacity
        )
    
    halo = halo.filter(ImageFilter.GaussianBlur(radius=size * 0.3))
    return halo

def create_foxing_spots(size):
    """Create foxing - brown aging spots common in old manuscripts."""
    canvas_size = int(size * 2)
    foxing = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(foxing)
    
    center = canvas_size // 2
    num_spots = random.randint(3, 8)
    
    for _ in range(num_spots):
        offset_x = random.randint(-int(size * 0.4), int(size * 0.4))
        offset_y = random.randint(-int(size * 0.4), int(size * 0.4))
        spot_radius = random.randint(int(size * 0.15), int(size * 0.4))
        opacity = random.randint(100, 150)
        
        x0 = center + offset_x - spot_radius
        y0 = center + offset_y - spot_radius
        x1 = center + offset_x + spot_radius
        y1 = center + offset_y + spot_radius
        
        draw.ellipse([x0, y0, x1, y1], fill=opacity)
    
    foxing = foxing.filter(ImageFilter.GaussianBlur(radius=size * 0.12))
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
    num_patches = random.randint(4, 9)
    
    for _ in range(num_patches):
        offset_x = random.randint(-int(size * 0.7), int(size * 0.7))
        offset_y = random.randint(-int(size * 0.7), int(size * 0.7))
        patch_size = random.randint(int(size * 0.3), int(size * 0.7))
        opacity = random.randint(30, 90)
        
        x0 = center + offset_x - patch_size
        y0 = center + offset_y - patch_size
        x1 = center + offset_x + patch_size
        y1 = center + offset_y + patch_size
        
        draw.ellipse([x0, y0, x1, y1], fill=opacity)
    
    fade = fade.filter(ImageFilter.GaussianBlur(radius=size * 0.25))
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
                draw.ellipse([cx - spot_radius, cy - spot_radius, cx + spot_radius, cy + spot_radius], fill=opacity)
    
    rust = rust.filter(ImageFilter.GaussianBlur(radius=3))
    return rust

def create_text_area_smudge(size):
    """Create smudges and halos around text areas."""
    canvas_size = int(size * 2.5)
    smudge = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(smudge)
    
    center = canvas_size // 2
    
    # Create irregular text-like smudge pattern
    num_marks = random.randint(4, 8)
    for _ in range(num_marks):
        mark_x = random.randint(int(center * 0.3), int(center * 1.7))
        mark_y = random.randint(int(center * 0.1), int(center * 1.9))
        mark_width = random.randint(int(size * 0.3), int(size * 0.8))
        mark_height = random.randint(int(size * 0.1), int(size * 0.3))
        opacity = random.randint(70, 140)
        
        draw.ellipse([mark_x - mark_width, mark_y - mark_height, mark_x + mark_width, mark_y + mark_height], fill=opacity)
    
    smudge = smudge.filter(ImageFilter.GaussianBlur(radius=size * 0.2))
    return smudge

def create_edge_darkening(width, height):
    """Create darkened edges from handling and aging."""
    edges = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(edges)
    
    # Darken all edges with varying intensity
    edge_width = random.randint(15, 50)
    
    # Top edge
    for y in range(edge_width):
        opacity = int(150 * (1 - y / edge_width) ** 1.2)
        draw.line([(0, y), (width, y)], fill=opacity, width=1)
    
    # Bottom edge
    for y in range(height - edge_width, height):
        opacity = int(150 * ((y - (height - edge_width)) / edge_width) ** 1.2)
        draw.line([(0, y), (width, y)], fill=opacity, width=1)
    
    # Left edge
    for x in range(edge_width):
        opacity = int(150 * (1 - x / edge_width) ** 1.2)
        draw.line([(x, 0), (x, height)], fill=opacity, width=1)
    
    # Right edge
    for x in range(width - edge_width, width):
        opacity = int(150 * ((x - (width - edge_width)) / edge_width) ** 1.2)
        draw.line([(x, 0), (x, height)], fill=opacity, width=1)
    
    edges = edges.filter(ImageFilter.GaussianBlur(radius=2))
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
        
        opacity = random.randint(80, 150)
        draw.ellipse([x0, y0, x1, y1], fill=opacity)
    
    mark = mark.filter(ImageFilter.GaussianBlur(radius=size * 0.08))
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
        opacity = random.randint(100, 180)
        
        draw.ellipse([x - spot_size, y - spot_size, x + spot_size, y + spot_size], fill=opacity)
    
    speckles = speckles.filter(ImageFilter.GaussianBlur(radius=1))
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
    """Create vignette/edge darkening effect."""
    vignette = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(vignette)
    
    # Create gradient from edges
    center_x, center_y = width // 2, height // 2
    max_dist = np.sqrt(center_x**2 + center_y**2)
    
    for y in range(height):
        for x in range(width):
            dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            darkness = int(min(200, (dist / max_dist) * 180 * strength))
            if darkness > 0:
                draw.point((x, y), fill=darkness)
    
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
        PIL Image with aging effects applied
    """
    # Convert to RGBA if not already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Create a copy to work on
    result = image.copy()
    width, height = result.size
    
    # Create overlay layer
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Define different mark types with their probabilities
    mark_types = [
        ('blob', 0.13),
        ('water_stain', 0.09),
        ('fingerprint', 0.09),
        ('dust', 0.07),
        ('streak', 0.09),
        ('bleeding_ink', 0.06),
        ('faded_ink', 0.05),
        ('smudged_calligraphy', 0.06),
        ('moisture_damage', 0.05),
        ('soot_stain', 0.04),
        ('atmospheric_grime', 0.04),
        ('coffee_mark', 0.03),
        ('muddy_mark', 0.03),
        ('heavy_ink_blotch', 0.03),
        ('age_rings', 0.05),
        ('ink_halo', 0.05),
        ('foxing_spots', 0.06),
        ('uneven_fading', 0.05),
        ('text_area_smudge', 0.06),
        ('rust_stains', 0.04)
    ]
    
    # Extended color palette for natural aging
    aging_colors = [
        # Brown/Sepia tones (ink stains)
        (101, 67, 33), (92, 64, 51), (80, 60, 40), (70, 50, 30),
        # Yellowish tones (aging paper, yellowing)
        (180, 150, 90), (165, 135, 85), (150, 130, 70),
        # Grayish tones (mold, dirt, dust)
        (120, 115, 100), (100, 95, 85), (90, 85, 75),
        # Reddish brown (rust, foxing spots)
        (130, 80, 50), (110, 70, 40), (140, 90, 60),
        # Greenish gray (moisture, mildew)
        (100, 110, 90), (85, 95, 80),
        # Dark grays (soot, dirt)
        (60, 55, 50), (75, 70, 65)
    ]

    ink_colors = [
        (35, 35, 35), (45, 40, 40), (60, 60, 60), (70, 70, 70)
    ]

    coffee_colors = [
        (120, 80, 50), (110, 70, 40), (130, 85, 55), (145, 95, 60)
    ]

    grime_colors = [
        (90, 85, 75), (85, 80, 70), (100, 95, 85), (75, 70, 65)
    ]
    
    # Apply random marks
    for i in range(num_smudges):
        # Choose random mark type based on weights
        mark_type = random.choices(
            [t[0] for t in mark_types],
            weights=[t[1] for t in mark_types]
        )[0]
        
        # Variable size for each mark
        base_size = min(width, height)
        
        if mark_type == 'blob':
            smudge_size = random.randint(int(base_size * 0.10), int(base_size * 0.28))
            smudge_mask = create_organic_blob(smudge_size, irregularity=random.uniform(0.3, 0.6))
            color = random.choice(aging_colors)
            intensity_mod = random.uniform(1.0, 1.6)
            
        elif mark_type == 'water_stain':
            smudge_size = random.randint(int(base_size * 0.20), int(base_size * 0.45))
            smudge_mask = create_water_stain(smudge_size)
            # Water stains are usually lighter, yellowish
            color = random.choice([(180, 150, 90), (165, 135, 85), (150, 130, 70), (140, 120, 80)])
            intensity_mod = random.uniform(0.5, 0.9)  # More visible
            
        elif mark_type == 'fingerprint':
            smudge_size = random.randint(int(base_size * 0.08), int(base_size * 0.18))
            smudge_mask = create_fingerprint_mark(smudge_size)
            # Fingerprints are usually darker
            color = random.choice([(80, 60, 40), (70, 50, 30), (90, 70, 50)])
            intensity_mod = random.uniform(0.7, 1.2)
            
        elif mark_type == 'dust':
            smudge_size = random.randint(int(base_size * 0.12), int(base_size * 0.22))
            smudge_mask = create_dust_speckles(smudge_size)
            # Dust can be various colors
            color = random.choice(aging_colors)
            intensity_mod = random.uniform(0.6, 1.0)
            
        elif mark_type == 'streak':
            smudge_size = random.randint(int(base_size * 0.12), int(base_size * 0.32))
            smudge_mask = create_streak_mark(smudge_size)
            color = random.choice([(92, 64, 51), (80, 60, 40), (100, 95, 85), (110, 70, 40)])
            intensity_mod = random.uniform(0.7, 1.3)

        elif mark_type == 'bleeding_ink':
            smudge_size = random.randint(int(base_size * 0.08), int(base_size * 0.18))
            smudge_mask = create_bleeding_ink(smudge_size)
            color = random.choice(ink_colors)
            intensity_mod = random.uniform(0.6, 1.1)

        elif mark_type == 'faded_ink':
            smudge_size = random.randint(int(base_size * 0.06), int(base_size * 0.14))
            smudge_mask = create_organic_blob(smudge_size, irregularity=random.uniform(0.2, 0.5))
            color = random.choice([(80, 80, 80), (95, 95, 95), (110, 110, 110)])
            intensity_mod = random.uniform(0.4, 0.8)

        elif mark_type == 'smudged_calligraphy':
            smudge_size = random.randint(int(base_size * 0.08), int(base_size * 0.20))
            smudge_mask = create_streak_mark(smudge_size)
            color = random.choice(ink_colors)
            intensity_mod = random.uniform(0.8, 1.4)

        elif mark_type == 'moisture_damage':
            smudge_size = random.randint(int(base_size * 0.22), int(base_size * 0.42))
            smudge_mask = create_water_stain(smudge_size)
            color = random.choice([(120, 125, 110), (110, 115, 100), (130, 135, 120)])
            intensity_mod = random.uniform(0.5, 0.85)

        elif mark_type == 'soot_stain':
            smudge_size = random.randint(int(base_size * 0.15), int(base_size * 0.32))
            smudge_mask = create_soot_stain(smudge_size)
            color = random.choice([(40, 40, 40), (55, 50, 50), (60, 60, 60)])
            intensity_mod = random.uniform(0.7, 1.2)

        elif mark_type == 'atmospheric_grime':
            smudge_size = random.randint(int(base_size * 0.16), int(base_size * 0.36))
            smudge_mask = create_atmospheric_grime(smudge_size)
            color = random.choice(grime_colors)
            intensity_mod = random.uniform(0.5, 0.9)

        elif mark_type == 'coffee_mark':
            smudge_size = random.randint(int(base_size * 0.16), int(base_size * 0.36))
            smudge_mask = create_coffee_ring(smudge_size)
            color = random.choice(coffee_colors)
            intensity_mod = random.uniform(0.6, 1.1)

        elif mark_type == 'muddy_mark':
            smudge_size = random.randint(int(base_size * 0.12), int(base_size * 0.28))
            smudge_mask = create_organic_blob(smudge_size, irregularity=random.uniform(0.4, 0.7))
            color = random.choice([(90, 70, 50), (100, 80, 55), (80, 60, 40)])
            intensity_mod = random.uniform(0.8, 1.4)

        elif mark_type == 'heavy_ink_blotch':
            smudge_size = random.randint(int(base_size * 0.18), int(base_size * 0.36))
            smudge_mask = create_heavy_ink_blotch(smudge_size)
            color = random.choice([(35, 35, 35), (45, 40, 40), (25, 25, 25)])
            intensity_mod = random.uniform(1.0, 1.5)

        elif mark_type == 'age_rings':
            smudge_size = random.randint(int(base_size * 0.20), int(base_size * 0.40))
            smudge_mask = create_age_rings(smudge_size)
            color = random.choice([(150, 130, 100), (140, 120, 85), (160, 140, 110), (145, 125, 95)])
            intensity_mod = random.uniform(0.6, 1.0)

        elif mark_type == 'ink_halo':
            smudge_size = random.randint(int(base_size * 0.12), int(base_size * 0.26))
            smudge_mask = create_ink_halo(smudge_size)
            color = random.choice([(80, 70, 55), (70, 60, 45), (90, 80, 65)])
            intensity_mod = random.uniform(0.5, 0.9)

        elif mark_type == 'foxing_spots':
            smudge_size = random.randint(int(base_size * 0.14), int(base_size * 0.30))
            smudge_mask = create_foxing_spots(smudge_size)
            color = random.choice([(140, 100, 60), (130, 90, 50), (150, 110, 70), (125, 85, 45)])
            intensity_mod = random.uniform(0.7, 1.2)

        elif mark_type == 'uneven_fading':
            smudge_size = random.randint(int(base_size * 0.16), int(base_size * 0.36))
            smudge_mask = create_uneven_fading(smudge_size)
            color = random.choice([(110, 105, 95), (120, 115, 105), (100, 95, 85)])
            intensity_mod = random.uniform(0.5, 0.85)

        elif mark_type == 'text_area_smudge':
            smudge_size = random.randint(int(base_size * 0.12), int(base_size * 0.28))
            smudge_mask = create_text_area_smudge(smudge_size)
            color = random.choice([(70, 65, 55), (85, 80, 70), (65, 60, 50)])
            intensity_mod = random.uniform(0.7, 1.2)

        elif mark_type == 'rust_stains':
            # Rust stains are full-width, so we handle them differently
            smudge_mask = create_rust_stains(width, height)
            color = random.choice([(160, 90, 60), (150, 85, 50), (170, 100, 70), (145, 80, 45)])
            intensity_mod = random.uniform(0.4, 0.8)
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
        # Calculate maximum valid positions
        max_x = max(0, width - smudge_mask.width)
        max_y = max(0, height - smudge_mask.height)
        
        # Calculate margin with safety checks
        edge_bias = random.uniform(0.5, 1.5)
        margin = int(smudge_size * edge_bias)
        margin = max(0, min(margin, min(width, height) // 4))
        
        # Sometimes place marks near edges or corners for natural look
        if random.random() < 0.3 and max_x > 0 and max_y > 0:  # 30% chance of edge placement
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
        mask_array = np.array(smudge_mask)
        adjusted_intensity = intensity * intensity_mod
        mask_array = (mask_array * adjusted_intensity).astype(np.uint8)
        
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
    
    # Add fold lines (heavy and extreme)
    if aging_level in ['heavy', 'extreme']:
        fold_prob = 0.4 if aging_level == 'heavy' else 0.7
        num_folds = 1 if aging_level == 'heavy' else random.randint(1, 3)
        
        for _ in range(num_folds):
            if random.random() < fold_prob:
                fold = create_fold_line(width, height, vertical=random.choice([True, False]))
                fold_color = random.choice([(70, 60, 50), (80, 70, 60), (60, 50, 40)])
                fold_rgba = Image.new('RGBA', (width, height), fold_color + (0,))
                
                fold_intensity_mult = 0.7 if aging_level == 'heavy' else 1.0
                fold_array = np.array(fold_rgba)
                fold_array[:, :, 3] = (np.array(fold) * intensity * fold_intensity_mult).astype(np.uint8)
                fold_rgba = Image.fromarray(fold_array)
                
                overlay = Image.alpha_composite(overlay, fold_rgba)
    
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
    
    # Add edge darkening (present on all images, varying by aging level)
    if random.random() < (0.5 if aging_level == 'light' else 0.7 if aging_level == 'medium' else 0.85):
        edge_dark = create_edge_darkening(width, height)
        edge_color = random.choice([(80, 70, 55), (90, 75, 60), (70, 60, 45)])
        edge_rgba = Image.new('RGBA', (width, height), edge_color + (0,))
        
        edge_intensity_mult = 0.3 if aging_level == 'light' else 0.5 if aging_level == 'medium' else 0.7 if aging_level == 'heavy' else 0.9
        edge_array = np.array(edge_rgba)
        edge_array[:, :, 3] = (np.array(edge_dark) * intensity * edge_intensity_mult).astype(np.uint8)
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

    # Composite with multiply/overlay blend for authentic look
    result = Image.alpha_composite(result, overlay)
    
    return result

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
    max_value=20,
    value=8,
    help="How many aging marks to randomly apply (stains, smudges, dust, etc.)"
)

intensity = st.sidebar.slider(
    "Mark Intensity",
    min_value=0.2,
    max_value=1.5,
    value=0.7,
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
    "Upload your manuscript images (PNG only, up to 10 files)",
    type=['png'],
    accept_multiple_files=True,
    help="Upload clean images with Devanagari or Sanskrit text"
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
    if st.button("🎨 Apply Aging Effect to All", type="primary"):
        with st.spinner(f"Applying authentic aging effects to {len(uploaded_files)} image(s)..."):
            st.session_state['processed_images'] = []
            st.session_state['original_images'] = []
            
            for idx, uploaded_file in enumerate(uploaded_files):
                original_image = Image.open(uploaded_file)
                st.session_state['original_images'].append({
                    'name': uploaded_file.name,
                    'image': original_image
                })
                
                # Apply smudges
                processed_image = apply_smudges(
                    original_image,
                    num_smudges=num_smudges,
                    intensity=intensity,
                    aging_level=aging_level
                )
                
                st.session_state['processed_images'].append({
                    'name': uploaded_file.name,
                    'image': processed_image
                })
        
        st.success(f"✨ {len(uploaded_files)} ancient manuscript(s) created successfully!")
    
    # Display images side-by-side if processed
    if 'processed_images' in st.session_state and len(st.session_state['processed_images']) > 0:
        st.markdown("---")
        st.subheader("Results")
        
        # Download All button
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col3:
            if st.button("⬇️ Download All", type="primary"):
                # Create a zip file with all processed images
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for item in st.session_state['processed_images']:
                        base_name = item['name'].rsplit('.', 1)[0]
                        image_data, ext = save_image_with_format(item['image'], download_format, dpi)
                        zip_file.writestr(f"{base_name}_aged.{ext}", image_data)
                
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
                st.image(orig_item['image'], use_container_width=True)
            
            with col2:
                st.markdown("**Aged Document**")
                st.image(proc_item['image'], use_container_width=True)
            
            # Individual download button
            col1, col2 = st.columns(2)
            
            with col1:
                image_data, ext = save_image_with_format(proc_item['image'], download_format, dpi)
                base_name = proc_item['name'].rsplit('.', 1)[0]
                
                st.download_button(
                    label=f"📥 Download ({download_format.upper()})",
                    data=image_data,
                    file_name=f"{base_name}_aged.{ext}",
                    mime=f"image/{ext if ext != 'jpg' else 'jpeg'}",
                    key=f"download_{idx}"
                )
            
            with col2:
                st.caption(f"DPI: {dpi} | Format: {download_format}")
    else:
        # Show preview of originals
        if len(uploaded_files) > 0:
            st.markdown("---")
            st.subheader("Preview")
            
            for idx, uploaded_file in enumerate(uploaded_files):
                original_image = Image.open(uploaded_file)
                st.markdown(f"**Image {idx + 1}: {uploaded_file.name}**")
                st.image(original_image, use_container_width=True)
            
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

