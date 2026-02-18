import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import io
import random

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
        ('blob', 0.3),
        ('water_stain', 0.15),
        ('fingerprint', 0.2),
        ('dust', 0.15),
        ('streak', 0.2)
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
            smudge_size = random.randint(int(base_size * 0.06), int(base_size * 0.18))
            smudge_mask = create_organic_blob(smudge_size, irregularity=random.uniform(0.3, 0.6))
            color = random.choice(aging_colors)
            intensity_mod = random.uniform(0.7, 1.3)
            
        elif mark_type == 'water_stain':
            smudge_size = random.randint(int(base_size * 0.15), int(base_size * 0.35))
            smudge_mask = create_water_stain(smudge_size)
            # Water stains are usually lighter, yellowish
            color = random.choice([(180, 150, 90), (165, 135, 85), (150, 130, 70), (140, 120, 80)])
            intensity_mod = random.uniform(0.3, 0.6)  # Very faint
            
        elif mark_type == 'fingerprint':
            smudge_size = random.randint(int(base_size * 0.05), int(base_size * 0.12))
            smudge_mask = create_fingerprint_mark(smudge_size)
            # Fingerprints are usually darker
            color = random.choice([(80, 60, 40), (70, 50, 30), (90, 70, 50)])
            intensity_mod = random.uniform(0.5, 0.9)
            
        elif mark_type == 'dust':
            smudge_size = random.randint(int(base_size * 0.08), int(base_size * 0.15))
            smudge_mask = create_dust_speckles(smudge_size)
            # Dust can be various colors
            color = random.choice(aging_colors)
            intensity_mod = random.uniform(0.4, 0.8)
            
        elif mark_type == 'streak':
            smudge_size = random.randint(int(base_size * 0.08), int(base_size * 0.20))
            smudge_mask = create_streak_mark(smudge_size)
            color = random.choice([(92, 64, 51), (80, 60, 40), (100, 95, 85), (110, 70, 40)])
            intensity_mod = random.uniform(0.5, 1.0)
        
        # Random position with smart bounds checking
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
    
    # Add vignette effect (medium, heavy, extreme)
    if aging_level in ['medium', 'heavy', 'extreme']:
        vignette_strength = {
            'medium': 0.3,
            'heavy': 0.6,
            'extreme': 0.9
        }.get(aging_level, 0.3)
        
        vignette = create_vignette(width, height, vignette_strength)
        vignette_color = (40, 35, 30) if aging_level != 'extreme' else (30, 25, 20)
        vignette_rgba = Image.new('RGBA', (width, height), vignette_color + (0,))
        
        vignette_array = np.array(vignette_rgba)
        vignette_mult = 0.5 if aging_level != 'extreme' else 0.8
        vignette_array[:, :, 3] = (np.array(vignette) * intensity * vignette_mult).astype(np.uint8)
        vignette_rgba = Image.fromarray(vignette_array)
        
        overlay = Image.alpha_composite(overlay, vignette_rgba)
    
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
    
    # Composite with multiply/overlay blend for authentic look
    result = Image.alpha_composite(result, overlay)
    
    # Apply paper grain texture (medium, heavy, extreme)
    if aging_level in ['medium', 'heavy', 'extreme']:
        grain_intensity = {
            'medium': 0.2,
            'heavy': 0.4,
            'extreme': 0.7
        }.get(aging_level, 0.2)
        
        grain = create_paper_grain(width, height, grain_intensity)
        result_array = np.array(result).astype(np.int16)
        
        # Apply grain to RGB channels only
        for c in range(3):
            result_array[:, :, c] = np.clip(result_array[:, :, c] + grain, 0, 255)
        
        result = Image.fromarray(result_array.astype(np.uint8))
    
    # Apply overall paper yellowing (based on aging level)
    yellowing_intensity = {
        'light': 0.0,
        'medium': intensity * 0.3,
        'heavy': intensity * 0.6,
        'extreme': intensity * 0.9
    }.get(aging_level, 0.0)
    
    if yellowing_intensity > 0:
        result = apply_paper_yellowing(result, intensity=yellowing_intensity)
    
    return result

# Sidebar controls
st.sidebar.header("⚙️ Aging Parameters")
st.sidebar.markdown("---")

aging_level = st.sidebar.select_slider(
    "Aging Level",
    options=['light', 'medium', 'heavy', 'extreme'],
    value='medium',
    help="Choose the overall aging intensity: Light (basic marks), Medium (+ texture, yellowing), Heavy (+ folds, vignette), Extreme (maximum weathering)"
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
st.sidebar.markdown("""
### 📖 Aging Levels
**Light**: Basic stains and marks only
- Ink blobs, water stains, dust
- Minimal corner darkening

**Medium**: + Environmental effects
- Paper grain texture
- Slight yellowing/sepia tone
- Vignette (edge darkening)
- More corner aging

**Heavy**: + Structural damage
- Strong yellowing
- Fold/crease lines (40% chance)
- Small cracks (random)
- Heavy vignetting
- Maximum corner aging

**Extreme**: Maximum all effects
- All heavy effects at max
- Multiple folds and cracks
- Intense yellowing
- Heavy texture

💡 **Pro Tips:**
- Each run generates unique patterns
- Extreme + 15-20 marks = very aged look
- Try same settings multiple times for variety
""")

# Main content area
col1, col2 = st.columns(2)

# File uploader
uploaded_file = st.file_uploader(
    "Upload your manuscript image (PNG only)",
    type=['png'],
    help="Upload a clean image with Devanagari or Sanskrit text"
)

if uploaded_file is not None:
    # Load the original image
    original_image = Image.open(uploaded_file)
    
    # Process button
    if st.button("🎨 Apply Aging Effect", type="primary"):
        with st.spinner("Applying authentic aging effects..."):
            # Apply smudges
            processed_image = apply_smudges(
                original_image,
                num_smudges=num_smudges,
                intensity=intensity,
                aging_level=aging_level
            )
            
            # Store in session state
            st.session_state['processed_image'] = processed_image
            st.session_state['original_image'] = original_image
    
    # Display images side-by-side if processed
    if 'processed_image' in st.session_state:
        st.markdown("---")
        st.subheader("Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Original Document**")
            st.image(st.session_state['original_image'], width='stretch')
        
        with col2:
            st.markdown("**Aged Document**")
            st.image(st.session_state['processed_image'], width='stretch')
        
        # Download button
        st.markdown("---")
        
        # Convert processed image to bytes for download
        buf = io.BytesIO()
        st.session_state['processed_image'].save(buf, format='PNG')
        byte_im = buf.getvalue()
        
        st.download_button(
            label="📥 Download Aged Manuscript",
            data=byte_im,
            file_name="aged_manuscript.png",
            mime="image/png",
            type="primary"
        )
        
        st.success("✨ Ancient manuscript created successfully!")
    else:
        # Show preview of original
        st.markdown("---")
        st.subheader("Preview")
        st.image(original_image, caption="Original Image", width='stretch')
        st.info("👆 Click the button above to apply aging effects")
else:
    # Instructions when no file is uploaded
    st.info("👆 Upload a PNG image to begin the authentication process")
    
    # Example instructions
    with st.expander("📚 How to use this tool"):
        st.markdown("""
        1. **Prepare your image**: Ensure you have a clean PNG image of Devanagari or Sanskrit text
        2. **Upload**: Use the file uploader above to select your image
        3. **Adjust parameters**: Use the sidebar sliders to control the aging effect
           - **Aging Level**: Choose light, medium, heavy, or extreme weathering
           - **Number of Marks**: How many random stains/marks to apply (1-20)
           - **Mark Intensity**: Darkness of individual marks (0.2-1.5)
        4. **Process**: Click the "Apply Aging Effect" button
        5. **Download**: Save your aged manuscript using the download button
        
        **🎨 Aging Effects by Level:**
        
        **Light:**
        - 5 mark types (blobs, water stains, fingerprints, dust, streaks)
        - 15+ color variations
        - Basic corner darkening
        
        **Medium:**
        - All light effects PLUS:
        - Paper grain texture
        - Slight yellowing/sepia tone
        - Vignette (edge darkening)
        - More corner aging
        
        **Heavy:**
        - All medium effects PLUS:
        - Strong yellowing
        - Fold/crease lines (40% chance)
        - Small cracks (0-2)
        - Heavy vignetting
        - Maximum corner aging
        
        **Extreme:**
        - ALL effects at maximum intensity!
        - Multiple folds (1-3)
        - Many cracks (2-4)
        - Intense yellowing and grain
        - 90% corner darkening chance
        - Perfect for ancient, heavily damaged look
        
        **💡 Recommended Settings:**
        - **Light aging**: Light level, 3-5 marks, 0.4-0.6 intensity
        - **Moderate aging**: Medium level, 6-10 marks, 0.6-0.8 intensity
        - **Heavy aging**: Heavy level, 10-15 marks, 0.8-1.2 intensity
        - **Ancient/Damaged**: Extreme level, 15-20 marks, 1.0-1.5 intensity
        
        **✨ Each process creates a unique result** - try multiple times with the same settings!
        """)
