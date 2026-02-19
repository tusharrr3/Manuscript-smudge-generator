"""
Generate sample aged manuscript images with authentic weathering effects.
Creates images similar to ancient Devanagari/Sanskrit manuscripts.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random
from datetime import datetime
import os

# Import the aging functions from app.py
import sys
sys.path.insert(0, os.path.dirname(__file__))

# Copy the necessary functions from app.py
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
    num_rings = random.randint(3, 6)
    
    for i in range(num_rings):
        ring_size = int(size * (0.5 + i * 0.3))
        opacity = random.randint(30, 80) // (i + 1)
        
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
    angle = random.randint(0, 360)
    mark = mark.rotate(angle, expand=False)
    
    return mark

def create_dust_speckles(size):
    """Create tiny dust spots or foxing marks."""
    canvas_size = int(size * 2)
    speckles = Image.new('L', (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(speckles)
    
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
    
    corners = {
        'top-left': (0, 0),
        'top-right': (width - corner_size, 0),
        'bottom-left': (0, height - corner_size),
        'bottom-right': (width - corner_size, height - corner_size)
    }
    
    x_start, y_start = corners[corner_position]
    
    for i in range(corner_size):
        opacity = int(100 * (1 - i / corner_size) ** 2)
        if opacity > 5:
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

def create_fold_line(width, height, vertical=True):
    """Create a fold/crease line."""
    fold = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(fold)
    
    if vertical:
        center = random.randint(int(width * 0.3), int(width * 0.7))
        for y in range(height):
            offset = random.randint(-3, 3)
            x = center + offset
            thickness = random.randint(2, 5)
            opacity = random.randint(60, 120)
            draw.line([(x - thickness, y), (x + thickness, y)], fill=opacity, width=thickness)
    else:
        center = random.randint(int(height * 0.3), int(height * 0.7))
        for x in range(width):
            offset = random.randint(-3, 3)
            y = center + offset
            thickness = random.randint(2, 5)
            opacity = random.randint(60, 120)
            draw.line([(x, y - thickness), (x, y + thickness)], fill=opacity, width=thickness)
    
    fold = fold.filter(ImageFilter.GaussianBlur(radius=2))
    return fold

def create_ancient_paper_background(width, height):
    """Create an ancient paper-like background with natural color variations."""
    # Base colors for aged paper (brown/sepia tones like the examples)
    base_colors = [
        (194, 178, 128),  # Light brown/tan
        (186, 168, 120),  # Sandy brown
        (198, 182, 140),  # Lighter tan
        (180, 160, 115),  # Darker tan
    ]
    
    base_color = random.choice(base_colors)
    
    # Create base image
    image = Image.new('RGB', (width, height), base_color)
    img_array = np.array(image).astype(np.float32)
    
    # Add paper grain/texture noise
    for c in range(3):
        noise = np.random.randint(-15, 15, (height, width))
        img_array[:, :, c] = np.clip(img_array[:, :, c] + noise, 0, 255)
    
    # Add subtle color variations
    for _ in range(5):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(100, 300)
        
        color_shift = random.randint(-20, 20)
        for dy in range(-radius, radius):
            for dx in range(-radius, radius):
                px = x + dx
                py = y + dy
                if 0 <= px < width and 0 <= py < height:
                    dist = np.sqrt(dx**2 + dy**2)
                    if dist < radius:
                        factor = 1 - (dist / radius)
                        shift = color_shift * factor
                        img_array[py, px] = np.clip(img_array[py, px] + shift, 0, 255)
    
    return Image.fromarray(img_array.astype(np.uint8))

def apply_aging_effects(image, num_marks=15, intensity=0.8):
    """Apply comprehensive aging effects to create authentic ancient manuscript look."""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    result = image.copy()
    width, height = result.size
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Define mark types
    mark_types = ['blob', 'water_stain', 'fingerprint', 'dust', 'streak']
    
    # Extended color palette matching the reference images
    aging_colors = [
        # Dark brown/black (ink stains)
        (50, 35, 25), (60, 45, 30), (70, 50, 35),
        # Brown tones (aging, oxidation)
        (90, 65, 45), (100, 75, 50), (110, 80, 55),
        # Reddish brown (rust, foxing)
        (130, 70, 50), (120, 65, 45), (140, 80, 60),
        # Yellowish stains
        (150, 120, 70), (140, 110, 65),
        # Gray (mold, dirt)
        (80, 75, 65), (90, 85, 75), (100, 95, 85),
    ]
    
    # Apply random marks
    for i in range(num_marks):
        mark_type = random.choice(mark_types)
        base_size = min(width, height)
        
        if mark_type == 'blob':
            size = random.randint(int(base_size * 0.06), int(base_size * 0.18))
            mask = create_organic_blob(size, irregularity=random.uniform(0.3, 0.7))
            color = random.choice(aging_colors)
            intensity_mod = random.uniform(0.6, 1.4)
            
        elif mark_type == 'water_stain':
            size = random.randint(int(base_size * 0.15), int(base_size * 0.40))
            mask = create_water_stain(size)
            color = random.choice([(140, 110, 65), (150, 120, 70), (130, 100, 60)])
            intensity_mod = random.uniform(0.3, 0.7)
            
        elif mark_type == 'fingerprint':
            size = random.randint(int(base_size * 0.05), int(base_size * 0.12))
            mask = create_fingerprint_mark(size)
            color = random.choice([(70, 50, 35), (60, 45, 30), (80, 55, 40)])
            intensity_mod = random.uniform(0.5, 1.0)
            
        elif mark_type == 'dust':
            size = random.randint(int(base_size * 0.08), int(base_size * 0.15))
            mask = create_dust_speckles(size)
            color = random.choice(aging_colors)
            intensity_mod = random.uniform(0.4, 0.9)
            
        elif mark_type == 'streak':
            size = random.randint(int(base_size * 0.08), int(base_size * 0.22))
            mask = create_streak_mark(size)
            color = random.choice([(90, 65, 45), (80, 60, 40), (100, 70, 50)])
            intensity_mod = random.uniform(0.5, 1.1)
        
        # Random position
        max_x = max(0, width - mask.width)
        max_y = max(0, height - mask.height)
        
        if max_x > 0 and max_y > 0:
            pos_x = random.randint(0, max_x)
            pos_y = random.randint(0, max_y)
            
            # Create colored mark with alpha
            mark_rgba = Image.new('RGBA', mask.size, color + (0,))
            mask_array = np.array(mask)
            adjusted_intensity = intensity * intensity_mod
            mask_array = (mask_array * adjusted_intensity).astype(np.uint8)
            
            mark_array = np.array(mark_rgba)
            mark_array[:, :, 3] = mask_array
            mark_rgba = Image.fromarray(mark_array)
            
            overlay.paste(mark_rgba, (pos_x, pos_y), mark_rgba)
    
    # Add corner aging (high probability)
    for corner in ['top-left', 'top-right', 'bottom-left', 'bottom-right']:
        if random.random() < 0.7:  # 70% chance
            corner_aging = create_corner_aging(width, height, corner)
            corner_color = random.choice([(65, 55, 40), (75, 65, 50), (55, 45, 35)])
            corner_rgba = Image.new('RGBA', (width, height), corner_color + (0,))
            
            corner_array = np.array(corner_rgba)
            corner_mask = np.array(corner_aging)
            corner_array[:, :, 3] = (corner_mask * intensity * 0.7).astype(np.uint8)
            corner_rgba = Image.fromarray(corner_array)
            
            overlay = Image.alpha_composite(overlay, corner_rgba)
    
    # Add fold lines (50% chance)
    if random.random() < 0.5:
        num_folds = random.randint(1, 2)
        for _ in range(num_folds):
            fold = create_fold_line(width, height, vertical=random.choice([True, False]))
            fold_color = random.choice([(65, 55, 45), (70, 60, 50), (60, 50, 40)])
            fold_rgba = Image.new('RGBA', (width, height), fold_color + (0,))
            
            fold_array = np.array(fold_rgba)
            fold_array[:, :, 3] = (np.array(fold) * intensity * 0.8).astype(np.uint8)
            fold_rgba = Image.fromarray(fold_array)
            
            overlay = Image.alpha_composite(overlay, fold_rgba)
    
    # Composite
    result = Image.alpha_composite(result, overlay)
    
    return result

def generate_sample_manuscript(width=1400, height=600, num_marks=15, intensity=0.8, output_name=None):
    """Generate a complete aged manuscript image."""
    print(f"Generating ancient manuscript ({width}x{height})...")
    
    # Create ancient paper background
    manuscript = create_ancient_paper_background(width, height)
    manuscript = manuscript.convert('RGBA')
    
    # Apply aging effects
    manuscript = apply_aging_effects(manuscript, num_marks=num_marks, intensity=intensity)
    
    # Convert back to RGB for saving
    manuscript = manuscript.convert('RGB')
    
    # Save
    if output_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"ancient_manuscript_{timestamp}.png"
    
    manuscript.save(output_name, dpi=(300, 300))
    print(f"✓ Saved: {output_name}")
    
    return manuscript

if __name__ == "__main__":
    print("=" * 60)
    print("Ancient Manuscript Generator")
    print("=" * 60)
    print()
    
    # Create output directory
    output_dir = "sample_manuscripts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate multiple samples with varying parameters
    configs = [
        {"width": 1400, "height": 600, "num_marks": 12, "intensity": 0.7, "name": "moderate_aging"},
        {"width": 1400, "height": 600, "num_marks": 18, "intensity": 0.9, "name": "heavy_aging"},
        {"width": 1200, "height": 500, "num_marks": 15, "intensity": 0.8, "name": "balanced"},
        {"width": 1600, "height": 700, "num_marks": 20, "intensity": 1.0, "name": "extreme_aging"},
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"\n[{i}/{len(configs)}] Generating: {config['name']}")
        output_path = os.path.join(output_dir, f"{config['name']}.png")
        generate_sample_manuscript(
            width=config['width'],
            height=config['height'],
            num_marks=config['num_marks'],
            intensity=config['intensity'],
            output_name=output_path
        )
    
    print("\n" + "=" * 60)
    print(f"✓ Generated {len(configs)} sample manuscripts")
    print(f"✓ Saved in: {os.path.abspath(output_dir)}")
    print("=" * 60)
