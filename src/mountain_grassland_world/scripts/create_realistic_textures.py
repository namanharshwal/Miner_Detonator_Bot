#!/usr/bin/env python3
"""
High-Fidelity Photorealistic PBR Texture Generator for Alpine Mountain Grassland
Creates:
1. alpine_grass_meadow_albedo.png (2048x2048)
2. alpine_grass_meadow_normal.png (2048x2048)
3. alpine_grass_meadow_roughness.png (2048x2048)
4. mountain_rock_cliff_albedo.png (2048x2048)
5. mountain_rock_cliff_normal.png (2048x2048)
6. mountain_rock_cliff_roughness.png (2048x2048)
7. alpine_pine_foliage.png (1024x1024 RGBA)
8. alpine_pine_foliage_normal.png (1024x1024)
9. alpine_pine_bark.png (1024x1024)
10. alpine_pine_bark_normal.png (1024x1024)
11. alpine_wildflower_poppy.png (1024x1024 RGBA)
12. alpine_wildflower_buttercup.png (1024x1024 RGBA)
13. alpine_wildflower_daisy.png (1024x1024 RGBA)
14. alpine_wildflower_gentian.png (1024x1024 RGBA)
15. alpine_dwarf_rhododendron.png (1024x1024 RGBA)
"""

import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

TEX_DIR = '/home/nammy/army_mine_bot/src/mountain_grassland_world/materials/textures'
os.makedirs(TEX_DIR, exist_ok=True)


def sobel_normal_map(img_gray, strength=2.5):
    """Generate tangent-space normal map (RGB) from grayscale heightmap using pure NumPy Sobel slicing."""
    arr = np.array(img_gray, dtype=np.float32) / 255.0
    p = np.pad(arr, 1, mode='wrap')
    
    # Sobel kernels via vector slicing:
    dx = ((p[:-2, 2:] + 2.0 * p[1:-1, 2:] + p[2:, 2:]) - 
          (p[:-2, :-2] + 2.0 * p[1:-1, :-2] + p[2:, :-2])) * (strength / 8.0)
    dy = ((p[2:, :-2] + 2.0 * p[2:, 1:-1] + p[2:, 2:]) - 
          (p[:-2, :-2] + 2.0 * p[:-2, 1:-1] + p[:-2, 2:])) * (strength / 8.0)
    dz = np.ones_like(dx)
    
    norm = np.sqrt(dx**2 + dy**2 + dz**2)
    nx = -dx / norm
    ny = -dy / norm
    nz = dz / norm
    
    r = np.clip((nx * 0.5 + 0.5) * 255, 0, 255).astype(np.uint8)
    g = np.clip((ny * 0.5 + 0.5) * 255, 0, 255).astype(np.uint8)
    b = np.clip((nz * 0.5 + 0.5) * 255, 0, 255).astype(np.uint8)
    
    normal_img = Image.fromarray(np.stack([r, g, b], axis=-1), mode='RGB')
    return normal_img


def generate_grass_meadow_pbr():
    print("🌾 Generating Photorealistic Alpine Grass Meadow PBR Set (2048x2048)...")
    w, h = 2048, 2048
    np.random.seed(42)
    random.seed(42)

    # 1. Base Soil & Turf Matrix (Multi-octave noise)
    x = np.linspace(0, 16 * np.pi, w)
    y = np.linspace(0, 16 * np.pi, h)
    X, Y = np.meshgrid(x, y)
    
    # Multi-frequency organic undulation
    n1 = np.sin(X * 0.5) * np.cos(Y * 0.4)
    n2 = np.sin(X * 1.8 + 1.2) * np.sin(Y * 1.5 - 0.7) * 0.5
    n3 = np.cos(X * 4.2 - Y * 2.1) * 0.25
    n_total = (n1 + n2 + n3 + 1.75) / 3.5  # [0, 1]
    
    # Fine soil grain
    grain = np.random.normal(0, 12, (h, w, 3))
    
    # Soil tones: humus brown [52, 44, 32] to dark mossy loam [42, 65, 34] to lush turf base [50, 95, 40]
    base_col1 = np.array([45, 40, 30], dtype=np.float32)
    base_col2 = np.array([52, 98, 42], dtype=np.float32)
    
    base_rgb = np.zeros((h, w, 3), dtype=np.float32)
    for c in range(3):
        base_rgb[:, :, c] = base_col1[c] * (1.0 - n_total) + base_col2[c] * n_total
    
    base_rgb = np.clip(base_rgb + grain, 0, 255).astype(np.uint8)
    img = Image.fromarray(base_rgb).filter(ImageFilter.GaussianBlur(1.0))
    draw = ImageDraw.Draw(img)

    # 2. Organic Footpath / Dirt Trail streaks
    for path_y in [512, 1400]:
        for step_x in range(0, w, 4):
            offset_y = int(path_y + 120 * math.sin(step_x * 0.005) + 35 * math.sin(step_x * 0.02))
            rad = random.randint(35, 65)
            draw.ellipse([step_x - rad, offset_y - rad // 2, step_x + rad, offset_y + rad // 2],
                         fill=(random.randint(60, 78), random.randint(52, 68), random.randint(40, 52)))

    # 3. Dense Realistic Grass Blades (180,000 blades in natural palettes)
    blade_palettes = [
        # Alpine fescue (golden-olive)
        (96, 148, 62), (108, 162, 70), (88, 138, 55),
        # Mountain ryegrass (emerald / forest)
        (48, 102, 40), (58, 120, 48), (40, 88, 34), (66, 135, 54),
        # High-altitude bluegrass
        (35, 82, 38), (52, 110, 52), (72, 145, 65),
        # Sun-dried tips / thatch
        (135, 148, 76), (148, 158, 88), (122, 132, 65),
        # Dark shadows
        (28, 60, 24), (22, 50, 18)
    ]

    print("  -> Drawing 180,000 fine grass blades and turf filaments...")
    for _ in range(180000):
        bx = random.randint(0, w - 1)
        by = random.randint(0, h - 1)
        blen = random.randint(6, 20)
        # Slight natural wind tilt to Northeast
        b_angle = random.gauss(0.25, 0.45)
        ex = int(bx + blen * math.sin(b_angle))
        ey = int(by - blen * math.cos(b_angle))
        col = random.choice(blade_palettes)
        b_width = 1 if blen < 14 else 2
        draw.line([(bx, by), (ex, ey)], fill=col, width=b_width)

    # 4. Alpine Clover & Groundcover Flecks (12,000 micro-leaves)
    print("  -> Scattering alpine clover and herbal leaves...")
    for _ in range(12000):
        cx = random.randint(0, w - 1)
        cy = random.randint(0, h - 1)
        c_rad = random.randint(2, 5)
        c_col = (random.randint(65, 120), random.randint(130, 180), random.randint(55, 95))
        for lobe in [0, 2.09, 4.18]:
            lx = int(cx + c_rad * math.cos(lobe))
            ly = int(cy + c_rad * math.sin(lobe))
            draw.ellipse([lx - c_rad, ly - c_rad, lx + c_rad, ly + c_rad], fill=c_col)

    # 5. Scattered Alpine Slate Pebbles (3,000 pebbles)
    for _ in range(3000):
        px = random.randint(0, w - 1)
        py = random.randint(0, h - 1)
        prx = random.randint(2, 6)
        pry = random.randint(1, 4)
        p_col = (random.randint(100, 135), random.randint(102, 132), random.randint(105, 135))
        draw.ellipse([px - prx, py - pry, px + prx, py + pry], fill=p_col)

    # Save Albedo
    albedo_path = os.path.join(TEX_DIR, 'alpine_grass_meadow.png')
    albedo_pbr = os.path.join(TEX_DIR, 'alpine_grass_meadow_albedo.png')
    img.save(albedo_path, quality=95)
    img.save(albedo_pbr, quality=95)
    print(f"  -> Saved Albedo: {albedo_path}")

    # 6. Generate Normal Map
    print("  -> Generating Tangent-Space Normal Map...")
    gray_img = img.convert('L').filter(ImageFilter.GaussianBlur(0.8))
    normal_img = sobel_normal_map(gray_img, strength=3.0)
    normal_path = os.path.join(TEX_DIR, 'alpine_grass_meadow_normal.png')
    normal_img.save(normal_path, quality=95)
    print(f"  -> Saved Normal Map: {normal_path}")

    # 7. Generate Roughness Map
    # Grass ~ 0.75, Soil ~ 0.92, Pebbles ~ 0.50
    gray_arr = np.array(gray_img, dtype=np.float32)
    rough_arr = np.clip(255 - gray_arr * 0.45 + np.random.normal(0, 8, (h, w)), 120, 250).astype(np.uint8)
    rough_img = Image.fromarray(rough_arr, mode='L')
    rough_path = os.path.join(TEX_DIR, 'alpine_grass_meadow_roughness.png')
    rough_img.save(rough_path, quality=95)
    print(f"  -> Saved Roughness Map: {rough_path}")


def generate_granite_cliff_pbr():
    print("🪨 Generating High-Altitude Metamorphic Granite Rock PBR Set (2048x2048)...")
    w, h = 2048, 2048
    np.random.seed(101)
    random.seed(101)

    # 1. Stratified Metamorphic Granite & Slate Base
    x = np.linspace(0, 18 * np.pi, w)
    y = np.linspace(0, 18 * np.pi, h)
    X, Y = np.meshgrid(x, y)

    # Shear angle ~ 25 degrees
    u = X * math.cos(0.4) + Y * math.sin(0.4)
    v = -X * math.sin(0.4) + Y * math.cos(0.4)

    strata = np.sin(u * 2.5) * 0.4 + np.sin(u * 7.0) * 0.25 + np.sin(u * 18.0) * 0.15
    fractures = np.cos(v * 3.2) * np.sin(u * 4.5) * 0.35
    noise = np.random.normal(0, 16, (h, w))

    rock_val = np.clip(125 + strata * 55 + fractures * 45 + noise, 45, 230).astype(np.uint8)
    
    # Color mapping: Slate grey to granite feldspar with dark fracture lines
    rock_rgb = np.zeros((h, w, 3), dtype=np.uint8)
    rock_rgb[:, :, 0] = np.clip(rock_val.astype(np.float32) * 1.05, 0, 255).astype(np.uint8)
    rock_rgb[:, :, 1] = np.clip(rock_val.astype(np.float32) * 1.02, 0, 255).astype(np.uint8)
    rock_rgb[:, :, 2] = np.clip(rock_val.astype(np.float32) * 0.98, 0, 255).astype(np.uint8)

    img = Image.fromarray(rock_rgb).filter(ImageFilter.GaussianBlur(1.0))
    draw = ImageDraw.Draw(img)

    # 2. Deep Cracks and Chiseled Cleavage Lines
    for _ in range(85):
        sx = random.randint(0, w - 1)
        sy = random.randint(0, h - 1)
        seg_len = random.randint(80, 450)
        angle = random.gauss(0.4, 0.3)
        pts = [(sx, sy)]
        curr_x, curr_y = sx, sy
        for _ in range(seg_len // 25):
            curr_x += int(25 * math.cos(angle) + random.randint(-8, 8))
            curr_y += int(25 * math.sin(angle) + random.randint(-8, 8))
            pts.append((curr_x, curr_y))
        draw.line(pts, fill=(35, 38, 42), width=random.randint(2, 5))

    # 3. Quartz Veins (bright white/cream streaks)
    for _ in range(18):
        sx = random.randint(0, w - 1)
        sy = random.randint(0, h - 1)
        pts = [(sx, sy)]
        curr_x, curr_y = sx, sy
        for _ in range(random.randint(6, 18)):
            curr_x += int(40 * math.cos(0.4) + random.randint(-15, 15))
            curr_y += int(40 * math.sin(0.4) + random.randint(-15, 15))
            pts.append((curr_x, curr_y))
        draw.line(pts, fill=(225, 228, 232), width=random.randint(2, 6))

    # 4. Pale Green Alpine Lichen & Dark Moss Patches
    for _ in range(350):
        lx = random.randint(0, w - 1)
        ly = random.randint(0, h - 1)
        lr = random.randint(15, 55)
        l_col = (random.randint(145, 175), random.randint(165, 195), random.randint(130, 160))
        draw.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=l_col)

    albedo_path = os.path.join(TEX_DIR, 'mountain_rock_cliff.png')
    albedo_pbr = os.path.join(TEX_DIR, 'mountain_rock_cliff_albedo.png')
    img.save(albedo_path, quality=95)
    img.save(albedo_pbr, quality=95)
    print(f"  -> Saved Granite Rock Albedo: {albedo_path}")

    # Normal Map with high rock relief
    gray_img = img.convert('L').filter(ImageFilter.GaussianBlur(1.0))
    normal_img = sobel_normal_map(gray_img, strength=4.5)
    normal_path = os.path.join(TEX_DIR, 'mountain_rock_cliff_normal.png')
    normal_img.save(normal_path, quality=95)
    print(f"  -> Saved Granite Rock Normal: {normal_path}")

    # Roughness Map
    gray_arr = np.array(gray_img, dtype=np.float32)
    rough_arr = np.clip(180 + np.random.normal(0, 15, (h, w)), 140, 245).astype(np.uint8)
    rough_img = Image.fromarray(rough_arr, mode='L')
    rough_path = os.path.join(TEX_DIR, 'mountain_rock_cliff_roughness.png')
    rough_img.save(rough_path, quality=95)
    print(f"  -> Saved Granite Rock Roughness: {rough_path}")


def generate_pine_foliage_and_bark():
    print("🌲 Generating Authentic Himalayan Pine Foliage & Bark PBR Set (1024x1024)...")
    w, h = 1024, 1024
    random.seed(88)

    # --- Foliage Bough (RGBA) ---
    foliage = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(foliage)

    # Central Woody Stem
    stem_pts = [(512, 1000)]
    cx = 512
    for sy in range(950, 120, -50):
        cx += random.randint(-12, 12)
        stem_pts.append((cx, sy))
    draw.line(stem_pts, fill=(68, 48, 35, 255), width=18)

    # Radiating secondary twigs
    twigs = []
    for idx, (tx, ty) in enumerate(stem_pts[1:-2]):
        for side in [-1, 1]:
            t_angle = side * random.uniform(0.65, 1.25)
            t_len = random.randint(180, 360) * (1.0 - idx / len(stem_pts))
            ex = int(tx + t_len * math.sin(t_angle))
            ey = int(ty - t_len * math.cos(t_angle) * 0.45)
            draw.line([(tx, ty), (ex, ey)], fill=(75, 52, 38, 255), width=8)
            twigs.append(((tx, ty), (ex, ey)))

    # Thousands of Pine Needles (radiating needle sprays)
    needle_cols = [
        (26, 68, 32, 245), (35, 85, 40, 250), (45, 105, 48, 250),
        (55, 125, 58, 240), (22, 55, 26, 255), (65, 140, 68, 230)
    ]
    for origin, end in twigs + [(p, (p[0] + random.randint(-40, 40), p[1] - 80)) for p in stem_pts]:
        for t in np.linspace(0.1, 1.0, 35):
            nx_orig = int(origin[0] * (1 - t) + end[0] * t)
            ny_orig = int(origin[1] * (1 - t) + end[1] * t)
            for _ in range(8):
                n_len = random.randint(35, 75)
                n_ang = random.uniform(0, 2 * math.pi)
                nx_end = int(nx_orig + n_len * math.cos(n_ang))
                ny_end = int(ny_orig + n_len * math.sin(n_ang))
                col = random.choice(needle_cols)
                draw.line([(nx_orig, ny_orig), (nx_end, ny_end)], fill=col, width=2)

    fol_path = os.path.join(TEX_DIR, 'alpine_pine_foliage.png')
    foliage.save(fol_path, quality=95)
    print(f"  -> Saved Pine Foliage: {fol_path}")

    # Normal map for foliage
    alpha_mask = foliage.split()[3]
    gray_fol = foliage.convert('L')
    norm_fol = sobel_normal_map(gray_fol, strength=2.2)
    norm_fol_rgba = Image.merge("RGBA", norm_fol.split() + (alpha_mask,))
    norm_fol_rgba.save(os.path.join(TEX_DIR, 'alpine_pine_foliage_normal.png'), quality=95)

    # --- Bark Texture ---
    bark = Image.new("RGB", (w, h), (55, 42, 35))
    bdraw = ImageDraw.Draw(bark)
    for bx in range(0, w, 18):
        col_val = random.randint(40, 75)
        bdraw.rectangle([(bx, 0), (bx + 14, h)], fill=(col_val, int(col_val * 0.75), int(col_val * 0.6)))
        # Vertical fissures
        for fy in range(0, h, random.randint(40, 120)):
            bdraw.line([(bx, fy), (bx + 14, fy + random.randint(-15, 15))], fill=(25, 18, 14), width=3)
    bark = bark.filter(ImageFilter.GaussianBlur(1.2))
    bark_path = os.path.join(TEX_DIR, 'alpine_pine_bark.png')
    bark.save(bark_path, quality=95)
    
    gray_bark = bark.convert('L')
    norm_bark = sobel_normal_map(gray_bark, strength=4.0)
    norm_bark.save(os.path.join(TEX_DIR, 'alpine_pine_bark_normal.png'), quality=95)
    print(f"  -> Saved Pine Bark: {bark_path}")


def generate_photorealistic_wildflowers():
    print("🌸 Generating Photorealistic Alpine Wildflower & Shrub Textures (1024x1024 RGBA)...")
    w, h = 1024, 1024

    # 1. Himalayan Blue Poppy (Meconopsis betonicifolia)
    poppy = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(poppy)
    random.seed(99)

    # Slender hairy stems
    stem_x = 512
    draw.line([(stem_x, 1000), (512, 350)], fill=(45, 115, 48, 255), width=14)
    # Leaves along stem
    for ly in [800, 650, 500]:
        for s in [-1, 1]:
            draw.polygon([
                (stem_x, ly),
                (stem_x + s * 140, ly - 45),
                (stem_x + s * 190, ly - 70),
                (stem_x + s * 110, ly - 100),
                (stem_x, ly - 50)
            ], fill=(52, 128, 55, 245))

    # Large Sky-Blue / Cobalt Poppy Petals (4 overlapping ruffled petals)
    cx, cy = 512, 280
    petal_offsets = [
        (-120, -50, 0.9), (120, -50, 0.9), (-90, 80, 1.1), (90, 80, 1.1)
    ]
    for px, py, scale in petal_offsets:
        rad_x = int(140 * scale)
        rad_y = int(120 * scale)
        # Petal gradient: cobalt base to brilliant cyan/azure tip
        for r_step in range(rad_x, 10, -8):
            ratio = r_step / rad_x
            r_col = int(25 * (1 - ratio) + 65 * ratio)
            g_col = int(95 * (1 - ratio) + 185 * ratio)
            b_col = int(195 * (1 - ratio) + 245 * ratio)
            draw.ellipse([
                (cx + px) - r_step, (cy + py) - int(r_step * (rad_y / rad_x)),
                (cx + px) + r_step, (cy + py) + int(r_step * (rad_y / rad_x))
            ], fill=(r_col, g_col, b_col, 240))

    # Center Boss: Golden Yellow Stamens & Green Pistil
    draw.ellipse([cx - 35, cy - 35, cx + 35, cy + 35], fill=(55, 135, 50, 255))
    for ang in np.linspace(0, 2 * math.pi, 36):
        sx = int(cx + 42 * math.cos(ang))
        sy = int(cy + 42 * math.sin(ang))
        draw.line([(cx, cy), (sx, sy)], fill=(245, 205, 45, 255), width=3)
        draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 225, 60, 255))

    poppy.save(os.path.join(TEX_DIR, 'alpine_wildflower_poppy.png'), quality=95)
    print("  -> Saved Himalayan Blue Poppy")

    # 2. Alpine Buttercup (Ranunculus)
    buttercup = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(buttercup)
    # Stems
    bdraw.line([(512, 1000), (512, 340)], fill=(42, 110, 40, 255), width=12)
    bdraw.line([(512, 600), (320, 420)], fill=(42, 110, 40, 255), width=10)
    bdraw.line([(512, 520), (700, 390)], fill=(42, 110, 40, 255), width=10)

    # 3 Golden Yellow Blossoms
    flower_locs = [(512, 320, 1.0), (310, 400, 0.75), (710, 370, 0.8)]
    for fcx, fcy, fscale in flower_locs:
        # 5 Cupped Golden Petals
        for p_i in range(5):
            p_ang = p_i * (2 * math.pi / 5) - math.pi / 2
            pet_cx = int(fcx + 55 * fscale * math.cos(p_ang))
            pet_cy = int(fcy + 55 * fscale * math.sin(p_ang))
            prad = int(60 * fscale)
            bdraw.ellipse([pet_cx - prad, pet_cy - prad, pet_cx + prad, pet_cy + prad],
                          fill=(255, 215, 30, 245), outline=(235, 185, 20, 255), width=2)
        # Flower center
        bdraw.ellipse([fcx - int(24 * fscale), fcy - int(24 * fscale),
                       fcx + int(24 * fscale), fcy + int(24 * fscale)],
                      fill=(180, 150, 20, 255))
    buttercup.save(os.path.join(TEX_DIR, 'alpine_wildflower_buttercup.png'), quality=95)
    print("  -> Saved Alpine Buttercup")

    # 3. Alpine Mountain Daisy / Chamomile (Asteraceae)
    daisy = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ddraw = ImageDraw.Draw(daisy)
    ddraw.line([(512, 1000), (512, 320)], fill=(40, 105, 38, 255), width=12)
    # Radiating white ray petals
    dcx, dcy = 512, 300
    for r_ang in np.linspace(0, 2 * math.pi, 28):
        rx_tip = int(dcx + 130 * math.cos(r_ang))
        ry_tip = int(dcy + 130 * math.sin(r_ang))
        ddraw.line([(dcx, dcy), (rx_tip, ry_tip)], fill=(248, 248, 252, 245), width=14)
    # Golden Orange Disc
    ddraw.ellipse([dcx - 45, dcy - 45, dcx + 45, dcy + 45], fill=(245, 160, 20, 255))
    for _ in range(80):
        fx = random.randint(dcx - 38, dcx + 38)
        fy = random.randint(dcy - 38, dcy + 38)
        if (fx - dcx)**2 + (fy - dcy)**2 < 38**2:
            ddraw.point((fx, fy), fill=(255, 200, 30, 255))
    daisy.save(os.path.join(TEX_DIR, 'alpine_wildflower_daisy.png'), quality=95)
    print("  -> Saved Mountain Daisy")

    # 4. Alpine Purple Gentian / Aster
    gentian = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(gentian)
    gdraw.line([(512, 1000), (512, 330)], fill=(45, 110, 42, 255), width=12)
    gcx, gcy = 512, 310
    # Deep royal purple / violet petals
    for gang in np.linspace(0, 2 * math.pi, 24):
        gx_tip = int(gcx + 125 * math.cos(gang))
        gy_tip = int(gcy + 125 * math.sin(gang))
        gdraw.line([(gcx, gcy), (gx_tip, gy_tip)], fill=(120, 50, 185, 245), width=15)
    gdraw.ellipse([gcx - 35, gcy - 35, gcx + 35, gcy + 35], fill=(235, 175, 30, 255))
    gentian.save(os.path.join(TEX_DIR, 'alpine_wildflower_gentian.png'), quality=95)
    print("  -> Saved Alpine Purple Gentian")

    # 5. Alpine Dwarf Rhododendron / Mountain Bush (Dense evergreen foliage + pink blooms)
    shrub = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shrub)
    # Dense dome of small oval leathery leaves
    for _ in range(1200):
        lx = random.randint(150, 874)
        ly = random.randint(220, 950)
        # Only inside an elliptical dome
        if ((lx - 512) / 360)**2 + ((ly - 620) / 330)**2 <= 1.0:
            l_rad = random.randint(18, 38)
            leaf_col = (random.randint(25, 55), random.randint(75, 125), random.randint(30, 60), 245)
            sdraw.ellipse([lx - l_rad, ly - l_rad // 2, lx + l_rad, ly + l_rad // 2], fill=leaf_col)
    # Bright pink alpine blooms scattered across shrub
    for _ in range(85):
        bx = random.randint(180, 844)
        by = random.randint(240, 800)
        if ((bx - 512) / 340)**2 + ((by - 600) / 300)**2 <= 0.9:
            brad = random.randint(15, 28)
            sdraw.ellipse([bx - brad, by - brad, bx + brad, by + brad],
                          fill=(230, 85, 145, 250), outline=(255, 140, 185, 255))
    shrub.save(os.path.join(TEX_DIR, 'alpine_dwarf_rhododendron.png'), quality=95)
    print("  -> Saved Alpine Dwarf Rhododendron")


if __name__ == '__main__':
    generate_grass_meadow_pbr()
    generate_granite_cliff_pbr()
    generate_pine_foliage_and_bark()
    generate_photorealistic_wildflowers()
    print("✨ ALL PHOTOREALISTIC PBR TEXTURES GENERATED SUCCESSFULLY!")
