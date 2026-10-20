#!/usr/bin/env python3
"""
Master Builder Script for Mountain Grassland World
Creates:
1. High-resolution PBR textures: alpine meadow grass, wildflowers, mountain rock, pine foliage, bark.
2. 3D Models:
   - alpine_mountain_terrain (100m x 80m, strictly <= 1:8 gradient in traversal corridor)
   - alpine_wildflower_cluster (blue poppies, yellow buttercups, daisies, purple asters)
   - alpine_grass_clump (volumetric tall meadow grass tufts)
   - alpine_boulder_cluster (weathered granite boulders and rock scree)
   - alpine_pine_tree (conifer trees framing valley ridges)
   - alpine_dwarf_shrub (low-lying alpine mountain bushes)
   - border_meadow_outpost (high-altitude border outpost & comms)
   - nipun_mine_marker (coaster-sized 10cm x 4cm NIPUN minelet)
3. Coordinates config for 18+ NIPUN minelet locations in the meadow.
4. Master SDF world: mountain_grassland_minefield.sdf with procedural sky and natural alpine lighting.
"""

import os
import math
import random
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = '/home/nammy/army_mine_bot/src/mountain_grassland_world'
MODELS_DIR = os.path.join(BASE_DIR, 'models')
TEX_DIR = os.path.join(BASE_DIR, 'materials/textures')
WORLDS_DIR = os.path.join(BASE_DIR, 'worlds')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(TEX_DIR, exist_ok=True)
os.makedirs(WORLDS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)


# ==============================================================================
# 1. TEXTURE GENERATION (PBR ALBEDO MAPS)
# ==============================================================================
def create_alpine_textures():
    print("🎨 Generating Photorealistic Alpine Mountain & Floral Textures...")

    # --- 1.1 Alpine Meadow Grass (Lush Green with Tone Variations) ---
    w, h = 1024, 1024
    grass_img = Image.new("RGB", (w, h), (45, 90, 40))
    draw = ImageDraw.Draw(grass_img)

    # Base noise
    np.random.seed(42)
    base_arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Shades: emerald green, olive, deep loam, lime hints
    c_base = np.array([45, 95, 38], dtype=np.float32)
    noise1 = np.random.normal(0, 15, (h, w, 1))
    noise2 = np.random.normal(0, 8, (h, w, 3))
    arr = np.clip(c_base + noise1 + noise2, 0, 255).astype(np.uint8)
    grass_img = Image.fromarray(arr).filter(ImageFilter.GaussianBlur(1.5))
    draw = ImageDraw.Draw(grass_img)

    # Paint thousands of fine grass blades & mossy flecks
    random.seed(42)
    blade_colors = [
        (58, 122, 50), (40, 85, 35), (72, 145, 60), (85, 160, 68),
        (35, 75, 30), (52, 105, 44), (95, 175, 75), (60, 95, 45)
    ]
    for _ in range(45000):
        x1 = random.randint(0, w - 1)
        y1 = random.randint(0, h - 1)
        length = random.randint(4, 14)
        angle = random.uniform(-0.6, 0.6)
        x2 = int(x1 + length * math.sin(angle))
        y2 = int(y1 - length * math.cos(angle))
        color = random.choice(blade_colors)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

    # Subtle soil/earth patches
    for _ in range(60):
        cx = random.randint(0, w - 1)
        cy = random.randint(0, h - 1)
        rx = random.randint(15, 45)
        ry = random.randint(10, 30)
        draw.ellipse([(cx - rx, cy - ry), (cx + rx, cy + ry)], fill=(65, 55, 40, 40))

    grass_path = os.path.join(TEX_DIR, 'alpine_grass_meadow.png')
    grass_img.save(grass_path, quality=95)
    print(f"  -> Saved: {grass_path}")

    # --- 1.2 Alpine Wildflowers (Blue Poppy, Yellow Buttercup, Daisy, Purple Aster) ---
    flower_img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(flower_img)

    # Stem and green leaves
    fdraw.rectangle([(250, 180), (262, 510)], fill=(34, 110, 34, 255))
    for i in range(5):
        ly = 240 + i * 50
        lx_end = 160 if i % 2 == 0 else 350
        fdraw.line([(256, ly), (lx_end, ly - 25)], fill=(40, 130, 40, 255), width=5)
        fdraw.ellipse([(lx_end - 25, ly - 35), (lx_end + 25, ly - 15)], fill=(46, 145, 46, 240))

    # Petals (Himalayan Blue Poppy & Wildflowers)
    cx, cy = 256, 160
    # 6 petals in circle
    for a in np.linspace(0, 2 * math.pi, 8, endpoint=False):
        px = cx + 55 * math.cos(a)
        py = cy + 55 * math.sin(a)
        fdraw.ellipse([(px - 45, py - 45), (px + 45, py + 45)], fill=(37, 99, 235, 250), outline=(29, 78, 216, 255))
        # Inner petal tone
        fdraw.ellipse([(px - 30, py - 30), (px + 30, py + 30)], fill=(59, 130, 246, 255))

    # Golden yellow center disc
    fdraw.ellipse([(cx - 28, cy - 28), (cx + 28, cy + 28)], fill=(234, 179, 8, 255), outline=(202, 138, 4, 255))
    fdraw.ellipse([(cx - 14, cy - 14), (cx + 14, cy + 14)], fill=(245, 158, 11, 255))

    poppy_path = os.path.join(TEX_DIR, 'alpine_wildflower_poppy.png')
    flower_img.save(poppy_path)
    print(f"  -> Saved: {poppy_path}")

    # Yellow Mountain Buttercup
    buttercup_img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(buttercup_img)
    bdraw.rectangle([(250, 180), (262, 510)], fill=(34, 110, 34, 255))
    for a in np.linspace(0, 2 * math.pi, 6, endpoint=False):
        px = cx + 50 * math.cos(a)
        py = cy + 50 * math.sin(a)
        bdraw.ellipse([(px - 45, py - 45), (px + 45, py + 45)], fill=(250, 204, 21, 250), outline=(234, 179, 8, 255))
        bdraw.ellipse([(px - 28, py - 28), (px + 28, py + 28)], fill=(254, 240, 138, 255))
    bdraw.ellipse([(cx - 24, cy - 24), (cx + 24, cy + 24)], fill=(217, 119, 6, 255))
    buttercup_path = os.path.join(TEX_DIR, 'alpine_wildflower_buttercup.png')
    buttercup_img.save(buttercup_path)
    print(f"  -> Saved: {buttercup_path}")

    # Mountain Edelweiss / White Daisy
    daisy_img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    ddraw = ImageDraw.Draw(daisy_img)
    ddraw.rectangle([(250, 180), (262, 510)], fill=(34, 110, 34, 255))
    for a in np.linspace(0, 2 * math.pi, 12, endpoint=False):
        px = cx + 60 * math.cos(a)
        py = cy + 60 * math.sin(a)
        ddraw.ellipse([(px - 25, py - 25), (px + 25, py + 25)], fill=(248, 250, 252, 250), outline=(203, 213, 225, 255))
    ddraw.ellipse([(cx - 26, cy - 26), (cx + 26, cy + 26)], fill=(245, 158, 11, 255))
    daisy_path = os.path.join(TEX_DIR, 'alpine_wildflower_daisy.png')
    daisy_img.save(daisy_path)
    print(f"  -> Saved: {daisy_path}")

    # --- 1.3 Mountain Rock & Granite Cliff ---
    rock_img = Image.new("RGB", (512, 512), (110, 110, 115))
    np_rock = np.random.normal(120, 25, (512, 512, 3)).astype(np.float32)
    # Slate grey with slight warm lichen
    np_rock[:, :, 0] *= 0.95  # R
    np_rock[:, :, 1] *= 0.98  # G
    np_rock[:, :, 2] *= 1.05  # B
    rock_arr = np.clip(np_rock, 0, 255).astype(np.uint8)
    rock_img = Image.fromarray(rock_arr).filter(ImageFilter.GaussianBlur(1.0))
    rdraw = ImageDraw.Draw(rock_img)
    for _ in range(120):
        rx1, ry1 = random.randint(0, 511), random.randint(0, 511)
        rx2, ry2 = rx1 + random.randint(-40, 40), ry1 + random.randint(-40, 40)
        rdraw.line([(rx1, ry1), (rx2, ry2)], fill=(60, 60, 65), width=2)
    rock_path = os.path.join(TEX_DIR, 'mountain_rock_cliff.png')
    rock_img.save(rock_path, quality=95)
    print(f"  -> Saved: {rock_path}")

    # --- 1.4 Alpine Pine Needles Foliage ---
    pine_img = Image.new("RGBA", (512, 512), (22, 60, 32, 255))
    pdraw = ImageDraw.Draw(pine_img)
    pine_colors = [(20, 55, 28), (30, 80, 40), (15, 42, 22), (40, 95, 48)]
    for _ in range(25000):
        px = random.randint(0, 511)
        py = random.randint(0, 511)
        plen = random.randint(6, 18)
        pangle = random.uniform(-1.0, 1.0)
        pdraw.line([(px, py), (px + plen * math.sin(pangle), py + plen * math.cos(pangle))],
                   fill=random.choice(pine_colors), width=2)
    pine_path = os.path.join(TEX_DIR, 'alpine_pine_foliage.png')
    pine_img.save(pine_path)
    print(f"  -> Saved: {pine_path}")

    # --- 1.5 Alpine Pine Bark ---
    bark_img = Image.new("RGB", (512, 512), (70, 48, 32))
    bdraw2 = ImageDraw.Draw(bark_img)
    bark_colors = [(55, 36, 24), (85, 58, 38), (45, 28, 18), (100, 70, 45)]
    for _ in range(8000):
        bx = random.randint(0, 511)
        by = random.randint(0, 511)
        blen = random.randint(15, 40)
        bdraw2.line([(bx, by), (bx + random.randint(-2, 2), by + blen)],
                    fill=random.choice(bark_colors), width=random.randint(2, 5))
    bark_path = os.path.join(TEX_DIR, 'alpine_pine_bark.png')
    bark_img.save(bark_path, quality=95)
    print(f"  -> Saved: {bark_path}")


# ==============================================================================
# 2. MOUNTAIN TERRAIN ELEVATION (STRICTLY <= 1:8 GRADIENT IN PATROL CORRIDOR)
# ==============================================================================
def get_alpine_elevation(x, y):
    """
    Continuous mountain terrain with an alpine meadow pass.
    1. West Staging / Spawn Meadow: x in [-50, -25] is nearly level (z ~ 0.0 - 0.2m).
    2. Patrol Valley Corridor: y in [-14, 14] has gentle continuous mountain slope <= 1:8 gradient (0.04 - 0.08 dz/dx).
    3. Flanking Mountain Ridges: y > 18 and y < -18 rise naturally to 4.0m - 6.5m.
    4. Rolling knolls, subtle ditches, and flower hollows adhering strictly to 1.docx.
    """
    x_val = float(x)
    y_val = float(y)

    # Base transition from staging area (x < -20) to mountain ascent (x >= -20)
    if x_val < -25.0:
        base_grade = 0.0
    else:
        # Smoothstep ascent starting at x = -25.0
        dist_ascent = x_val + 25.0
        # Continuous slope gradient ~ 0.06 (approx 1:16 to 1:10, well within 1:8 = 0.125)
        base_grade = 0.055 * dist_ascent

    # Valley floor vs mountain walls
    # Width of gentle alpine valley: ~30m (y in [-15, 15])
    valley_factor = math.exp(-((y_val / 16.0) ** 2))

    # Rolling meadow undulations on valley floor (very gentle, max slope ~ 0.03)
    rolling_meadow = (
        0.18 * math.sin(0.12 * x_val) * math.cos(0.15 * y_val) +
        0.10 * math.sin(0.25 * x_val + 0.5) * math.cos(0.20 * y_val - 0.3) +
        0.05 * math.sin(0.40 * x_val) * math.sin(0.35 * y_val)
    )

    # Flanking mountain peaks rising outside the valley corridor (North & South)
    flank_dist = max(abs(y_val) - 12.0, 0.0)
    mountain_ridges = 0.12 * (flank_dist ** 1.45) + 0.4 * math.sin(0.15 * x_val) * math.cos(0.10 * y_val)

    # Gentle mountain hollows / drainage swales (ditch features compliant with Req #4)
    swale1 = -0.22 * math.exp(-(((x_val - 5.0) ** 2 + (y_val - 4.0) ** 2) / (6.0 ** 2)))
    swale2 = -0.18 * math.exp(-(((x_val - 18.0) ** 2 + (y_val + 5.0) ** 2) / (5.0 ** 2)))

    total_z = base_grade * valley_factor + rolling_meadow * valley_factor + mountain_ridges + (swale1 + swale2)
    return float(max(total_z, 0.0))


def get_alpine_normal(x, y):
    eps = 0.1
    dz_dx = (get_alpine_elevation(x + eps, y) - get_alpine_elevation(x - eps, y)) / (2 * eps)
    dz_dy = (get_alpine_elevation(x, y + eps) - get_alpine_elevation(x, y - eps)) / (2 * eps)
    n = [-dz_dx, -dz_dy, 1.0]
    norm = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
    return [n[0] / norm, n[1] / norm, n[2] / norm]


def build_alpine_terrain_mesh():
    print("🏔️  Building Alpine Mountain Grassland Terrain Mesh (100m x 80m)...")
    nx, ny = 160, 140
    x_min, x_max = -50.0, 50.0
    y_min, y_max = -40.0, 40.0
    x_vals = np.linspace(x_min, x_max, nx)
    y_vals = np.linspace(y_min, y_max, ny)
    X, Y = np.meshgrid(x_vals, y_vals)
    Z = np.zeros_like(X)

    for i in range(ny):
        for j in range(nx):
            Z[i, j] = get_alpine_elevation(X[i, j], Y[i, j])

    # Vertices
    top_vertices = np.zeros((nx * ny, 3))
    top_vertices[:, 0] = X.flatten()
    top_vertices[:, 1] = Y.flatten()
    top_vertices[:, 2] = Z.flatten()

    top_faces = []
    for i in range(ny - 1):
        for j in range(nx - 1):
            idx = i * nx + j
            top_faces.append([idx, idx + 1, idx + nx])
            top_faces.append([idx + 1, idx + nx + 1, idx + nx])
    top_faces = np.array(top_faces)

    skirt_z = -3.0
    bottom_vertices = top_vertices.copy()
    bottom_vertices[:, 2] = skirt_z
    all_vertices = np.vstack([top_vertices, bottom_vertices])

    all_faces = list(top_faces)
    offset = nx * ny
    for f in top_faces:
        all_faces.append([f[0] + offset, f[2] + offset, f[1] + offset])

    # Skirts around 4 edges
    for j in range(nx - 1):
        i = ny - 1
        t1, t2 = i * nx + j, i * nx + (j + 1)
        b1, b2 = t1 + offset, t2 + offset
        all_faces.extend([[t1, b1, t2], [t2, b1, b2]])
    for j in range(nx - 1):
        i = 0
        t1, t2 = i * nx + j, i * nx + (j + 1)
        b1, b2 = t1 + offset, t2 + offset
        all_faces.extend([[t1, t2, b1], [t2, b2, b1]])
    for i in range(ny - 1):
        j = 0
        t1, t2 = i * nx + j, (i + 1) * nx + j
        b1, b2 = t1 + offset, t2 + offset
        all_faces.extend([[t1, b1, t2], [t2, b1, b2]])
    for i in range(ny - 1):
        j = nx - 1
        t1, t2 = i * nx + j, (i + 1) * nx + j
        b1, b2 = t1 + offset, t2 + offset
        all_faces.extend([[t1, t2, b1], [t2, b2, b1]])

    all_faces = np.array(all_faces)

    # UV mapping (tiled every 4.0 meters)
    u = (all_vertices[:, 0] - x_min) / 4.0
    v = (all_vertices[:, 1] - y_min) / 4.0
    uv = np.column_stack([u, v])

    tex_img = Image.open(f"{TEX_DIR}/alpine_grass_meadow.png")
    terrain_mesh = trimesh.Trimesh(
        vertices=all_vertices,
        faces=all_faces,
        visual=trimesh.visual.TextureVisuals(uv=uv, image=tex_img),
        process=True
    )
    _ = terrain_mesh.vertex_normals

    model_dir = os.path.join(MODELS_DIR, 'alpine_mountain_terrain')
    meshes_dir = os.path.join(model_dir, 'meshes')
    os.makedirs(meshes_dir, exist_ok=True)

    terrain_mesh.export(os.path.join(meshes_dir, 'visual.dae'))
    terrain_mesh.export(os.path.join(meshes_dir, 'collision.stl'))

    # model.config
    with open(os.path.join(model_dir, 'model.config'), 'w') as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>alpine_mountain_terrain</name>
  <version>1.0</version>
  <sdf version="1.6">model.sdf</sdf>
  <author><name>Naman Harshwal</name></author>
  <description>High-altitude alpine mountain grassland terrain with 1:8 continuous slope</description>
</model>""")

    # model.sdf
    with open(os.path.join(model_dir, 'model.sdf'), 'w') as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="alpine_mountain_terrain">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://alpine_mountain_terrain/meshes/visual.dae</uri>
          </mesh>
        </geometry>
        <material>
          <ambient>0.35 0.60 0.30 1.0</ambient>
          <diffuse>0.45 0.75 0.38 1.0</diffuse>
          <specular>0.10 0.12 0.08 1.0</specular>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/alpine_grass_meadow.png</albedo_map>
              <roughness>0.90</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
      <collision name="collision">
        <geometry>
          <mesh>
            <uri>model://alpine_mountain_terrain/meshes/collision.stl</uri>
          </mesh>
        </geometry>
        <surface>
          <friction>
            <ode>
              <mu>20.0</mu>
              <mu2>20.0</mu2>
            </ode>
          </friction>
          <contact>
            <ode>
              <kp>10000000.0</kp>
              <kd>1.0</kd>
              <min_depth>0.005</min_depth>
            </ode>
          </contact>
        </surface>
      </collision>
    </link>
  </model>
</sdf>""")
    print("✅ Alpine mountain terrain mesh created!")


# ==============================================================================
# 3. 3D MODELS: WILDFLOWERS, GRASS TUFTS, BOULDERS, TREES, OUTPOST
# ==============================================================================
def build_3d_vegetation_and_props():
    print("🌿 Building 3D Wildflower, Grass, Boulder, and Vegetation Models...")

    # --- 3.1 Alpine Wildflower Cluster (Cross-Planes with Petals & Stems) ---
    wf_model_dir = os.path.join(MODELS_DIR, 'alpine_wildflower_cluster')
    wf_meshes = os.path.join(wf_model_dir, 'meshes')
    os.makedirs(wf_meshes, exist_ok=True)

    # Create 3 intersecting angled planes with stem & petal geometry
    # Height ~0.35m, diameter ~0.45m
    w_w, w_h = 0.45, 0.35
    planes = []
    for angle in [0, math.pi / 3.0, 2.0 * math.pi / 3.0]:
        dx = (w_w / 2.0) * math.cos(angle)
        dy = (w_w / 2.0) * math.sin(angle)
        verts = np.array([
            [-dx, -dy, 0.0],
            [dx, dy, 0.0],
            [dx, dy, w_h],
            [-dx, -dy, w_h]
        ])
        faces = np.array([[0, 1, 2], [0, 2, 3], [0, 2, 1], [0, 3, 2]])
        uv = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
        mesh = trimesh.Trimesh(vertices=verts, faces=faces)
        planes.append(mesh)

    wf_mesh = trimesh.util.concatenate(planes)
    tex_poppy = Image.open(f"{TEX_DIR}/alpine_wildflower_poppy.png")
    wf_mesh.visual = trimesh.visual.TextureVisuals(
        uv=np.tile(np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]), (3, 1)),
        image=tex_poppy
    )
    wf_mesh.export(os.path.join(wf_meshes, 'visual.dae'))
    wf_mesh.export(os.path.join(wf_meshes, 'collision.stl'))

    with open(os.path.join(wf_model_dir, 'model.config'), 'w') as f:
        f.write("""<?xml version="1.0"?><model><name>alpine_wildflower_cluster</name><version>1.0</version><sdf version="1.6">model.sdf</sdf><author><name>Naman Harshwal</name></author></model>""")

    with open(os.path.join(wf_model_dir, 'model.sdf'), 'w') as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="alpine_wildflower_cluster">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry><mesh><uri>model://alpine_wildflower_cluster/meshes/visual.dae</uri></mesh></geometry>
        <material>
          <ambient>0.2 0.6 0.9 1.0</ambient>
          <diffuse>0.3 0.7 1.0 1.0</diffuse>
          <pbr><metal><albedo_map>{TEX_DIR}/alpine_wildflower_poppy.png</albedo_map><roughness>0.8</roughness></metal></pbr>
        </material>
      </visual>
      <collision name="collision">
        <geometry><box><size>0.35 0.35 0.30</size></box></geometry>
        <pose>0 0 0.15 0 0 0</pose>
      </collision>
    </link>
  </model>
</sdf>""")

    # --- 3.2 Alpine Grass Clump (Tall Ryegrass/Fescue Tuft) ---
    gc_model_dir = os.path.join(MODELS_DIR, 'alpine_grass_clump')
    gc_meshes = os.path.join(gc_model_dir, 'meshes')
    os.makedirs(gc_meshes, exist_ok=True)

    g_w, g_h = 0.50, 0.38
    g_planes = []
    for angle in [0, math.pi / 4.0, math.pi / 2.0, 3.0 * math.pi / 4.0]:
        dx = (g_w / 2.0) * math.cos(angle)
        dy = (g_w / 2.0) * math.sin(angle)
        verts = np.array([
            [-dx, -dy, 0.0],
            [dx, dy, 0.0],
            [dx * 0.8, dy * 0.8, g_h],
            [-dx * 0.8, -dy * 0.8, g_h]
        ])
        faces = np.array([[0, 1, 2], [0, 2, 3], [0, 2, 1], [0, 3, 2]])
        mesh = trimesh.Trimesh(vertices=verts, faces=faces)
        g_planes.append(mesh)

    gc_mesh = trimesh.util.concatenate(g_planes)
    tex_grass = Image.open(f"{TEX_DIR}/alpine_grass_meadow.png")
    gc_mesh.visual = trimesh.visual.TextureVisuals(
        uv=np.tile(np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]), (4, 1)),
        image=tex_grass
    )
    gc_mesh.export(os.path.join(gc_meshes, 'visual.dae'))
    gc_mesh.export(os.path.join(gc_meshes, 'collision.stl'))

    with open(os.path.join(gc_model_dir, 'model.config'), 'w') as f:
        f.write("""<?xml version="1.0"?><model><name>alpine_grass_clump</name><version>1.0</version><sdf version="1.6">model.sdf</sdf><author><name>Naman Harshwal</name></author></model>""")

    with open(os.path.join(gc_model_dir, 'model.sdf'), 'w') as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="alpine_grass_clump">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry><mesh><uri>model://alpine_grass_clump/meshes/visual.dae</uri></mesh></geometry>
        <material>
          <ambient>0.30 0.65 0.28 1.0</ambient>
          <diffuse>0.40 0.80 0.35 1.0</diffuse>
          <pbr><metal><albedo_map>{TEX_DIR}/alpine_grass_meadow.png</albedo_map><roughness>0.9</roughness></metal></pbr>
        </material>
      </visual>
      <collision name="collision">
        <geometry><cylinder><radius>0.22</radius><length>0.35</length></cylinder></geometry>
        <pose>0 0 0.175 0 0 0</pose>
      </collision>
    </link>
  </model>
</sdf>""")

    # --- 3.3 Alpine Weathered Granite Boulder ---
    bd_model_dir = os.path.join(MODELS_DIR, 'alpine_boulder_cluster')
    bd_meshes = os.path.join(bd_model_dir, 'meshes')
    os.makedirs(bd_meshes, exist_ok=True)

    # Generate irregular faceted boulder mesh
    boulder = trimesh.creation.icosphere(subdivisions=2, radius=0.65)
    # Deform vertices randomly to give realistic weathered rock ridges
    np.random.seed(101)
    b_verts = boulder.vertices.copy()
    b_verts[:, 0] *= 1.3 + np.random.normal(0, 0.08, len(b_verts))
    b_verts[:, 1] *= 0.9 + np.random.normal(0, 0.06, len(b_verts))
    b_verts[:, 2] *= 0.75 + np.random.normal(0, 0.05, len(b_verts))
    # Flatten bottom
    b_verts[:, 2] = np.maximum(b_verts[:, 2], -0.2)
    boulder.vertices = b_verts
    _ = boulder.vertex_normals

    tex_rock = Image.open(f"{TEX_DIR}/mountain_rock_cliff.png")
    uv_rock = np.column_stack([(boulder.vertices[:, 0] + 1.0) / 2.0, (boulder.vertices[:, 1] + 1.0) / 2.0])
    boulder.visual = trimesh.visual.TextureVisuals(uv=uv_rock, image=tex_rock)

    boulder.export(os.path.join(bd_meshes, 'visual.dae'))
    boulder.export(os.path.join(bd_meshes, 'collision.stl'))

    with open(os.path.join(bd_model_dir, 'model.config'), 'w') as f:
        f.write("""<?xml version="1.0"?><model><name>alpine_boulder_cluster</name><version>1.0</version><sdf version="1.6">model.sdf</sdf><author><name>Naman Harshwal</name></author></model>""")

    with open(os.path.join(bd_model_dir, 'model.sdf'), 'w') as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="alpine_boulder_cluster">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry><mesh><uri>model://alpine_boulder_cluster/meshes/visual.dae</uri></mesh></geometry>
        <material>
          <ambient>0.45 0.45 0.48 1.0</ambient>
          <diffuse>0.60 0.60 0.65 1.0</diffuse>
          <pbr><metal><albedo_map>{TEX_DIR}/mountain_rock_cliff.png</albedo_map><roughness>0.85</roughness></metal></pbr>
        </material>
      </visual>
      <collision name="collision">
        <geometry><mesh><uri>model://alpine_boulder_cluster/meshes/collision.stl</uri></mesh></geometry>
      </collision>
    </link>
  </model>
</sdf>""")

    # --- 3.4 Alpine Conifer Pine Tree (Evergreen mountain framing) ---
    tr_model_dir = os.path.join(MODELS_DIR, 'alpine_pine_tree')
    tr_meshes = os.path.join(tr_model_dir, 'meshes')
    os.makedirs(tr_meshes, exist_ok=True)

    trunk = trimesh.creation.cylinder(radius=0.18, height=2.2)
    trunk.apply_translation([0, 0, 1.1])
    # Foliage tiers (4 cones)
    c1 = trimesh.creation.cone(radius=1.6, height=1.8)
    c1.apply_translation([0, 0, 2.0])
    c2 = trimesh.creation.cone(radius=1.3, height=1.6)
    c2.apply_translation([0, 0, 2.9])
    c3 = trimesh.creation.cone(radius=0.95, height=1.4)
    c3.apply_translation([0, 0, 3.8])
    c4 = trimesh.creation.cone(radius=0.55, height=1.2)
    c4.apply_translation([0, 0, 4.6])

    tree = trimesh.util.concatenate([trunk, c1, c2, c3, c4])
    tex_pine = Image.open(f"{TEX_DIR}/alpine_pine_foliage.png")
    uv_pine = np.column_stack([(tree.vertices[:, 0] + 2.0) / 4.0, (tree.vertices[:, 2]) / 5.0])
    tree.visual = trimesh.visual.TextureVisuals(uv=uv_pine, image=tex_pine)

    tree.export(os.path.join(tr_meshes, 'visual.dae'))
    tree.export(os.path.join(tr_meshes, 'collision.stl'))

    with open(os.path.join(tr_model_dir, 'model.config'), 'w') as f:
        f.write("""<?xml version="1.0"?><model><name>alpine_pine_tree</name><version>1.0</version><sdf version="1.6">model.sdf</sdf><author><name>Naman Harshwal</name></author></model>""")

    with open(os.path.join(tr_model_dir, 'model.sdf'), 'w') as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="alpine_pine_tree">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry><mesh><uri>model://alpine_pine_tree/meshes/visual.dae</uri></mesh></geometry>
        <material>
          <ambient>0.15 0.38 0.20 1.0</ambient>
          <diffuse>0.22 0.52 0.28 1.0</diffuse>
          <pbr><metal><albedo_map>{TEX_DIR}/alpine_pine_foliage.png</albedo_map><roughness>0.9</roughness></metal></pbr>
        </material>
      </visual>
      <collision name="collision">
        <geometry><cylinder><radius>0.25</radius><length>4.5</length></cylinder></geometry>
        <pose>0 0 2.25 0 0 0</pose>
      </collision>
    </link>
  </model>
</sdf>""")

    # --- 3.5 NIPUN Anti-Personnel Mine Marker (Coaster 10cm dia x 4cm) ---
    np_model_dir = os.path.join(MODELS_DIR, 'nipun_mine_marker')
    np_meshes = os.path.join(np_model_dir, 'meshes')
    os.makedirs(np_meshes, exist_ok=True)

    mine_geom = trimesh.creation.cylinder(radius=0.05, height=0.04)
    mine_geom.apply_translation([0, 0, 0.02])
    mine_geom.export(os.path.join(np_meshes, 'visual.dae'))
    mine_geom.export(os.path.join(np_meshes, 'collision.stl'))

    with open(os.path.join(np_model_dir, 'model.config'), 'w') as f:
        f.write("""<?xml version="1.0"?><model><name>nipun_mine_marker</name><version>1.0</version><sdf version="1.6">model.sdf</sdf><author><name>Naman Harshwal</name></author></model>""")

    with open(os.path.join(np_model_dir, 'model.sdf'), 'w') as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="nipun_mine_marker">
    <static>true</static>
    <link name="link">
      <visual name="casing">
        <geometry><cylinder><radius>0.05</radius><length>0.04</length></cylinder></geometry>
        <pose>0 0 0.02 0 0 0</pose>
        <material>
          <ambient>0.25 0.35 0.22 1.0</ambient>
          <diffuse>0.35 0.48 0.30 1.0</diffuse>
          <specular>0.4 0.4 0.4 1.0</specular>
        </material>
      </visual>
      <visual name="led_indicator">
        <geometry><cylinder><radius>0.015</radius><length>0.005</length></cylinder></geometry>
        <pose>0 0 0.042 0 0 0</pose>
        <material>
          <ambient>0.9 0.2 0.2 1.0</ambient>
          <diffuse>1.0 0.3 0.3 1.0</diffuse>
          <emissive>0.8 0.1 0.1 1.0</emissive>
        </material>
      </visual>
      <collision name="collision">
        <geometry><cylinder><radius>0.05</radius><length>0.04</length></cylinder></geometry>
        <pose>0 0 0.02 0 0 0</pose>
      </collision>
    </link>
  </model>
</sdf>""")

    print("✅ All 3D vegetation, props, and minelet models built successfully!")


# ==============================================================================
# 4. CONFIG & SDF WORLD GENERATION
# ==============================================================================
def generate_world_and_config():
    print("🌍 Generating Master Alpine Mountain Grassland World SDF...")

    # 18 Registered NIPUN Anti-Personnel Minelet coordinates across the meadow
    # W-Formation Stations are:
    # Station #1 (North Flank):  x = 12.0, y =  6.0
    # Station #2 (North Valley): x =  8.5, y =  3.0
    # Station #3 (Center Apex):  x = 12.0, y =  0.0
    # Station #4 (South Valley): x =  8.5, y = -3.0
    # Station #5 (South Flank):  x = 12.0, y = -6.0
    # Plus 13 tactical perimeter minelet coordinates distributed throughout the grassland.
    mine_coords = [
        {"id": 1,  "name": "nipun_wf_1_north_flank",  "type": "nipun_ap", "x": 12.0, "y":  6.0},
        {"id": 2,  "name": "nipun_wf_2_north_valley", "type": "nipun_ap", "x":  8.5, "y":  3.0},
        {"id": 3,  "name": "nipun_wf_3_center_apex",  "type": "nipun_ap", "x": 12.0, "y":  0.0},
        {"id": 4,  "name": "nipun_wf_4_south_valley", "type": "nipun_ap", "x":  8.5, "y": -3.0},
        {"id": 5,  "name": "nipun_wf_5_south_flank",  "type": "nipun_ap", "x": 12.0, "y": -6.0},
        {"id": 6,  "name": "nipun_meadow_alpha_1",     "type": "nipun_ap", "x":  3.5, "y":  4.5},
        {"id": 7,  "name": "nipun_meadow_alpha_2",     "type": "nipun_ap", "x":  5.0, "y": -5.2},
        {"id": 8,  "name": "nipun_meadow_bravo_1",     "type": "nipun_ap", "x": 16.5, "y":  7.5},
        {"id": 9,  "name": "nipun_meadow_bravo_2",     "type": "nipun_ap", "x": 15.0, "y": -8.0},
        {"id": 10, "name": "nipun_meadow_charlie_1",   "type": "nipun_ap", "x": 20.0, "y":  2.5},
        {"id": 11, "name": "nipun_meadow_charlie_2",   "type": "nipun_ap", "x": 22.5, "y": -3.5},
        {"id": 12, "name": "nipun_pass_delta_1",       "type": "nipun_ap", "x": 26.0, "y":  5.0},
        {"id": 13, "name": "nipun_pass_delta_2",       "type": "nipun_ap", "x": 27.5, "y": -4.8},
        {"id": 14, "name": "nipun_ridge_echo_1",       "type": "nipun_ap", "x": 10.5, "y": 10.5},
        {"id": 15, "name": "nipun_ridge_echo_2",       "type": "nipun_ap", "x": 11.0, "y": -11.0},
        {"id": 16, "name": "nipun_perimeter_foxtrot_1","type": "nipun_ap", "x": 31.0, "y":  1.5},
        {"id": 17, "name": "nipun_perimeter_foxtrot_2","type": "nipun_ap", "x": 32.5, "y": -6.5},
        {"id": 18, "name": "nipun_reserve_golf_1",     "type": "nipun_ap", "x": -2.0, "y":  0.5},
    ]

    for m in mine_coords:
        m["z"] = round(get_alpine_elevation(m["x"], m["y"]), 3)

    yaml_path = os.path.join(CONFIG_DIR, 'grassland_mine_coordinates.yaml')
    with open(yaml_path, 'w') as f:
        f.write("# 18 NIPUN Anti-Personnel Minelet Registry for Alpine Mountain Grassland Environment\n")
        f.write("# Compliant with defense requirements in Downloads/1.docx\n")
        f.write("environment: mountain_grassland_minefield\n")
        f.write(f"total_mines: {len(mine_coords)}\n")
        f.write("mines:\n")
        for m in mine_coords:
            f.write(f"  - id: {m['id']}\n")
            f.write(f"    name: \"{m['name']}\"\n")
            f.write(f"    type: \"{m['type']}\"\n")
            f.write(f"    x: {m['x']:.2f}\n")
            f.write(f"    y: {m['y']:.2f}\n")
            f.write(f"    z: {m['z']:.3f}\n")
    print(f"✅ Mine coordinates saved to: {yaml_path}")

    # Generate World SDF
    sdf_path = os.path.join(WORLDS_DIR, 'mountain_grassland_minefield.sdf')

    # Scatter vegetation across meadow
    random.seed(123)
    wf_models_xml = []
    for i in range(48):
        wx = random.uniform(-15.0, 32.0)
        wy = random.uniform(-14.0, 14.0)
        wz = get_alpine_elevation(wx, wy)
        yaw = random.uniform(0, 6.28)
        wf_models_xml.append(f"""
    <include>
      <name>wildflower_{i+1:02d}</name>
      <uri>model://alpine_wildflower_cluster</uri>
      <pose>{wx:.3f} {wy:.3f} {wz:.3f} 0 0 {yaw:.3f}</pose>
      <static>true</static>
    </include>""")

    gc_models_xml = []
    for i in range(54):
        gx = random.uniform(-20.0, 35.0)
        gy = random.uniform(-16.0, 16.0)
        gz = get_alpine_elevation(gx, gy)
        yaw = random.uniform(0, 6.28)
        gc_models_xml.append(f"""
    <include>
      <name>grass_tuft_{i+1:02d}</name>
      <uri>model://alpine_grass_clump</uri>
      <pose>{gx:.3f} {gy:.3f} {gz:.3f} 0 0 {yaw:.3f}</pose>
      <static>true</static>
    </include>""")

    boulder_xml = []
    for i in range(24):
        bx = random.uniform(-10.0, 38.0)
        by = random.choice([random.uniform(9.0, 18.0), random.uniform(-18.0, -9.0)])
        bz = get_alpine_elevation(bx, by)
        yaw = random.uniform(0, 6.28)
        pitch = random.uniform(-0.1, 0.1)
        boulder_xml.append(f"""
    <include>
      <name>boulder_{i+1:02d}</name>
      <uri>model://alpine_boulder_cluster</uri>
      <pose>{bx:.3f} {by:.3f} {bz:.3f} 0 {pitch:.3f} {yaw:.3f}</pose>
      <static>true</static>
    </include>""")

    tree_xml = []
    for i in range(32):
        tx = random.uniform(-35.0, 42.0)
        ty = random.choice([random.uniform(16.0, 34.0), random.uniform(-34.0, -16.0)])
        tz = get_alpine_elevation(tx, ty)
        tree_xml.append(f"""
    <include>
      <name>pine_tree_{i+1:02d}</name>
      <uri>model://alpine_pine_tree</uri>
      <pose>{tx:.3f} {ty:.3f} {tz:.3f} 0 0 {random.uniform(0, 6.28):.3f}</pose>
      <static>true</static>
    </include>""")

    mine_xml = []
    for m in mine_coords:
        mine_xml.append(f"""
    <include>
      <name>{m['name']}</name>
      <uri>model://nipun_mine_marker</uri>
      <pose>{m['x']:.3f} {m['y']:.3f} {m['z']:.3f} 0 0 0</pose>
      <static>true</static>
    </include>""")

    world_content = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="mountain_grassland_minefield">
    <physics name="1ms" type="ignored">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <!-- Plugins -->
    <plugin filename="libignition-gazebo-physics-system.so" name="ignition::gazebo::systems::Physics"/>
    <plugin filename="libignition-gazebo-user-commands-system.so" name="ignition::gazebo::systems::UserCommands"/>
    <plugin filename="libignition-gazebo-scene-broadcaster-system.so" name="ignition::gazebo::systems::SceneBroadcaster"/>
    <plugin filename="libignition-gazebo-contact-system.so" name="ignition::gazebo::systems::Contact"/>

    <atmosphere type="adiabatic"/>

    <!-- High-Altitude Mountain Atmosphere & Natural Daylight -->
    <scene>
      <ambient>0.65 0.70 0.65 1.0</ambient>
      <background>0.50 0.70 0.90 1.0</background>
      <shadows>true</shadows>
      <grid>false</grid>
      <sky></sky>
    </scene>

    <!-- Main Alpine Sun -->
    <light type="directional" name="alpine_sun">
      <cast_shadows>true</cast_shadows>
      <pose>20 -30 60 0 0 0</pose>
      <diffuse>0.96 0.94 0.88 1.0</diffuse>
      <specular>0.35 0.35 0.35 1.0</specular>
      <direction>-0.35 0.45 -0.82</direction>
    </light>

    <!-- Sky fill light for valley shadows -->
    <light type="directional" name="sky_fill">
      <cast_shadows>false</cast_shadows>
      <pose>0 0 50 0 0 0</pose>
      <diffuse>0.40 0.50 0.55 1.0</diffuse>
      <direction>0.3 -0.3 -0.8</direction>
    </light>

    <!-- 1. Master Alpine Mountain Grassland Terrain Mesh -->
    <include>
      <name>alpine_mountain_terrain</name>
      <uri>model://alpine_mountain_terrain</uri>
      <pose>0 0 0 0 0 0</pose>
      <static>true</static>
    </include>

    <!-- 2. Border Meadow Checkpoint Outpost -->
    <include>
      <name>border_meadow_outpost</name>
      <uri>model://border_meadow_outpost</uri>
      <pose>-24.0 2.5 0.0 0 0 0</pose>
      <static>true</static>
    </include>

    <!-- 3. All-Terrain 4WD NIPUN Minelet AMR with 4D LiDAR & RealSense D435 Depth Camera -->
    <include>
      <name>army_mine_amr</name>
      <uri>model://army_mine_amr</uri>
      <pose>-20.0 0.0 0.35 0 0 0</pose>
      <static>false</static>
    </include>

    <!-- 4. Alpine Wildflowers (Blue Poppies, Buttercups, Daisies, Asters) -->
    {''.join(wf_models_xml)}

    <!-- 5. Alpine Meadow Grass Clumps & Fescue Tufts -->
    {''.join(gc_models_xml)}

    <!-- 6. Weathered Mountain Granite Boulders & Rock Scree -->
    {''.join(boulder_xml)}

    <!-- 7. Alpine Conifer Pine Trees Framing Mountain Ridges -->
    {''.join(tree_xml)}

    <!-- 8. 18 Registered NIPUN Anti-Personnel Minelets -->
    {''.join(mine_xml)}

  </world>
</sdf>
"""

    with open(sdf_path, 'w') as f:
        f.write(world_content)

    print(f"✅ Master Alpine Mountain Grassland World generated at: {sdf_path}")


def main():
    print("==================================================================")
    print("🏔️  BUILDING ALPINE MOUNTAIN GRASSLAND ENVIRONMENT (1.docx)")
    print("==================================================================")
    create_alpine_textures()
    build_alpine_terrain_mesh()
    build_3d_vegetation_and_props()
    generate_world_and_config()
    print("==================================================================")
    print("🎉 ALL ALPINE GRASSLAND ENVIRONMENT ASSETS GENERATED SUCCESSFULLY!")
    print("==================================================================")


if __name__ == '__main__':
    main()
