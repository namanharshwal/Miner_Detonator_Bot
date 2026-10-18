import os
import shutil
import trimesh
import numpy as np

BASE_DIR = '/home/nammy/army_mine_bot/src/army_border_world'
MODELS_DIR = os.path.join(BASE_DIR, 'models')
TEX_DIR = os.path.join(BASE_DIR, 'materials/textures')

# 1. Copy the photorealistic soldier texture
soldier_tex_src = '/tmp/soldier_diffuse.png'
soldier_tex_dst = os.path.join(TEX_DIR, 'soldier_diffuse.png')
shutil.copyfile(soldier_tex_src, soldier_tex_dst)
print(f"Copied {soldier_tex_dst}")

def make_model(name, mesh_visual, mesh_coll, desc):
    model_dir = os.path.join(MODELS_DIR, name)
    meshes_dir = os.path.join(model_dir, 'meshes')
    os.makedirs(meshes_dir, exist_ok=True)

    _ = mesh_visual.vertex_normals
    _ = mesh_coll.vertex_normals

    dae_path = os.path.join(meshes_dir, 'visual.dae')
    stl_path = os.path.join(meshes_dir, 'collision.stl')
    mesh_visual.export(dae_path)
    mesh_coll.export(stl_path)

    # Copy texture inside model folder too for maximum compatibility
    model_tex_dir = os.path.join(model_dir, 'materials/textures')
    os.makedirs(model_tex_dir, exist_ok=True)
    shutil.copyfile(soldier_tex_src, os.path.join(model_tex_dir, 'soldier_diffuse.png'))

    # Config
    config_xml = f"""<?xml version="1.0"?>
<model>
  <name>{name}</name>
  <version>1.0</version>
  <sdf version="1.6">model.sdf</sdf>
  <author>
    <name>Army Mine Bot Team</name>
  </author>
  <description>{desc}</description>
</model>
"""
    with open(os.path.join(model_dir, 'model.config'), 'w') as f:
        f.write(config_xml)

    # SDF
    sdf_xml = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="{name}">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://{name}/meshes/visual.dae</uri>
          </mesh>
        </geometry>
        <material>
          <ambient>0.6 0.6 0.6 1</ambient>
          <diffuse>0.85 0.85 0.85 1</diffuse>
          <specular>0.2 0.2 0.2 1</specular>
          <pbr>
            <metal>
              <albedo_map>{soldier_tex_dst}</albedo_map>
            </metal>
          </pbr>
        </material>
      </visual>
      <collision name="collision">
        <geometry>
          <mesh>
            <uri>model://{name}/meshes/collision.stl</uri>
          </mesh>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
"""
    with open(os.path.join(model_dir, 'model.sdf'), 'w') as f:
        f.write(sdf_xml)
    print(f"[{name}] successfully updated with realistic soldier mesh!")

# Load standing mesh
m_stand = trimesh.load('/tmp/soldier_standing.obj', force='mesh')
# Ensure base is exactly at z = 0
min_z = m_stand.bounds[0, 2]
m_stand.apply_translation([0, 0, -min_z])
make_model("soldier_standing_sentry", m_stand, m_stand, "Realistic military combat soldier sentry standing alert in uniform and body armor")

# Load sitting mesh
m_sit = trimesh.load('/tmp/soldier_sitting.obj', force='mesh')
# In m_sit, feet are down near 0, hips/buttocks are at z ~0.44m
# Add a camp stool / crate beneath the buttocks
stool = trimesh.creation.box([0.42, 0.42, 0.42])
stool.apply_translation([0.0, 0.0, 0.21])

m_sit_single = trimesh.util.concatenate([m_sit, stool])
make_model("soldier_sitting", m_sit_single, m_sit_single, "Realistic military combat soldier sitting on camp stool in uniform and tactical helmet")

# Military Bench with 2 sitting soldiers
bench_seat = trimesh.creation.box([0.45, 2.2, 0.06])
bench_seat.apply_translation([0.0, 0.0, 0.42])
leg1 = trimesh.creation.box([0.42, 0.10, 0.40])
leg1.apply_translation([0.0, -0.95, 0.20])
leg2 = trimesh.creation.box([0.42, 0.10, 0.40])
leg2.apply_translation([0.0, 0.95, 0.20])
bench = trimesh.util.concatenate([bench_seat, leg1, leg2])

# Soldier 1 sitting on left
s1 = m_sit.copy()
s1.apply_translation([0.0, -0.50, 0.0])

# Soldier 2 sitting on right, angled slightly towards soldier 1
s2 = m_sit.copy()
s2.apply_transform(trimesh.transformations.rotation_matrix(0.2, [0, 0, 1]))
s2.apply_translation([0.0, 0.50, 0.0])

soldier_bench = trimesh.util.concatenate([bench, s1, s2])
make_model("soldier_sitting_bench", soldier_bench, soldier_bench, "Camp briefing bench with two realistic military soldiers in camouflage sitting together")

print("All realistic soldier models installed successfully!")
