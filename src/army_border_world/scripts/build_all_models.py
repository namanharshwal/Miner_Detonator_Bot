import os
import math
import numpy as np
import trimesh
from PIL import Image

BASE_DIR = '/home/nammy/army_mine_bot/src/army_border_world'
MODELS_DIR = os.path.join(BASE_DIR, 'models')
TEX_DIR = os.path.join(BASE_DIR, 'materials/textures')

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_model_config(model_dir, model_name, desc=""):
    config_content = f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf version="1.6">model.sdf</sdf>
  <author>
    <name>Army Mine Bot Team</name>
    <email>army_mine_bot@simulation.org</email>
  </author>
  <description>{desc}</description>
</model>
"""
    with open(os.path.join(model_dir, 'model.config'), 'w') as f:
        f.write(config_content)

def write_sdf(model_dir, model_name, visual_mesh="visual.dae", coll_mesh="collision.stl", is_static=True, material_xml=None):
    if material_xml is None:
        material_xml = """<material>
          <ambient>0.6 0.6 0.6 1</ambient>
          <diffuse>0.8 0.8 0.8 1</diffuse>
          <specular>0.2 0.2 0.2 1</specular>
        </material>"""

    sdf_content = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="{model_name}">
    <static>{str(is_static).lower()}</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{visual_mesh}</uri>
          </mesh>
        </geometry>
        {material_xml}
      </visual>
      <collision name="collision">
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{coll_mesh}</uri>
          </mesh>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
"""
    with open(os.path.join(model_dir, 'model.sdf'), 'w') as f:
        f.write(sdf_content)

def export_model_meshes(model_name, visual_mesh, coll_mesh=None, desc="", material_xml=None):
    model_dir = os.path.join(MODELS_DIR, model_name)
    meshes_dir = os.path.join(model_dir, 'meshes')
    ensure_dir(meshes_dir)
    
    if coll_mesh is None:
        coll_mesh = visual_mesh
        
    _ = visual_mesh.vertex_normals
    _ = coll_mesh.vertex_normals
    
    visual_mesh.export(os.path.join(meshes_dir, 'visual.dae'))
    coll_mesh.export(os.path.join(meshes_dir, 'collision.stl'))
    
    write_model_config(model_dir, model_name, desc)
    write_sdf(model_dir, model_name, "visual.dae", "collision.stl", is_static=True, material_xml=material_xml)
    print(f"[{model_name}] created successfully.")

# ==============================================================================
# 1. UNEVEN MINEFIELD TERRAIN
# ==============================================================================
def get_terrain_elevation(x, y):
    if x < -2.0:
        return 0.0
    elif x < 1.0:
        t = (x + 2.0) / 3.0
        return t * (0.25 * math.sin(0.3 * y))
    else:
        # Base rolling hills
        h1 = 0.90 * math.sin(0.22 * x) * math.cos(0.25 * y)
        h2 = 0.40 * math.sin(0.55 * x + 1.2) * math.cos(0.48 * y - 0.7)
        h3 = 0.18 * math.sin(1.1 * x) * math.sin(0.95 * y)
        
        # Bomb craters
        c1 = -0.75 * math.exp(-(((x - 10.0)**2 + (y - 4.0)**2) / (2.6**2)))
        c2 = -0.80 * math.exp(-(((x - 18.0)**2 + (y + 8.0)**2) / (3.0**2)))
        c3 = -0.65 * math.exp(-(((x - 14.0)**2 + (y + 12.0)**2) / (2.2**2)))
        c4 = -0.85 * math.exp(-(((x - 22.0)**2 + (y - 3.0)**2) / (3.5**2)))
        
        # Dune / Trench feature
        dune = 0.35 * math.exp(-(((y - 2.5 * math.sin(0.25 * x))**2) / (3.0**2)))
        return h1 + h2 + h3 + c1 + c2 + c3 + c4 + dune

def generate_terrain():
    print("Generating uneven terrain mesh (60m x 60m)...")
    nx, ny = 120, 120
    x_vals = np.linspace(-30, 30, nx)
    y_vals = np.linspace(-30, 30, ny)
    X, Y = np.meshgrid(x_vals, y_vals)
    Z = np.zeros_like(X)
    for i in range(ny):
        for j in range(nx):
            Z[i, j] = get_terrain_elevation(X[i, j], Y[i, j])

    # Top surface vertices
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

    # Skirt vertices at z = -2.5m
    skirt_z = -2.5
    bottom_vertices = top_vertices.copy()
    bottom_vertices[:, 2] = skirt_z
    
    # Combined vertices
    all_vertices = np.vstack([top_vertices, bottom_vertices])
    all_faces = list(top_faces)
    
    # Bottom faces (reversed order)
    offset = nx * ny
    for f in top_faces:
        all_faces.append([f[0] + offset, f[2] + offset, f[1] + offset])
        
    # Edge skirts
    # North (i = ny-1)
    for j in range(nx - 1):
        i = ny - 1
        t1 = i * nx + j
        t2 = i * nx + (j + 1)
        b1 = t1 + offset
        b2 = t2 + offset
        all_faces.append([t1, b1, t2])
        all_faces.append([t2, b1, b2])
        
    # South (i = 0)
    for j in range(nx - 1):
        i = 0
        t1 = i * nx + j
        t2 = i * nx + (j + 1)
        b1 = t1 + offset
        b2 = t2 + offset
        all_faces.append([t1, t2, b1])
        all_faces.append([t2, b2, b1])
        
    # West (j = 0)
    for i in range(ny - 1):
        j = 0
        t1 = i * nx + j
        t2 = (i + 1) * nx + j
        b1 = t1 + offset
        b2 = t2 + offset
        all_faces.append([t1, b1, t2])
        all_faces.append([t2, b1, b2])

    # East (j = nx-1)
    for i in range(ny - 1):
        j = nx - 1
        t1 = i * nx + j
        t2 = (i + 1) * nx + j
        b1 = t1 + offset
        b2 = t2 + offset
        all_faces.append([t1, t2, b1])
        all_faces.append([t2, b2, b1])

    all_faces = np.array(all_faces)
    
    # Generate UV coordinates (tiled 12x across 60m terrain)
    u = (all_vertices[:, 0] + 30.0) / 60.0 * 12.0
    v = (all_vertices[:, 1] + 30.0) / 60.0 * 12.0
    uv = np.column_stack([u, v])
    tex_img = Image.open(f"{TEX_DIR}/desert_ground.png")
    
    terrain_mesh = trimesh.Trimesh(
        vertices=all_vertices,
        faces=all_faces,
        visual=trimesh.visual.TextureVisuals(uv=uv, image=tex_img),
        process=True
    )
    _ = terrain_mesh.vertex_normals
    
    mat_xml = f"""<material>
          <ambient>0.72 0.65 0.50 1</ambient>
          <diffuse>0.85 0.78 0.62 1</diffuse>
          <specular>0.1 0.1 0.1 1</specular>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/desert_ground.png</albedo_map>
              <roughness>0.9</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>"""
    export_model_meshes("uneven_minefield_terrain", terrain_mesh, desc="60m x 60m terrain with level camp and uneven bomb minefield", material_xml=mat_xml)

generate_terrain()
