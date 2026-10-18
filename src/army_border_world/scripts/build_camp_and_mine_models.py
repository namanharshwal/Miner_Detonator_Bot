import os
import math
import numpy as np
import trimesh

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
# 2. SOLDIER SITTING & STANDING
# ==============================================================================
def create_soldier_mesh(sitting=True):
    parts = []
    
    # Boots
    if sitting:
        # Lower legs vertical, feet on ground
        # Left boot
        b_left = trimesh.creation.box([0.14, 0.24, 0.12])
        b_left.apply_translation([-0.12, 0.35, 0.06])
        # Right boot
        b_right = trimesh.creation.box([0.14, 0.24, 0.12])
        b_right.apply_translation([0.12, 0.35, 0.06])
        parts.extend([b_left, b_right])
        
        # Shins (lower legs)
        shin_l = trimesh.creation.cylinder(radius=0.06, height=0.36)
        shin_l.apply_translation([-0.12, 0.35, 0.26])
        shin_r = trimesh.creation.cylinder(radius=0.06, height=0.36)
        shin_r.apply_translation([0.12, 0.35, 0.26])
        parts.extend([shin_l, shin_r])
        
        # Thighs (horizontal forward from hip (y=0) to knee (y=0.35) at z=0.45)
        thigh_l = trimesh.creation.cylinder(radius=0.07, height=0.35)
        # rotate cylinder to lie along Y
        thigh_l.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [1, 0, 0]))
        thigh_l.apply_translation([-0.12, 0.18, 0.45])
        
        thigh_r = trimesh.creation.cylinder(radius=0.07, height=0.35)
        thigh_r.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [1, 0, 0]))
        thigh_r.apply_translation([0.12, 0.18, 0.45])
        parts.extend([thigh_l, thigh_r])
        
        # Pelvis / Hips
        pelvis = trimesh.creation.box([0.34, 0.26, 0.18])
        pelvis.apply_translation([0.0, 0.0, 0.46])
        parts.append(pelvis)
        
        # Torso / Tactical Plate Carrier
        torso = trimesh.creation.box([0.38, 0.24, 0.48])
        torso.apply_translation([0.0, 0.0, 0.74])
        # Front chest ammo pouches
        pouch = trimesh.creation.box([0.28, 0.08, 0.16])
        pouch.apply_translation([0.0, 0.14, 0.70])
        parts.extend([torso, pouch])
        
        # Arms (resting on thighs)
        # Upper arm
        uarm_l = trimesh.creation.cylinder(radius=0.05, height=0.28)
        uarm_l.apply_translation([-0.22, 0.04, 0.76])
        uarm_r = trimesh.creation.cylinder(radius=0.05, height=0.28)
        uarm_r.apply_translation([0.22, 0.04, 0.76])
        # Forearm extending along Y onto thighs
        farm_l = trimesh.creation.cylinder(radius=0.045, height=0.26)
        farm_l.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [1, 0, 0]))
        farm_l.apply_translation([-0.16, 0.20, 0.56])
        farm_r = trimesh.creation.cylinder(radius=0.045, height=0.26)
        farm_r.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [1, 0, 0]))
        farm_r.apply_translation([0.16, 0.20, 0.56])
        parts.extend([uarm_l, uarm_r, farm_l, farm_r])
        
        # Head & Tactical Combat Helmet
        head = trimesh.creation.icosphere(radius=0.10, subdivisions=2)
        head.apply_translation([0.0, 0.0, 1.05])
        # Helmet dome
        helmet = trimesh.creation.icosphere(radius=0.13, subdivisions=2)
        helmet.apply_translation([0.0, 0.0, 1.09])
        # Helmet brim / visor
        brim = trimesh.creation.box([0.24, 0.16, 0.04])
        brim.apply_translation([0.0, 0.08, 1.06])
        parts.extend([head, helmet, brim])
        
    else:
        # Standing Sentry Soldier
        # Boots
        b_left = trimesh.creation.box([0.14, 0.26, 0.14])
        b_left.apply_translation([-0.14, 0.0, 0.07])
        b_right = trimesh.creation.box([0.14, 0.26, 0.14])
        b_right.apply_translation([0.14, 0.0, 0.07])
        parts.extend([b_left, b_right])
        
        # Legs
        leg_l = trimesh.creation.cylinder(radius=0.07, height=0.76)
        leg_l.apply_translation([-0.14, 0.0, 0.48])
        leg_r = trimesh.creation.cylinder(radius=0.07, height=0.76)
        leg_r.apply_translation([0.14, 0.0, 0.48])
        parts.extend([leg_l, leg_r])
        
        # Pelvis & Torso
        pelvis = trimesh.creation.box([0.36, 0.24, 0.20])
        pelvis.apply_translation([0.0, 0.0, 0.92])
        torso = trimesh.creation.box([0.40, 0.26, 0.52])
        torso.apply_translation([0.0, 0.0, 1.24])
        pouch = trimesh.creation.box([0.30, 0.08, 0.18])
        pouch.apply_translation([0.0, 0.14, 1.20])
        parts.extend([pelvis, torso, pouch])
        
        # Arms holding rifle diagonally
        uarm_l = trimesh.creation.cylinder(radius=0.05, height=0.32)
        uarm_l.apply_translation([-0.24, 0.05, 1.26])
        uarm_r = trimesh.creation.cylinder(radius=0.05, height=0.32)
        uarm_r.apply_translation([0.24, 0.05, 1.26])
        # Service Rifle
        rifle_body = trimesh.creation.box([0.06, 0.65, 0.10])
        rifle_body.apply_transform(trimesh.transformations.rotation_matrix(-0.3, [0, 0, 1]))
        rifle_body.apply_translation([0.05, 0.22, 1.15])
        barrel = trimesh.creation.cylinder(radius=0.015, height=0.35)
        barrel.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2 - 0.3, [0, 0, 1]))
        barrel.apply_translation([0.15, 0.52, 1.18])
        parts.extend([uarm_l, uarm_r, rifle_body, barrel])
        
        # Head and Helmet
        head = trimesh.creation.icosphere(radius=0.10, subdivisions=2)
        head.apply_translation([0.0, 0.0, 1.58])
        helmet = trimesh.creation.icosphere(radius=0.13, subdivisions=2)
        helmet.apply_translation([0.0, 0.0, 1.62])
        brim = trimesh.creation.box([0.24, 0.16, 0.04])
        brim.apply_translation([0.0, 0.08, 1.59])
        parts.extend([head, helmet, brim])
        
    soldier = trimesh.util.concatenate(parts)
    return soldier

def generate_soldiers():
    print("Generating soldier models...")
    # Sitting soldier
    s_sit = create_soldier_mesh(sitting=True)
    # stool / crate to sit on
    stool = trimesh.creation.box([0.45, 0.45, 0.42])
    stool.apply_translation([0.0, 0.0, 0.21])
    s_sit_full = trimesh.util.concatenate([s_sit, stool])
    
    mat_sit = f"""<material>
          <ambient>0.4 0.45 0.35 1</ambient>
          <diffuse>0.6 0.7 0.5 1</diffuse>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/camo_military.png</albedo_map>
            </metal>
          </pbr>
        </material>"""
    export_model_meshes("soldier_sitting", s_sit_full, desc="Soldier in military camo uniform sitting on camp stool", material_xml=mat_sit)
    
    # Bench with 2 soldiers sitting
    bench_top = trimesh.creation.box([2.2, 0.45, 0.06])
    bench_top.apply_translation([0.0, 0.0, 0.42])
    leg1 = trimesh.creation.box([0.10, 0.42, 0.40])
    leg1.apply_translation([-0.95, 0.0, 0.20])
    leg2 = trimesh.creation.box([0.10, 0.42, 0.40])
    leg2.apply_translation([0.95, 0.0, 0.20])
    bench = trimesh.util.concatenate([bench_top, leg1, leg2])
    
    soldier_1 = create_soldier_mesh(sitting=True)
    soldier_1.apply_translation([-0.55, 0.0, 0.0])
    soldier_2 = create_soldier_mesh(sitting=True)
    soldier_2.apply_transform(trimesh.transformations.rotation_matrix(0.2, [0, 0, 1]))
    soldier_2.apply_translation([0.55, 0.0, 0.0])
    
    soldier_bench = trimesh.util.concatenate([bench, soldier_1, soldier_2])
    export_model_meshes("soldier_sitting_bench", soldier_bench, desc="Camp briefing bench with two soldiers sitting in camouflage", material_xml=mat_sit)
    
    # Standing Sentry Soldier
    s_stand = create_soldier_mesh(sitting=False)
    export_model_meshes("soldier_standing_sentry", s_stand, desc="Sentry soldier in full combat gear standing alert with rifle", material_xml=mat_sit)

generate_soldiers()

# ==============================================================================
# 3. MILITARY TENTS (HQ & BARRACKS)
# ==============================================================================
def generate_tents():
    print("Generating army tents...")
    # Command Tent (6.0m x 4.5m, peak 2.8m, walls 1.8m)
    # Roof slope
    L, W, H_wall, H_peak = 6.0, 4.5, 1.8, 2.8
    parts = []
    
    # Roof panels (left and right slopes)
    hyp = math.sqrt((W/2)**2 + (H_peak - H_wall)**2)
    angle = math.atan2(H_peak - H_wall, W/2)
    
    r_left = trimesh.creation.box([L, hyp, 0.04])
    r_left.apply_transform(trimesh.transformations.rotation_matrix(angle, [1, 0, 0]))
    r_left.apply_translation([0.0, -W/4, (H_peak + H_wall)/2])
    
    r_right = trimesh.creation.box([L, hyp, 0.04])
    r_right.apply_transform(trimesh.transformations.rotation_matrix(-angle, [1, 0, 0]))
    r_right.apply_translation([0.0, W/4, (H_peak + H_wall)/2])
    parts.extend([r_left, r_right])
    
    # Side walls
    wall_left = trimesh.creation.box([L, 0.04, H_wall])
    wall_left.apply_translation([0.0, -W/2, H_wall/2])
    wall_right = trimesh.creation.box([L, 0.04, H_wall])
    wall_right.apply_translation([0.0, W/2, H_wall/2])
    parts.extend([wall_left, wall_right])
    
    # Back wall
    back_wall = trimesh.creation.box([0.04, W, H_wall])
    back_wall.apply_translation([-L/2, 0.0, H_wall/2])
    # Back gable triangle
    g_pts = np.array([
        [-L/2, -W/2, H_wall],
        [-L/2, W/2, H_wall],
        [-L/2, 0.0, H_peak]
    ])
    back_gable = trimesh.Trimesh(vertices=g_pts, faces=[[0, 1, 2], [0, 2, 1]])
    parts.extend([back_wall, back_gable])
    
    # Front entrance with opening flap
    front_l = trimesh.creation.box([0.04, W*0.3, H_wall])
    front_l.apply_translation([L/2, -W*0.35, H_wall/2])
    front_r = trimesh.creation.box([0.04, W*0.3, H_wall])
    front_r.apply_translation([L/2, W*0.35, H_wall/2])
    # Front gable
    fg_pts = np.array([
        [L/2, -W/2, H_wall],
        [L/2, W/2, H_wall],
        [L/2, 0.0, H_peak]
    ])
    front_gable = trimesh.Trimesh(vertices=fg_pts, faces=[[0, 1, 2], [0, 2, 1]])
    parts.extend([front_l, front_r, front_gable])
    
    # Support poles
    for x in [-L/2 + 0.1, 0.0, L/2 - 0.1]:
        pole = trimesh.creation.cylinder(radius=0.04, height=H_peak)
        pole.apply_translation([x, 0.0, H_peak/2])
        parts.append(pole)
        
    # Interior tactical table inside HQ tent
    table_top = trimesh.creation.box([2.2, 1.2, 0.08])
    table_top.apply_translation([0.0, 0.0, 0.75])
    t_leg1 = trimesh.creation.box([0.08, 0.08, 0.72])
    t_leg1.apply_translation([-0.95, -0.45, 0.36])
    t_leg2 = trimesh.creation.box([0.08, 0.08, 0.72])
    t_leg2.apply_translation([0.95, -0.45, 0.36])
    t_leg3 = trimesh.creation.box([0.08, 0.08, 0.72])
    t_leg3.apply_translation([-0.95, 0.45, 0.36])
    t_leg4 = trimesh.creation.box([0.08, 0.08, 0.72])
    t_leg4.apply_translation([0.95, 0.45, 0.36])
    parts.extend([table_top, t_leg1, t_leg2, t_leg3, t_leg4])
    
    cmd_tent = trimesh.util.concatenate(parts)
    mat_camo = f"""<material>
          <ambient>0.45 0.5 0.4 1</ambient>
          <diffuse>0.65 0.75 0.55 1</diffuse>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/camo_military.png</albedo_map>
            </metal>
          </pbr>
        </material>"""
    export_model_meshes("army_command_tent", cmd_tent, desc="Military Command HQ Tent with tactical table and camo canvas", material_xml=mat_camo)
    
    # Barracks Tent (4.5m x 3.2m, closed flaps)
    Lb, Wb, Hwb, Hpb = 4.5, 3.2, 1.6, 2.4
    b_parts = []
    hyp_b = math.sqrt((Wb/2)**2 + (Hpb - Hwb)**2)
    ang_b = math.atan2(Hpb - Hwb, Wb/2)
    
    rb_left = trimesh.creation.box([Lb, hyp_b, 0.04])
    rb_left.apply_transform(trimesh.transformations.rotation_matrix(ang_b, [1, 0, 0]))
    rb_left.apply_translation([0.0, -Wb/4, (Hpb + Hwb)/2])
    
    rb_right = trimesh.creation.box([Lb, hyp_b, 0.04])
    rb_right.apply_transform(trimesh.transformations.rotation_matrix(-ang_b, [1, 0, 0]))
    rb_right.apply_translation([0.0, Wb/4, (Hpb + Hwb)/2])
    
    wb_l = trimesh.creation.box([Lb, 0.04, Hwb])
    wb_l.apply_translation([0.0, -Wb/2, Hwb/2])
    wb_r = trimesh.creation.box([Lb, 0.04, Hwb])
    wb_r.apply_translation([0.0, Wb/2, Hwb/2])
    
    wb_back = trimesh.creation.box([0.04, Wb, Hwb])
    wb_back.apply_translation([-Lb/2, 0.0, Hwb/2])
    wb_front = trimesh.creation.box([0.04, Wb, Hwb])
    wb_front.apply_translation([Lb/2, 0.0, Hwb/2])
    
    b_parts.extend([rb_left, rb_right, wb_l, wb_r, wb_back, wb_front])
    barracks = trimesh.util.concatenate(b_parts)
    export_model_meshes("army_barracks_tent", barracks, desc="Military Barracks Tent for soldiers resting", material_xml=mat_camo)

# ==============================================================================
# 4. MILITARY WATCHTOWER
# ==============================================================================
def generate_watchtower():
    print("Generating military watchtower...")
    parts = []
    # 4 corner columns (height 3.6m to deck, then to 5.4m roof)
    H_deck = 3.6
    H_roof = 5.4
    R = 1.3 # half width
    
    for dx in [-R, R]:
        for dy in [-R, R]:
            # Lower post
            post = trimesh.creation.cylinder(radius=0.08, height=H_deck)
            post.apply_translation([dx, dy, H_deck/2])
            # Upper post
            upost = trimesh.creation.cylinder(radius=0.06, height=H_roof - H_deck)
            upost.apply_translation([dx, dy, H_deck + (H_roof - H_deck)/2])
            parts.extend([post, upost])
            
    # Observation platform deck
    deck = trimesh.creation.box([2.8, 2.8, 0.12])
    deck.apply_translation([0.0, 0.0, H_deck])
    parts.append(deck)
    
    # Deck safety handrails
    for angle, side_pos in [(0, [0.0, -1.35]), (0, [0.0, 1.35]), (math.pi/2, [-1.35, 0.0]), (math.pi/2, [1.35, 0.0])]:
        rail = trimesh.creation.box([2.7, 0.06, 0.06])
        rail.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 0, 1]))
        rail.apply_translation([side_pos[0], side_pos[1], H_deck + 1.0])
        parts.append(rail)
        
    # Canopy roof on top
    roof = trimesh.creation.box([3.2, 3.2, 0.08])
    roof.apply_transform(trimesh.transformations.rotation_matrix(0.08, [1, 0, 0])) # slight slope
    roof.apply_translation([0.0, 0.0, H_roof])
    parts.append(roof)
    
    # Access ladder on rear side (x = -R)
    ladder_rail_l = trimesh.creation.cylinder(radius=0.03, height=H_deck)
    ladder_rail_l.apply_translation([-R - 0.1, -0.3, H_deck/2])
    ladder_rail_r = trimesh.creation.cylinder(radius=0.03, height=H_deck)
    ladder_rail_r.apply_translation([-R - 0.1, 0.3, H_deck/2])
    parts.extend([ladder_rail_l, ladder_rail_r])
    for z_step in np.linspace(0.3, H_deck - 0.2, 10):
        rung = trimesh.creation.cylinder(radius=0.02, height=0.6)
        rung.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [1, 0, 0]))
        rung.apply_translation([-R - 0.1, 0.0, z_step])
        parts.append(rung)
        
    # Searchlight on front railing
    light_box = trimesh.creation.box([0.3, 0.4, 0.3])
    light_box.apply_translation([R, 0.0, H_deck + 1.1])
    lens = trimesh.creation.cylinder(radius=0.15, height=0.05)
    lens.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [0, 1, 0]))
    lens.apply_translation([R + 0.16, 0.0, H_deck + 1.1])
    parts.extend([light_box, lens])
    
    tower = trimesh.util.concatenate(parts)
    mat_metal = f"""<material>
          <ambient>0.3 0.3 0.3 1</ambient>
          <diffuse>0.5 0.5 0.5 1</diffuse>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/rusty_metal.png</albedo_map>
            </metal>
          </pbr>
        </material>"""
    export_model_meshes("military_watchtower", tower, desc="Military Watchtower with platform deck, ladder, and searchlight", material_xml=mat_metal)

# ==============================================================================
# 5. SANDBAG BUNKERS & WALLS
# ==============================================================================
def create_single_sandbag(length=0.55, width=0.28, height=0.15):
    # Rounded box shape for sandbag
    sb = trimesh.creation.box([length, width, height])
    return sb

def generate_sandbag_fortifications():
    print("Generating sandbag fortifications...")
    mat_burlap = f"""<material>
          <ambient>0.6 0.5 0.4 1</ambient>
          <diffuse>0.75 0.65 0.5 1</diffuse>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/sandbag_burlap.png</albedo_map>
            </metal>
          </pbr>
        </material>"""
        
    # 1. Straight Sandbag Wall (3m long, 0.85m high)
    wall_parts = []
    tiers = 6
    L_bag, W_bag, H_bag = 0.55, 0.30, 0.14
    for tier in range(tiers):
        z = (tier + 0.5) * H_bag
        n_bags = 5 if (tier % 2 == 0) else 6
        x_start = -1.2 + (0.15 if tier % 2 == 1 else 0.0)
        for b in range(n_bags):
            x = x_start + b * 0.52
            bag = create_single_sandbag(L_bag, W_bag, H_bag)
            bag.apply_translation([x, 0.0, z])
            wall_parts.append(bag)
    sb_wall = trimesh.util.concatenate(wall_parts)
    export_model_meshes("sandbag_wall", sb_wall, desc="Defensive straight sandbag wall", material_xml=mat_burlap)
    
    # 2. Curved Sandbag Bunker (U-shaped facing minefield)
    bunker_parts = []
    radius = 1.4
    n_tiers = 7
    for tier in range(n_tiers):
        z = (tier + 0.5) * H_bag
        # arc from -90 to +90 degrees
        n_arc = 9
        angles = np.linspace(-math.pi/2, math.pi/2, n_arc)
        if tier % 2 == 1:
            angles += 0.1
        for ang in angles:
            # Leave firing port notch in top tier in center
            if tier >= 5 and abs(ang) < 0.25:
                continue
            x = radius * math.cos(ang)
            y = radius * math.sin(ang)
            bag = create_single_sandbag(L_bag, W_bag, H_bag)
            bag.apply_transform(trimesh.transformations.rotation_matrix(ang, [0, 0, 1]))
            bag.apply_translation([x, y, z])
            bunker_parts.append(bag)
    sb_bunker = trimesh.util.concatenate(bunker_parts)
    export_model_meshes("sandbag_bunker", sb_bunker, desc="Curved military sandbag bunker emplacement with firing notch", material_xml=mat_burlap)

generate_tents()
generate_watchtower()
generate_sandbag_fortifications()

# ==============================================================================
# 6. BORDER OBSTACLES: CZECH HEDGEHOG & BARBED WIRE FENCE
# ==============================================================================
def generate_border_obstacles():
    print("Generating border obstacles...")
    mat_metal = f"""<material>
          <ambient>0.35 0.35 0.35 1</ambient>
          <diffuse>0.5 0.5 0.5 1</diffuse>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/rusty_metal.png</albedo_map>
            </metal>
          </pbr>
        </material>"""
        
    # Czech Hedgehog: 3 intersecting crossed steel I-beams (length 1.4m)
    L_beam = 1.4
    b1 = trimesh.creation.box([L_beam, 0.14, 0.14])
    b2 = trimesh.creation.box([0.14, L_beam, 0.14])
    b3 = trimesh.creation.box([0.14, 0.14, L_beam])
    hedgehog = trimesh.util.concatenate([b1, b2, b3])
    # Tilt slightly so it rests on 3 points on the ground
    hedgehog.apply_transform(trimesh.transformations.rotation_matrix(math.pi/4, [1, 1, 0]))
    # elevate so base is at z = 0
    min_z = hedgehog.bounds[0, 2]
    hedgehog.apply_translation([0, 0, -min_z])
    export_model_meshes("czech_hedgehog", hedgehog, desc="Anti-tank Czech hedgehog steel obstacle", material_xml=mat_metal)
    
    # Barbed Wire Fence: 3 posts (length 3m span, height 1.8m) with horizontal wires & coiled wire
    f_parts = []
    for px in [-1.4, 0.0, 1.4]:
        post = trimesh.creation.cylinder(radius=0.04, height=1.8)
        post.apply_translation([px, 0.0, 0.9])
        f_parts.append(post)
    # Horizontal wires
    for wz in [0.3, 0.7, 1.1, 1.5, 1.75]:
        wire = trimesh.creation.cylinder(radius=0.012, height=3.0)
        wire.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [0, 1, 0]))
        wire.apply_translation([0.0, 0.0, wz])
        f_parts.append(wire)
    # Concertina razor wire cylinder coil representation
    coil1 = trimesh.creation.cylinder(radius=0.35, height=2.9)
    coil1.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [0, 1, 0]))
    coil1.apply_translation([0.0, 0.0, 0.5])
    coil2 = trimesh.creation.cylinder(radius=0.35, height=2.9)
    coil2.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [0, 1, 0]))
    coil2.apply_translation([0.0, 0.0, 1.3])
    f_parts.extend([coil1, coil2])
    
    fence = trimesh.util.concatenate(f_parts)
    export_model_meshes("barbed_wire_fence", fence, desc="Military border razor wire security fence", material_xml=mat_metal)

# ==============================================================================
# 7. BORDER POST & MINE WARNING SIGN
# ==============================================================================
def generate_signs_and_posts():
    print("Generating border post and warning signs...")
    # Border boundary post
    base = trimesh.creation.box([0.5, 0.5, 0.2])
    base.apply_translation([0.0, 0.0, 0.1])
    pillar = trimesh.creation.box([0.3, 0.3, 1.6])
    pillar.apply_translation([0.0, 0.0, 1.0])
    pyramid_top = trimesh.creation.cone(radius=0.22, height=0.3)
    pyramid_top.apply_translation([0.0, 0.0, 1.8 + 0.15])
    bpost = trimesh.util.concatenate([base, pillar, pyramid_top])
    mat_border = f"""<material>
          <ambient>0.7 0.7 0.7 1</ambient>
          <diffuse>0.85 0.85 0.85 1</diffuse>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/border_stripes.png</albedo_map>
            </metal>
          </pbr>
        </material>"""
    export_model_meshes("border_boundary_post", bpost, desc="Official international border marker post with warning stripes", material_xml=mat_border)
    
    # Mine Warning Sign
    s_parts = []
    # Wooden/steel post
    spost = trimesh.creation.cylinder(radius=0.03, height=1.3)
    spost.apply_translation([0.0, 0.0, 0.65])
    # Triangular sign plate
    tri_sign = trimesh.creation.box([0.55, 0.03, 0.48])
    tri_sign.apply_translation([0.0, 0.03, 1.1])
    s_parts.extend([spost, tri_sign])
    warning_sign = trimesh.util.concatenate(s_parts)
    mat_sign = f"""<material>
          <ambient>0.8 0.7 0.1 1</ambient>
          <diffuse>0.95 0.85 0.2 1</diffuse>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/danger_mines_sign.png</albedo_map>
            </metal>
          </pbr>
        </material>"""
    export_model_meshes("mine_warning_sign", warning_sign, desc="High-visibility DANGER MINES warning sign with skull symbol", material_xml=mat_sign)

# ==============================================================================
# 8. BOMB MINES (LANDMINES: ANTI-TANK & ANTI-PERSONNEL)
# ==============================================================================
def generate_landmines():
    print("Generating landmines...")
    mat_mine = f"""<material>
          <ambient>0.4 0.45 0.35 1</ambient>
          <diffuse>0.6 0.7 0.5 1</diffuse>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/landmine_texture.png</albedo_map>
            </metal>
          </pbr>
        </material>"""
        
    # Anti-Tank Mine: heavy disc (dia 0.32m, height 0.09m)
    parts_at = []
    # Main outer body disc
    body_at = trimesh.creation.cylinder(radius=0.16, height=0.08)
    body_at.apply_translation([0.0, 0.0, 0.04])
    # Pressure plate on top
    plate_at = trimesh.creation.cylinder(radius=0.11, height=0.02)
    plate_at.apply_translation([0.0, 0.0, 0.09])
    # Detonator center fuse / active LED (red)
    det_at = trimesh.creation.cylinder(radius=0.035, height=0.02)
    det_at.apply_translation([0.0, 0.0, 0.105])
    # Side carry handle
    handle_at = trimesh.creation.box([0.04, 0.10, 0.02])
    handle_at.apply_translation([0.16, 0.0, 0.04])
    parts_at.extend([body_at, plate_at, det_at, handle_at])
    mine_at = trimesh.util.concatenate(parts_at)
    export_model_meshes("landmine_anti_tank", mine_at, desc="Heavy Anti-Tank landmine with pressure plate fuse and armed indicator", material_xml=mat_mine)
    
    # Anti-Personnel Blast Mine: compact cylinder (dia 0.14m, height 0.08m)
    parts_ap = []
    body_ap = trimesh.creation.cylinder(radius=0.07, height=0.07)
    body_ap.apply_translation([0.0, 0.0, 0.035])
    # Top prong switch / trigger
    trigger_ap = trimesh.creation.cylinder(radius=0.025, height=0.03)
    trigger_ap.apply_translation([0.0, 0.0, 0.08])
    for ang in [0, 2*math.pi/3, 4*math.pi/3]:
        prong = trimesh.creation.cylinder(radius=0.005, height=0.04)
        prong.apply_translation([0.04 * math.cos(ang), 0.04 * math.sin(ang), 0.09])
        parts_ap.append(prong)
    parts_ap.extend([body_ap, trigger_ap])
    mine_ap = trimesh.util.concatenate(parts_ap)
    export_model_meshes("landmine_anti_personnel", mine_ap, desc="Anti-personnel blast mine with trip prongs and central firing cap", material_xml=mat_mine)

# ==============================================================================
# 9. CAMP LOGISTICS: AMMO CRATES, FUEL DRUMS, RADIO STATION, FLOODLIGHT, ROCKS
# ==============================================================================
def generate_camp_accessories():
    print("Generating camp accessories & obstacles...")
    # Ammo Crate (0.8m x 0.5m x 0.4m)
    c_parts = []
    box_body = trimesh.creation.box([0.8, 0.5, 0.4])
    box_body.apply_translation([0.0, 0.0, 0.2])
    # Latches & ribs
    rib1 = trimesh.creation.box([0.82, 0.04, 0.42])
    rib1.apply_translation([0.0, -0.25, 0.2])
    rib2 = trimesh.creation.box([0.82, 0.04, 0.42])
    rib2.apply_translation([0.0, 0.25, 0.2])
    c_parts.extend([box_body, rib1, rib2])
    crate = trimesh.util.concatenate(c_parts)
    mat_crate = f"""<material>
          <ambient>0.5 0.5 0.4 1</ambient>
          <diffuse>0.65 0.65 0.5 1</diffuse>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/military_crate.png</albedo_map>
            </metal>
          </pbr>
        </material>"""
    export_model_meshes("military_ammo_crate", crate, desc="Military wooden ammo supply crate with stenciled explosive markings", material_xml=mat_crate)
    
    # Fuel Drum (200L, dia 0.6m, height 0.9m)
    d_parts = []
    drum_body = trimesh.creation.cylinder(radius=0.30, height=0.90)
    drum_body.apply_translation([0.0, 0.0, 0.45])
    # Rolling ribs
    rib_d1 = trimesh.creation.cylinder(radius=0.315, height=0.04)
    rib_d1.apply_translation([0.0, 0.0, 0.30])
    rib_d2 = trimesh.creation.cylinder(radius=0.315, height=0.04)
    rib_d2.apply_translation([0.0, 0.0, 0.60])
    d_parts.extend([drum_body, rib_d1, rib_d2])
    drum = trimesh.util.concatenate(d_parts)
    mat_drum = f"""<material>
          <ambient>0.35 0.4 0.3 1</ambient>
          <diffuse>0.5 0.6 0.45 1</diffuse>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/rusty_metal.png</albedo_map>
            </metal>
          </pbr>
        </material>"""
    export_model_meshes("military_fuel_drum", drum, desc="Standard 200L military olive-drab fuel barrel", material_xml=mat_drum)
    
    # Radio Station Outpost
    r_parts = []
    # Console base cabinet
    console = trimesh.creation.box([0.9, 0.6, 1.1])
    console.apply_translation([0.0, 0.0, 0.55])
    # Antenna mast (height 3.5m)
    mast = trimesh.creation.cylinder(radius=0.03, height=3.5)
    mast.apply_translation([-0.35, 0.0, 1.75])
    # Satellite dish
    dish = trimesh.creation.cone(radius=0.35, height=0.15)
    dish.apply_transform(trimesh.transformations.rotation_matrix(math.pi/3, [0, 1, 0]))
    dish.apply_translation([0.2, 0.0, 1.4])
    r_parts.extend([console, mast, dish])
    radio_stn = trimesh.util.concatenate(r_parts)
    export_model_meshes("military_radio_station", radio_stn, desc="Military outpost communications rack with antenna and dish", material_xml=mat_drum)
    
    # Camp Floodlight
    fl_parts = []
    pole = trimesh.creation.cylinder(radius=0.06, height=4.2)
    pole.apply_translation([0.0, 0.0, 2.1])
    lamp_bar = trimesh.creation.box([0.1, 0.8, 0.1])
    lamp_bar.apply_translation([0.0, 0.0, 4.2])
    head1 = trimesh.creation.box([0.3, 0.25, 0.2])
    head1.apply_translation([0.15, -0.3, 4.15])
    head2 = trimesh.creation.box([0.3, 0.25, 0.2])
    head2.apply_translation([0.15, 0.3, 4.15])
    fl_parts.extend([pole, lamp_bar, head1, head2])
    floodlight = trimesh.util.concatenate(fl_parts)
    export_model_meshes("camp_floodlight", floodlight, desc="Military base camp floodlight tower", material_xml=mat_drum)
    
    # Rock Boulder
    rock = trimesh.creation.icosphere(radius=0.6, subdivisions=1)
    # Distort vertices randomly to make natural irregular boulder
    np.random.seed(123)
    rock.vertices += np.random.uniform(-0.15, 0.15, rock.vertices.shape)
    # flatten bottom slightly
    rock.vertices[:, 2] = np.maximum(rock.vertices[:, 2], -0.3)
    min_rz = rock.bounds[0, 2]
    rock.apply_translation([0, 0, -min_rz])
    mat_rock = f"""<material>
          <ambient>0.5 0.45 0.4 1</ambient>
          <diffuse>0.7 0.65 0.6 1</diffuse>
          <pbr>
            <metal>
              <albedo_map>{TEX_DIR}/desert_ground.png</albedo_map>
            </metal>
          </pbr>
        </material>"""
    export_model_meshes("rock_boulder", rock, desc="Desert rock boulder obstacle on uneven terrain", material_xml=mat_rock)

generate_border_obstacles()
generate_signs_and_posts()
generate_landmines()
generate_camp_accessories()
