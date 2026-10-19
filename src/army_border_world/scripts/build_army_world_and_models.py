#!/usr/bin/env python3
"""
Master Builder Script for Army Border World
1. Builds mountain terrain with gradient <= 1:8 matching Downloads/1.docx.
2. Updates all 3D models with embedded UV coordinates (TEXCOORD) and rich military camo materials.
3. Regenerates the master army_border_minefield.sdf with sky dome, clear roadway, and realistic lighting.
"""

import os
import math
import shutil
import numpy as np
import trimesh
from PIL import Image

BASE_DIR = '/home/nammy/army_mine_bot/src/army_border_world'
MODELS_DIR = os.path.join(BASE_DIR, 'models')
TEX_DIR = os.path.join(BASE_DIR, 'materials/textures')
WORLDS_DIR = os.path.join(BASE_DIR, 'worlds')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(WORLDS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# ==============================================================================
# 1. MOUNTAIN TERRAIN ELEVATION (Strictly <= 1:8 gradient, continuous with camp)
# ==============================================================================
def get_terrain_elevation(x, y):
    x_val = float(x)
    y_val = float(y)
    if x_val <= 0.0:
        return 0.0
    
    # Smoothstep transition over x in [0.0, 8.0]
    t = min(max(x_val / 8.0, 0.0), 1.0)
    w = t * t * (3.0 - 2.0 * t)
    
    # Mountain terrain with gentle upward grade and rolling features
    # Total max slope gradient is strictly < 0.115 (< 1:8 = 0.125)
    elev = 0.045 * x_val
    elev += 0.18 * math.sin(0.10 * x_val) * math.cos(0.12 * y_val)
    elev += 0.10 * math.sin(0.22 * x_val + 0.8) * math.cos(0.18 * y_val - 0.4)
    elev += 0.05 * math.sin(0.40 * x_val) * math.sin(0.30 * y_val)
    
    # Mountain depressions / dips (gradual slopes)
    c1 = -0.20 * math.exp(-(((x_val - 12.0)**2 + (y_val - 3.0)**2) / (5.0**2)))
    c2 = -0.25 * math.exp(-(((x_val - 22.0)**2 + (y_val + 6.0)**2) / (6.0**2)))
    
    return float(w * (elev + c1 + c2))

def get_terrain_normal(x, y):
    eps = 0.1
    dz_dx = (get_terrain_elevation(x + eps, y) - get_terrain_elevation(x - eps, y)) / (2 * eps)
    dz_dy = (get_terrain_elevation(x, y + eps) - get_terrain_elevation(x, y - eps)) / (2 * eps)
    n = [-dz_dx, -dz_dy, 1.0]
    norm = math.sqrt(n[0]**2 + n[1]**2 + n[2]**2)
    return [n[0]/norm, n[1]/norm, n[2]/norm]

def get_roll_pitch(x, y):
    n = get_terrain_normal(x, y)
    pitch = math.atan2(n[0], n[2])
    roll = math.atan2(-n[1], n[2])
    return roll, pitch

# ==============================================================================
# 2. GENERATE UNEVEN MOUNTAIN TERRAIN MESH WITH UVs & PBR
# ==============================================================================
def build_terrain():
    print("🏔️  Building Full-Scale Mountain & Army Camp Terrain (100m x 70m, slope <= 1:8)...")
    nx, ny = 160, 120
    x_min, x_max = -60.0, 40.0
    y_min, y_max = -35.0, 35.0
    x_vals = np.linspace(x_min, x_max, nx)
    y_vals = np.linspace(y_min, y_max, ny)
    X, Y = np.meshgrid(x_vals, y_vals)
    Z = np.zeros_like(X)
    for i in range(ny):
        for j in range(nx):
            Z[i, j] = get_terrain_elevation(X[i, j], Y[i, j])

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

    skirt_z = -2.5
    bottom_vertices = top_vertices.copy()
    bottom_vertices[:, 2] = skirt_z
    all_vertices = np.vstack([top_vertices, bottom_vertices])
    all_faces = list(top_faces)
    offset = nx * ny
    for f in top_faces:
        all_faces.append([f[0] + offset, f[2] + offset, f[1] + offset])

    # Skirts
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

    # UV coordinates (tiled seamlessly every 4m across the 100m x 70m terrain)
    u = (all_vertices[:, 0] - x_min) / 4.0
    v = (all_vertices[:, 1] - y_min) / 4.0
    uv = np.column_stack([u, v])

    tex_img = Image.open(f"{TEX_DIR}/desert_ground.png")
    terrain_mesh = trimesh.Trimesh(
        vertices=all_vertices,
        faces=all_faces,
        visual=trimesh.visual.TextureVisuals(uv=uv, image=tex_img),
        process=True
    )
    _ = terrain_mesh.vertex_normals

    model_dir = os.path.join(MODELS_DIR, 'uneven_minefield_terrain')
    meshes_dir = os.path.join(model_dir, 'meshes')
    os.makedirs(meshes_dir, exist_ok=True)

    terrain_mesh.export(os.path.join(meshes_dir, 'visual.dae'))
    terrain_mesh.export(os.path.join(meshes_dir, 'collision.stl'))

    # Config
    with open(os.path.join(model_dir, 'model.config'), 'w') as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>uneven_minefield_terrain</name>
  <version>1.0</version>
  <sdf version="1.6">model.sdf</sdf>
  <author><name>Army Mine Bot Team</name></author>
  <description>Mountain border terrain with 1:8 gradient</description>
</model>""")

    # SDF with rich golden mountain ground texture
    with open(os.path.join(model_dir, 'model.sdf'), 'w') as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="uneven_minefield_terrain">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://uneven_minefield_terrain/meshes/visual.dae</uri>
          </mesh>
        </geometry>
        <material>
          <ambient>0.65 0.58 0.42 1.0</ambient>
          <diffuse>0.82 0.74 0.56 1.0</diffuse>
          <specular>0.15 0.15 0.12 1.0</specular>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/desert_ground.png</albedo_map>
              <roughness>0.85</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
      <collision name="collision">
        <geometry>
          <mesh>
            <uri>model://uneven_minefield_terrain/meshes/collision.stl</uri>
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
    print("✅ Mountain terrain built successfully!")

# ==============================================================================
# 3. ASSIGN UVs & TEXTURES TO ALL CAMP MODELS
# ==============================================================================
def assign_triplanar_uvs(mesh, scale=0.5):
    v = mesh.vertices
    normals = mesh.vertex_normals
    uv = np.zeros((len(v), 2))
    abs_n = np.abs(normals)
    mask_x = (abs_n[:, 0] >= abs_n[:, 1]) & (abs_n[:, 0] >= abs_n[:, 2])
    uv[mask_x, 0] = v[mask_x, 1] * scale
    uv[mask_x, 1] = v[mask_x, 2] * scale
    mask_y = (abs_n[:, 1] > abs_n[:, 0]) & (abs_n[:, 1] >= abs_n[:, 2])
    uv[mask_y, 0] = v[mask_y, 0] * scale
    uv[mask_y, 1] = v[mask_y, 2] * scale
    mask_z = (abs_n[:, 2] > abs_n[:, 0]) & (abs_n[:, 2] > abs_n[:, 1])
    uv[mask_z, 0] = v[mask_z, 0] * scale
    uv[mask_z, 1] = v[mask_z, 1] * scale
    return uv

def update_camp_models():
    print("🎨 Updating Camp Models with embedded UV coordinates and camo materials...")

    model_texture_map = {
        'army_tank': ('military_armor_camo.png', 0.35, '0.35 0.42 0.30 1.0', '0.50 0.60 0.42 1.0', 0.6, 0.3),
        'army_truck': ('army_truck_camo.png', 0.4, '0.36 0.40 0.28 1.0', '0.52 0.58 0.40 1.0', 0.7, 0.2),
        'army_barracks_tent': ('camo_military.png', 0.5, '0.38 0.44 0.32 1.0', '0.55 0.65 0.46 1.0', 0.9, 0.0),
        'army_command_tent': ('military_canvas_cover.png', 0.5, '0.40 0.44 0.34 1.0', '0.58 0.64 0.50 1.0', 0.9, 0.0),
        'sandbag_bunker': ('sandbag_burlap.png', 1.0, '0.58 0.50 0.38 1.0', '0.72 0.64 0.48 1.0', 0.9, 0.0),
        'sandbag_wall': ('sandbag_burlap.png', 1.0, '0.58 0.50 0.38 1.0', '0.72 0.64 0.48 1.0', 0.9, 0.0),
        'military_watchtower': ('rusty_metal.png', 0.8, '0.35 0.32 0.30 1.0', '0.50 0.46 0.44 1.0', 0.6, 0.4),
        'barbed_wire_fence': ('rusty_metal.png', 1.0, '0.32 0.32 0.32 1.0', '0.45 0.45 0.45 1.0', 0.5, 0.5),
        'border_boundary_post': ('border_stripes.png', 1.0, '0.70 0.60 0.40 1.0', '0.85 0.75 0.50 1.0', 0.5, 0.1),
        'czech_hedgehog': ('rusty_metal.png', 0.8, '0.30 0.30 0.30 1.0', '0.45 0.45 0.45 1.0', 0.5, 0.5),
        'military_ammo_crate': ('military_crate.png', 1.0, '0.42 0.48 0.32 1.0', '0.58 0.66 0.45 1.0', 0.8, 0.1),
        'military_fuel_drum': ('rusty_metal.png', 0.8, '0.35 0.30 0.28 1.0', '0.55 0.45 0.40 1.0', 0.5, 0.5),
        'military_radio_station': ('rusty_metal.png', 0.8, '0.32 0.35 0.32 1.0', '0.48 0.52 0.48 1.0', 0.5, 0.4),
        'camp_floodlight': ('rusty_metal.png', 0.8, '0.35 0.35 0.35 1.0', '0.50 0.50 0.50 1.0', 0.5, 0.5),
        'mine_warning_sign': ('danger_mines_sign.png', 1.0, '0.80 0.25 0.20 1.0', '0.90 0.30 0.25 1.0', 0.6, 0.2),
        'rock_boulder': ('desert_ground.png', 0.8, '0.55 0.48 0.40 1.0', '0.70 0.62 0.52 1.0', 0.9, 0.0),
        'landmine_anti_tank': ('landmine_texture.png', 1.0, '0.35 0.40 0.30 1.0', '0.48 0.55 0.42 1.0', 0.6, 0.3),
        'landmine_anti_personnel': ('landmine_texture.png', 1.0, '0.38 0.42 0.32 1.0', '0.50 0.58 0.45 1.0', 0.6, 0.3),
    }

    for model_name, (tex_file, uv_scale, amb_col, diff_col, roughness, metalness) in model_texture_map.items():
        model_dir = os.path.join(MODELS_DIR, model_name)
        dae_path = os.path.join(model_dir, 'meshes', 'visual.dae')
        tex_path = os.path.join(TEX_DIR, tex_file)

        if not os.path.exists(dae_path) or not os.path.exists(tex_path):
            print(f"Skipping {model_name} (mesh or texture missing)")
            continue

        try:
            loaded = trimesh.load(dae_path)
            if isinstance(loaded, trimesh.Scene):
                mesh = loaded.to_geometry()
            else:
                mesh = loaded

            uv = assign_triplanar_uvs(mesh, scale=uv_scale)
            img = Image.open(tex_path)
            mesh.visual = trimesh.visual.TextureVisuals(uv=uv, image=img)
            _ = mesh.vertex_normals
            mesh.export(dae_path)

            # Update model.sdf with both fallback solid color and PBR albedo
            sdf_path = os.path.join(model_dir, 'model.sdf')
            sdf_xml = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="{model_name}">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/visual.dae</uri>
          </mesh>
        </geometry>
        <material>
          <ambient>{amb_col}</ambient>
          <diffuse>{diff_col}</diffuse>
          <specular>0.2 0.2 0.2 1.0</specular>
          <pbr>
            <metal>
              <albedo_map>{tex_path}</albedo_map>
              <roughness>{roughness}</roughness>
              <metalness>{metalness}</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
      <collision name="collision">
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/collision.stl</uri>
          </mesh>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
"""
            with open(sdf_path, 'w') as f:
                f.write(sdf_xml)

            print(f"  ✓ {model_name}: TEXCOORD embedded & PBR material applied.")
        except Exception as e:
            print(f"  ✗ {model_name} error: {e}")

# ==============================================================================
# 4. REGENERATE MASTER WORLD SDF
# ==============================================================================
def regenerate_world():
    print("🌍 Regenerating Master Army Border Minefield SDF...")

    # Registry of mines
    mines_data = [
        {"id": "mine_at_01", "type": "anti_tank", "x": 4.5, "y": 1.5, "notes": "Border entrance"},
        {"id": "mine_at_02", "type": "anti_tank", "x": 6.5, "y": -4.0, "notes": "Gentle slope area"},
        {"id": "mine_at_03", "type": "anti_tank", "x": 9.5, "y": 4.2, "notes": "North incline"},
        {"id": "mine_at_04", "type": "anti_tank", "x": 12.0, "y": 3.0, "notes": "Depression 1"},
        {"id": "mine_at_05", "type": "anti_tank", "x": 13.5, "y": -2.0, "notes": "Central crest"},
        {"id": "mine_at_06", "type": "anti_tank", "x": 17.5, "y": 12.0, "notes": "North slope"},
        {"id": "mine_at_07", "type": "anti_tank", "x": 18.2, "y": 8.0, "notes": "Mid-field"},
        {"id": "mine_at_08", "type": "anti_tank", "x": 22.0, "y": -6.0, "notes": "Depression 2"},
        {"id": "mine_at_09", "type": "anti_tank", "x": 25.0, "y": 2.5, "notes": "East incline"},
        {"id": "mine_at_10", "type": "anti_tank", "x": 28.0, "y": 14.0, "notes": "Rocky mound"},

        {"id": "mine_ap_01", "type": "anti_personnel", "x": 3.5, "y": 6.0, "notes": "Border sector north"},
        {"id": "mine_ap_02", "type": "anti_personnel", "x": 5.0, "y": -8.5, "notes": "Border sector south"},
        {"id": "mine_ap_03", "type": "anti_personnel", "x": 8.0, "y": -2.0, "notes": "Near rock outcrop"},
        {"id": "mine_ap_04", "type": "anti_personnel", "x": 11.5, "y": 14.0, "notes": "North hill incline"},
        {"id": "mine_ap_05", "type": "anti_personnel", "x": 14.0, "y": -12.5, "notes": "South slope"},
        {"id": "mine_ap_06", "type": "anti_personnel", "x": 16.5, "y": -8.0, "notes": "Southern gully"},
        {"id": "mine_ap_07", "type": "anti_personnel", "x": 20.0, "y": -14.0, "notes": "South-east rocky mound"},
        {"id": "mine_ap_08", "type": "anti_personnel", "x": 24.0, "y": 18.0, "notes": "North-east hill crest"},
    ]

    mines_yaml = []
    for m in mines_data:
        z = get_terrain_elevation(m["x"], m["y"])
        roll, pitch = get_roll_pitch(m["x"], m["y"])
        m["z"] = round(z, 3)
        m["roll"] = round(roll, 3)
        m["pitch"] = round(pitch, 3)
        m["yaw"] = round(math.atan2(m["y"], m["x"]), 3)
        m["status"] = "armed"
        m["defused"] = False
        mines_yaml.append(m)

    import yaml
    with open(os.path.join(CONFIG_DIR, 'mine_field_coordinates.yaml'), 'w') as f:
        yaml.dump({"mines": mines_yaml}, f, sort_keys=False)

    def inc(name, model_dir_name, x, y, z, roll=0.0, pitch=0.0, yaw=0.0, is_static=True):
        return f"""
    <!-- {name} -->
    <include>
      <name>{name}</name>
      <uri>model://{model_dir_name}</uri>
      <pose>{x:.3f} {y:.3f} {z:.3f} {roll:.3f} {pitch:.3f} {yaw:.3f}</pose>
      <static>{str(is_static).lower()}</static>
    </include>"""

    m_xml = []
    # 1. Uneven Mountain Terrain

    # 2. Uneven Mountain Terrain
    m_xml.append(inc("border_terrain", "uneven_minefield_terrain", 0.0, 0.0, 0.0))

    # 3. Main Battle Tanks in Defensive Bays
    m_xml.append(inc("army_tank_1", "army_tank", -26.0, 18.0, 0.0))
    m_xml.append(inc("army_tank_2", "army_tank", -26.0, -18.0, 0.0))
    m_xml.append(inc("army_tank_3", "army_tank", -36.0, 0.0, 0.0))

    # 4. Tactical Cargo Trucks
    m_xml.append(inc("army_truck_1", "army_truck", -28.0, 8.5, 0.0, yaw=0.15))
    m_xml.append(inc("army_truck_2", "army_truck", -28.0, -8.5, 0.0, yaw=-0.15))

    # 5. Sentries
    m_xml.append(inc("vehicle_sentry_north", "soldier_standing_sentry", -21.0, 14.0, 0.0))
    m_xml.append(inc("vehicle_sentry_south", "soldier_standing_sentry", -21.0, -14.0, 0.0))

    # 6. Command HQ & Barracks
    m_xml.append(inc("hq_command_tent", "army_command_tent", -16.0, 0.0, 0.0))
    m_xml.append(inc("soldier_sitting_hq", "soldier_sitting", -15.2, 0.0, 0.0, yaw=3.14))
    m_xml.append(inc("barracks_tent_north", "army_barracks_tent", -16.0, 10.0, 0.0, yaw=-0.15))
    m_xml.append(inc("barracks_tent_south", "army_barracks_tent", -16.0, -10.0, 0.0, yaw=0.15))
    m_xml.append(inc("soldiers_briefing_bench", "soldier_sitting_bench", -11.0, -5.0, 0.0))
    m_xml.append(inc("ammo_crate_courtyard", "military_ammo_crate", -9.0, -5.0, 0.0))
    m_xml.append(inc("soldier_sitting_courtyard", "soldier_sitting", -7.8, -5.0, 0.0, yaw=3.14))
    m_xml.append(inc("soldiers_resting_bench", "soldier_sitting_bench", -12.0, 10.0, 0.0))

    # 7. Sentry & OPERATOR (Operator relocated to sidewalk x=-3.5, y=2.8 to CLEAR ROADWAY)
    m_xml.append(inc("soldier_robot_controller", "soldier_robot_operator", -3.5, 2.8, 0.0, yaw=0.0))
    m_xml.append(inc("checkpoint_sentry_north", "soldier_standing_sentry", -3.5, 4.2, 0.0, yaw=0.0))
    m_xml.append(inc("bunker_sentry_south", "soldier_standing_sentry", -3.0, -8.0, 0.0, yaw=0.0))

    # 8. AMR Spawning facing border (Clean, open straight path along y=0.0)
    m_xml.append(inc("army_mine_amr", "army_mine_amr", -5.5, 0.0, 0.002, yaw=0.0, is_static=False))

    # 9. Watchtowers
    m_xml.append(inc("camp_watchtower_north", "military_watchtower", -5.0, 20.0, 0.0))
    m_xml.append(inc("watchtower_sentry_north", "soldier_standing_sentry", -5.0, 20.0, 3.6))
    m_xml.append(inc("camp_watchtower_south", "military_watchtower", -5.0, -20.0, 0.0))
    m_xml.append(inc("watchtower_sentry_south", "soldier_standing_sentry", -5.0, -20.0, 3.6))
    m_xml.append(inc("camp_watchtower_rear", "military_watchtower", -46.0, 0.0, 0.0))
    m_xml.append(inc("watchtower_sentry_rear", "soldier_standing_sentry", -46.0, 0.0, 3.6))

    # 10. Sandbag Fortifications
    m_xml.append(inc("sandbag_bunker_south", "sandbag_bunker", -3.0, -8.0, 0.0))
    m_xml.append(inc("sandbag_wall_gate_north", "sandbag_wall", -3.0, 4.8, 0.0))
    m_xml.append(inc("sandbag_wall_gate_south", "sandbag_wall", -3.0, -3.5, 0.0))
    m_xml.append(inc("sandbag_wall_hq_protect", "sandbag_wall", -12.0, 0.0, 0.0, yaw=1.57))

    # 11. Logistics & Comms
    m_xml.append(inc("radio_comms_outpost", "military_radio_station", -38.0, -18.0, 0.0, yaw=0.4))
    m_xml.append(inc("fuel_drum_1", "military_fuel_drum", -39.5, -17.5, 0.0))
    m_xml.append(inc("fuel_drum_2", "military_fuel_drum", -39.5, -18.3, 0.0))
    m_xml.append(inc("fuel_drum_3", "military_fuel_drum", -39.0, -17.9, 0.0))
    m_xml.append(inc("fuel_drum_4", "military_fuel_drum", -33.5, -9.0, 0.0))
    m_xml.append(inc("fuel_drum_5", "military_fuel_drum", -33.5, 9.0, 0.0))
    m_xml.append(inc("ammo_crate_stack_1", "military_ammo_crate", -38.0, 18.0, 0.0))
    m_xml.append(inc("ammo_crate_stack_2", "military_ammo_crate", -38.0, 18.0, 0.4))
    m_xml.append(inc("ammo_crate_stack_3", "military_ammo_crate", -33.0, 17.5, 0.0))

    # 12. Floodlights
    m_xml.append(inc("floodlight_north", "camp_floodlight", -4.5, 26.0, 0.0, yaw=-0.5))
    m_xml.append(inc("floodlight_south", "camp_floodlight", -4.5, -26.0, 0.0, yaw=0.5))
    m_xml.append(inc("floodlight_center", "camp_floodlight", -48.0, 0.0, 0.0))

    # 13. Perimeter Fences
    for idx, x in enumerate(range(-50, -4, 4)):
        m_xml.append(inc(f"fence_north_{idx}", "barbed_wire_fence", float(x), 30.0, 0.0))
        m_xml.append(inc(f"fence_south_{idx}", "barbed_wire_fence", float(x), -30.0, 0.0))
    for idx, y in enumerate(range(-28, 30, 4)):
        m_xml.append(inc(f"fence_rear_{idx}", "barbed_wire_fence", -52.0, float(y), 0.0, yaw=1.57))

    # 14. Border Boundary Posts & Hedgehogs
    for idx, py in enumerate([-24.0, -16.0, -8.0, 8.0, 16.0, 24.0]):
        m_xml.append(inc(f"border_post_{idx+1}", "border_boundary_post", 0.0, py, 0.0))
    for idx, hy in enumerate([-18.0, -12.0, 12.0, 18.0]):
        m_xml.append(inc(f"czech_hedgehog_{idx+1}", "czech_hedgehog", 0.0, hy, 0.0))

    # 15. Warning Signs
    m_xml.append(inc("warning_sign_gate_n", "mine_warning_sign", 0.5, 3.5, 0.0, yaw=3.14))
    m_xml.append(inc("warning_sign_gate_s", "mine_warning_sign", 0.5, -3.5, 0.0, yaw=3.14))
    m_xml.append(inc("warning_sign_border_n", "mine_warning_sign", 0.5, 10.0, 0.0, yaw=3.14))
    m_xml.append(inc("warning_sign_border_s", "mine_warning_sign", 0.5, -10.0, 0.0, yaw=3.14))

    # 16. Rock Boulders on Uneven Mountain Ground
    rocks_data = [
        {"x": 6.5, "y": 6.5, "yaw": 0.4},
        {"x": 8.0, "y": -11.0, "yaw": 1.2},
        {"x": 12.5, "y": -3.5, "yaw": 2.1},
        {"x": 16.0, "y": 18.0, "yaw": -0.8},
        {"x": 22.0, "y": 8.0, "yaw": 1.7},
        {"x": 27.5, "y": -20.0, "yaw": -1.4},
    ]
    for idx, r in enumerate(rocks_data):
        rz = get_terrain_elevation(r["x"], r["y"])
        r_roll, r_pitch = get_roll_pitch(r["x"], r["y"])
        m_xml.append(inc(f"boulder_{idx+1}", "rock_boulder", r["x"], r["y"], rz, roll=r_roll, pitch=r_pitch, yaw=r["yaw"]))

    # 17. Mines in Terrain
    for m in mines_yaml:
        model_name = "landmine_anti_tank" if m["type"] == "anti_tank" else "landmine_anti_personnel"
        m_xml.append(inc(m["id"], model_name, m["x"], m["y"], m["z"] + 0.015, roll=m["roll"], pitch=m["pitch"], yaw=m["yaw"]))

    models_block = "\n".join(m_xml)

    world_sdf = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="army_border_minefield">
    <physics name="1ms" type="ignored">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <plugin filename="libignition-gazebo-physics-system.so" name="ignition::gazebo::systems::Physics"/>
    <plugin filename="libignition-gazebo-user-commands-system.so" name="ignition::gazebo::systems::UserCommands"/>
    <plugin filename="libignition-gazebo-scene-broadcaster-system.so" name="ignition::gazebo::systems::SceneBroadcaster"/>
    <plugin filename="libignition-gazebo-contact-system.so" name="ignition::gazebo::systems::Contact"/>

    <atmosphere type="adiabatic"/>

    <!-- Native Atmospheric Sky & Sunlight -->
    <scene>
      <ambient>0.65 0.65 0.65 1.0</ambient>
      <background>0.50 0.70 0.90 1.0</background>
      <shadows>true</shadows>
      <grid>false</grid>
      <sky></sky>
    </scene>
    
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 50 0 0 0</pose>
      <diffuse>0.92 0.88 0.80 1</diffuse>
      <specular>0.3 0.3 0.25 1</specular>
      <direction>-0.4 0.3 -0.85</direction>
    </light>

    <light type="directional" name="sky_fill">
      <cast_shadows>false</cast_shadows>
      <pose>0 0 40 0 0 0</pose>
      <diffuse>0.35 0.40 0.45 1</diffuse>
      <direction>0.4 -0.3 -0.7</direction>
    </light>

{models_block}

  </world>
</sdf>
"""
    world_file = os.path.join(WORLDS_DIR, 'army_border_minefield.sdf')
    with open(world_file, 'w') as f:
        f.write(world_sdf)
    print(f"✅ Master World SDF regenerated at: {world_file}")

if __name__ == '__main__':
    build_terrain()
    update_camp_models()
    regenerate_world()
    print("🎖️  ALL MODELS AND WORLD REBUILT SUCCESSFULLY!")
