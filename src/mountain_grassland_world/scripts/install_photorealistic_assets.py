#!/usr/bin/env python3
"""
Photorealistic Asset Installer & Model Builder for Mountain Grassland World
Converts OpenRobotics photogrammetry scans & Fuel models into local, self-contained,
high-fidelity simulation models for Gazebo Sim Harmonic.
"""

import os
import shutil
import re
import math
import random
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = '/home/nammy/army_mine_bot/src/mountain_grassland_world'
MODELS_DIR = os.path.join(BASE_DIR, 'models')
TEX_DIR = os.path.join(BASE_DIR, 'materials/textures')
FUEL_BASE = '/home/nammy/.gz/fuel/fuel.gazebosim.org/openrobotics/models'

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(TEX_DIR, exist_ok=True)


# ==============================================================================
# 1. INSTALL OPENROBOTICS PINE TREE MODEL
# ==============================================================================
def install_pine_tree():
    print("🌲 Installing High-Fidelity OpenRobotics Pine Tree Model...")
    src_dir = os.path.join(FUEL_BASE, 'pine tree/6')
    dst_dir = os.path.join(MODELS_DIR, 'alpine_pine_tree')
    os.makedirs(dst_dir, exist_ok=True)

    # Copy meshes & materials
    shutil.copytree(os.path.join(src_dir, 'meshes'), os.path.join(dst_dir, 'meshes'), dirs_exist_ok=True)
    shutil.copytree(os.path.join(src_dir, 'materials'), os.path.join(dst_dir, 'materials'), dirs_exist_ok=True)

    # Write clean local model.config
    with open(os.path.join(dst_dir, 'model.config'), 'w') as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>alpine_pine_tree</name>
  <version>1.0</version>
  <sdf version="1.6">model.sdf</sdf>
  <author><name>OpenRobotics / Naman Harshwal</name></author>
  <description>High-Fidelity 3D Himalayan Conifer Pine Tree</description>
</model>""")

    # Write self-contained local model.sdf
    with open(os.path.join(dst_dir, 'model.sdf'), 'w') as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="alpine_pine_tree">
    <static>true</static>
    <link name="link">
      <collision name="collision">
        <geometry>
          <cylinder>
            <radius>0.30</radius>
            <length>8.5</length>
          </cylinder>
        </geometry>
        <pose>0 0 4.25 0 0 0</pose>
      </collision>
      <visual name="branch">
        <geometry>
          <mesh>
            <uri>model://alpine_pine_tree/meshes/pine_tree.dae</uri>
            <submesh>
              <name>Branch</name>
            </submesh>
          </mesh>
        </geometry>
        <material>
          <double_sided>true</double_sided>
          <diffuse>1.0 1.0 1.0 1.0</diffuse>
          <pbr>
            <metal>
              <albedo_map>model://alpine_pine_tree/materials/textures/branch_2_diffuse.png</albedo_map>
              <roughness>0.85</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
      <visual name="bark">
        <geometry>
          <mesh>
            <uri>model://alpine_pine_tree/meshes/pine_tree.dae</uri>
            <submesh>
              <name>Bark</name>
            </submesh>
          </mesh>
        </geometry>
        <material>
          <diffuse>1.0 1.0 1.0 1.0</diffuse>
          <pbr>
            <metal>
              <albedo_map>model://alpine_pine_tree/materials/textures/bark_diffuse.png</albedo_map>
              <roughness>0.90</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
    </link>
  </model>
</sdf>""")
    print("✅ High-Fidelity Pine Tree installed!")


# ==============================================================================
# 2. INSTALL OPENROBOTICS PHOTOGRAMMETRY BOULDERS & ROCK FORMATIONS
# ==============================================================================
def install_photogrammetry_rocks():
    print("🪨 Installing OpenRobotics Photogrammetry Scanned Rock Models...")

    rock_mappings = [
        # (fuel_src, dst_name, mesh_name, collider_name, desc)
        ('falling rock 1/6', 'alpine_glacial_boulder', 'FallingRock01.dae', 'FallingRock01_Collider.dae', 'Large Glacial Granite Boulder'),
        ('falling rock 1/6', 'alpine_boulder_cluster', 'FallingRock01.dae', 'FallingRock01_Collider.dae', 'Large Mountain Boulder Cluster'),
        ('falling rock 2/6', 'alpine_medium_boulder', 'FallingRock02.dae', 'FallingRock02_Collider.dae', 'Medium Weathered Mountain Rock'),
        ('falling rock 3/6', 'alpine_meadow_rock', 'FallingRock03.dae', 'FallingRock03_Collider.dae', 'Alpine Meadow Rock'),
        ('falling rock 4/9', 'alpine_granite_rock_2', 'FallingRock04.dae', 'FallingRock04_Collider.dae', 'Fractured Granite Rock Fragment'),
        ('falling rock 3/6', 'alpine_talus_scree', 'FallingRock03.dae', 'FallingRock03_Collider.dae', 'Mountain Scree Stone')
    ]

    for fuel_rel, model_name, mesh_file, col_file, desc in rock_mappings:
        src_dir = os.path.join(FUEL_BASE, fuel_rel)
        dst_dir = os.path.join(MODELS_DIR, model_name)
        os.makedirs(dst_dir, exist_ok=True)

        shutil.copytree(os.path.join(src_dir, 'meshes'), os.path.join(dst_dir, 'meshes'), dirs_exist_ok=True)
        shutil.copytree(os.path.join(src_dir, 'materials'), os.path.join(dst_dir, 'materials'), dirs_exist_ok=True)

        # Write model.config
        with open(os.path.join(dst_dir, 'model.config'), 'w') as f:
            f.write(f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf version="1.6">model.sdf</sdf>
  <author><name>OpenRobotics / Naman Harshwal</name></author>
  <description>{desc}</description>
</model>""")

        # Write model.sdf with full PBR
        with open(os.path.join(dst_dir, 'model.sdf'), 'w') as f:
            f.write(f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="{model_name}">
    <static>true</static>
    <link name="link">
      <collision name="collision">
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{col_file}</uri>
          </mesh>
        </geometry>
      </collision>
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{mesh_file}</uri>
          </mesh>
        </geometry>
        <material>
          <diffuse>1.0 1.0 1.0 1.0</diffuse>
          <specular>0.2 0.2 0.2 1.0</specular>
          <pbr>
            <metal>
              <albedo_map>model://{model_name}/materials/textures/FallingRocks_Albedo.jpg</albedo_map>
              <normal_map>model://{model_name}/materials/textures/FallingRocks_Normal.jpg</normal_map>
              <roughness_map>model://{model_name}/materials/textures/FallingRocks_Roughness.jpg</roughness_map>
              <roughness>0.9</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
    </link>
  </model>
</sdf>""")
    print("✅ All Photogrammetry Scanned Rock Models installed!")


# ==============================================================================
# 3. BUILD VOLUMETRIC HIGH-DENSITY ALPINE WILDFLOWER MODELS
# ==============================================================================
def build_volumetric_wildflowers():
    print("🌸 Building Volumetric 3D Wildflower Bouquets & Floral Drifts...")

    # For each flower type, we build a multi-plane radial bouquet with a basal leaf skirt
    # 8 radial vertical planes + 2 angled horizontal ground leaf planes
    flower_types = [
        ('alpine_wildflower_poppy', 'alpine_wildflower_poppy.png', 0.55, 0.45, 'Himalayan Blue Poppy Bouquet'),
        ('alpine_wildflower_buttercup', 'alpine_wildflower_buttercup.png', 0.48, 0.35, 'Alpine Golden Buttercup Drift'),
        ('alpine_wildflower_daisy', 'alpine_wildflower_daisy.png', 0.50, 0.38, 'Mountain Daisy & Aster Cluster'),
        ('alpine_wildflower_gentian', 'alpine_wildflower_gentian.png', 0.45, 0.36, 'Alpine Royal Gentian Cluster'),
        ('alpine_wildflower_cluster', 'alpine_wildflower_poppy.png', 0.60, 0.45, 'Mixed Alpine Wildflower Bouquet'),
        ('alpine_dwarf_rhododendron', 'alpine_dwarf_rhododendron.png', 0.85, 0.52, 'Alpine Dwarf Rhododendron Shrub')
    ]

    for model_name, tex_file, width, height, desc in flower_types:
        m_dir = os.path.join(MODELS_DIR, model_name)
        m_meshes = os.path.join(m_dir, 'meshes')
        os.makedirs(m_meshes, exist_ok=True)

        planes = []
        n_rad = 6
        for i in range(n_rad):
            ang = i * (math.pi / n_rad)
            dx = (width / 2.0) * math.cos(ang)
            dy = (width / 2.0) * math.sin(ang)
            # Upright flower plane with slight outward flare
            v = np.array([
                [-dx * 0.4, -dy * 0.4, 0.0],
                [dx * 0.4, dy * 0.4, 0.0],
                [dx, dy, height],
                [-dx, -dy, height]
            ])
            f = np.array([[0, 1, 2], [0, 2, 3], [0, 2, 1], [0, 3, 2]])
            p_mesh = trimesh.Trimesh(vertices=v, faces=f)
            planes.append(p_mesh)

        # Basal ground leaf rosettes (2 cross planes at ground level z in [0, 0.12])
        r_w = width * 0.75
        for ang in [math.pi / 4.0, 3.0 * math.pi / 4.0]:
            dx = (r_w / 2.0) * math.cos(ang)
            dy = (r_w / 2.0) * math.sin(ang)
            v_g = np.array([
                [-dx, -dy, 0.02],
                [dx, dy, 0.02],
                [dx * 0.8, dy * 0.8, 0.12],
                [-dx * 0.8, -dy * 0.8, 0.12]
            ])
            f_g = np.array([[0, 1, 2], [0, 2, 3], [0, 2, 1], [0, 3, 2]])
            planes.append(trimesh.Trimesh(vertices=v_g, faces=f_g))

        full_flora = trimesh.util.concatenate(planes)
        tex_path = f"materials/textures/{tex_file}"
        tex_full_path = os.path.join(TEX_DIR, tex_file)
        tex_img = Image.open(tex_full_path)
        full_flora.visual = trimesh.visual.TextureVisuals(
            uv=np.tile(np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]), (len(planes), 1)),
            image=tex_img
        )

        full_flora.export(os.path.join(m_meshes, 'visual.dae'))

        # Also copy texture locally into model directory for self-containment
        m_tex_dir = os.path.join(m_dir, 'materials/textures')
        os.makedirs(m_tex_dir, exist_ok=True)
        shutil.copy(tex_full_path, os.path.join(m_tex_dir, tex_file))

        with open(os.path.join(m_dir, 'model.config'), 'w') as f:
            f.write(f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf version="1.6">model.sdf</sdf>
  <author><name>Naman Harshwal</name></author>
  <description>{desc}</description>
</model>""")

        with open(os.path.join(m_dir, 'model.sdf'), 'w') as f:
            f.write(f"""<?xml version="1.0" ?>
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
          <double_sided>true</double_sided>
          <diffuse>1.0 1.0 1.0 1.0</diffuse>
          <pbr>
            <metal>
              <albedo_map>model://{model_name}/materials/textures/{tex_file}</albedo_map>
              <roughness>0.82</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
      <collision name="collision">
        <geometry>
          <cylinder>
            <radius>{width * 0.35:.2f}</radius>
            <length>{height * 0.6:.2f}</length>
          </cylinder>
        </geometry>
        <pose>0 0 {height * 0.3:.2f} 0 0 0</pose>
      </collision>
    </link>
  </model>
</sdf>""")
    print("✅ Volumetric Wildflower Models created!")


# ==============================================================================
# 4. BUILD VOLUMETRIC ALPINE GRASS TUSSOCK & CLUMP MODELS
# ==============================================================================
def build_volumetric_grass():
    print("🌾 Building Volumetric Alpine Grass Clumps & Tussocks...")
    for model_name in ['alpine_grass_clump', 'alpine_grass_tussock']:
        m_dir = os.path.join(MODELS_DIR, model_name)
        m_meshes = os.path.join(m_dir, 'meshes')
        os.makedirs(m_meshes, exist_ok=True)

        width, height = 0.60, 0.48
        planes = []
        n_rad = 6
        for i in range(n_rad):
            ang = i * (math.pi / n_rad)
            dx = (width / 2.0) * math.cos(ang)
            dy = (width / 2.0) * math.sin(ang)
            v = np.array([
                [-dx * 0.3, -dy * 0.3, 0.0],
                [dx * 0.3, dy * 0.3, 0.0],
                [dx, dy, height],
                [-dx, -dy, height]
            ])
            f = np.array([[0, 1, 2], [0, 2, 3], [0, 2, 1], [0, 3, 2]])
            planes.append(trimesh.Trimesh(vertices=v, faces=f))

        full_grass = trimesh.util.concatenate(planes)
        tex_file = 'alpine_grass_meadow.png'
        tex_full_path = os.path.join(TEX_DIR, tex_file)
        tex_img = Image.open(tex_full_path)
        full_grass.visual = trimesh.visual.TextureVisuals(
            uv=np.tile(np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]), (len(planes), 1)),
            image=tex_img
        )
        full_grass.export(os.path.join(m_meshes, 'visual.dae'))

        m_tex_dir = os.path.join(m_dir, 'materials/textures')
        os.makedirs(m_tex_dir, exist_ok=True)
        shutil.copy(tex_full_path, os.path.join(m_tex_dir, tex_file))

        with open(os.path.join(m_dir, 'model.config'), 'w') as f:
            f.write(f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf version="1.6">model.sdf</sdf>
  <author><name>Naman Harshwal</name></author>
  <description>Volumetric Alpine Meadow Grass Tussock</description>
</model>""")

        with open(os.path.join(m_dir, 'model.sdf'), 'w') as f:
            f.write(f"""<?xml version="1.0" ?>
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
          <double_sided>true</double_sided>
          <diffuse>1.0 1.0 1.0 1.0</diffuse>
          <pbr>
            <metal>
              <albedo_map>model://{model_name}/materials/textures/{tex_file}</albedo_map>
              <roughness>0.85</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
      <collision name="collision">
        <geometry>
          <cylinder>
            <radius>0.25</radius>
            <length>0.40</length>
          </cylinder>
        </geometry>
        <pose>0 0 0.20 0 0 0</pose>
      </collision>
    </link>
  </model>
</sdf>""")
    print("✅ Volumetric Grass Models created!")


# ==============================================================================
# 5. BUILD FORTIFIED MILITARY MOUNTAIN OUTPOST (CAMO SHELTER, SANDBAGS, RELAY)
# ==============================================================================
def build_fortified_outpost():
    print("🎖️ Building Fortified High-Altitude Border Sentry Outpost...")
    m_dir = os.path.join(MODELS_DIR, 'border_meadow_outpost')
    m_meshes = os.path.join(m_dir, 'meshes')
    m_tex = os.path.join(m_dir, 'materials/textures')
    os.makedirs(m_meshes, exist_ok=True)
    os.makedirs(m_tex, exist_ok=True)

    # 1. Main Camouflaged Sentry Shelter (3.0m x 2.4m x 2.2m pitched roof shelter)
    shelter_box = trimesh.creation.box(extents=[3.0, 2.4, 2.0])
    shelter_box.apply_translation([0, 0, 1.0])

    # 2. Communication Relay Mast (4.5m tall steel mast with antenna cross-dipole)
    mast = trimesh.creation.cylinder(radius=0.08, height=4.5)
    mast.apply_translation([1.6, 1.3, 2.25])
    dish = trimesh.creation.cylinder(radius=0.45, height=0.08)
    dish.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 4.0, [0, 1, 0]))
    dish.apply_translation([1.6, 1.3, 4.2])

    # 3. Stacked Sandbag Revetments (Perimeter U-shape around outpost)
    sandbag_boxes = []
    # Front parapet (x = -1.8, y in [-1.5, 1.5])
    for sy in np.linspace(-1.4, 1.4, 5):
        for sz in [0.2, 0.55]:
            sb = trimesh.creation.box(extents=[0.55, 0.65, 0.32])
            sb.apply_translation([-1.8, sy, sz])
            sandbag_boxes.append(sb)
    # Side flanks
    for sx in np.linspace(-1.3, 1.3, 4):
        for sz in [0.2, 0.55]:
            sb_n = trimesh.creation.box(extents=[0.65, 0.55, 0.32])
            sb_n.apply_translation([sx, 1.6, sz])
            sb_s = trimesh.creation.box(extents=[0.65, 0.55, 0.32])
            sb_s.apply_translation([sx, -1.6, sz])
            sandbag_boxes.extend([sb_n, sb_s])

    outpost_mesh = trimesh.util.concatenate([shelter_box, mast, dish] + sandbag_boxes)

    # Texture with Camo
    camo_src = '/home/nammy/army_mine_bot/src/army_border_world/materials/textures/camo_military.png'
    shutil.copy(camo_src, os.path.join(m_tex, 'camo_military.png'))
    tex_camo = Image.open(camo_src)

    uv_outpost = np.column_stack([
        (outpost_mesh.vertices[:, 0] + 3.0) / 6.0,
        (outpost_mesh.vertices[:, 2]) / 4.0
    ])
    outpost_mesh.visual = trimesh.visual.TextureVisuals(uv=uv_outpost, image=tex_camo)

    outpost_mesh.export(os.path.join(m_meshes, 'visual.dae'))
    outpost_mesh.export(os.path.join(m_meshes, 'collision.stl'))

    with open(os.path.join(m_dir, 'model.config'), 'w') as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>border_meadow_outpost</name>
  <version>1.0</version>
  <sdf version="1.6">model.sdf</sdf>
  <author><name>Naman Harshwal</name></author>
  <description>Fortified Himalayan Border Sentry Outpost with Camo Revetments & Comms Mast</description>
</model>""")

    with open(os.path.join(m_dir, 'model.sdf'), 'w') as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="border_meadow_outpost">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://border_meadow_outpost/meshes/visual.dae</uri>
          </mesh>
        </geometry>
        <material>
          <diffuse>1.0 1.0 1.0 1.0</diffuse>
          <pbr>
            <metal>
              <albedo_map>model://border_meadow_outpost/materials/textures/camo_military.png</albedo_map>
              <roughness>0.88</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
      <collision name="collision">
        <geometry>
          <mesh>
            <uri>model://border_meadow_outpost/meshes/collision.stl</uri>
          </mesh>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>""")
    print("✅ Fortified Military Outpost created!")


if __name__ == '__main__':
    install_pine_tree()
    install_photogrammetry_rocks()
    build_volumetric_wildflowers()
    build_volumetric_grass()
    build_fortified_outpost()
    print("✨ ALL PHOTOREALISTIC ASSETS INSTALLED SUCCESSFULLY!")
