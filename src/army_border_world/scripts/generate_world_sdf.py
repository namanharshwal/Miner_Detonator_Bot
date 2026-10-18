import os
import math
import yaml

BASE_DIR = '/home/nammy/army_mine_bot/src/army_border_world'
WORLDS_DIR = os.path.join(BASE_DIR, 'worlds')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

def get_terrain_elevation(x, y):
    if x < -2.0:
        return 0.0
    elif x < 1.0:
        t = (x + 2.0) / 3.0
        return t * (0.25 * math.sin(0.3 * y))
    else:
        # Base rolling hills across the expanded minefield
        h1 = 1.10 * math.sin(0.18 * x) * math.cos(0.20 * y)
        h2 = 0.55 * math.sin(0.42 * x + 1.2) * math.cos(0.35 * y - 0.7)
        h3 = 0.25 * math.sin(0.85 * x) * math.sin(0.75 * y)
        
        # Bomb craters distributed across the field
        c1 = -1.10 * math.exp(-(((x - 10.0)**2 + (y - 4.0)**2) / (3.2**2)))
        c2 = -1.25 * math.exp(-(((x - 18.0)**2 + (y + 12.0)**2) / (3.8**2)))
        c3 = -0.95 * math.exp(-(((x - 14.0)**2 + (y - 18.0)**2) / (2.8**2)))
        c4 = -1.30 * math.exp(-(((x - 26.0)**2 + (y - 6.0)**2) / (4.2**2)))
        c5 = -1.40 * math.exp(-(((x - 38.0)**2 + (y + 8.0)**2) / (4.5**2)))
        c6 = -1.15 * math.exp(-(((x - 45.0)**2 + (y - 20.0)**2) / (3.6**2)))
        c7 = -1.50 * math.exp(-(((x - 56.0)**2 + (y + 2.0)**2) / (5.0**2)))
        c8 = -1.20 * math.exp(-(((x - 62.0)**2 + (y - 15.0)**2) / (4.0**2)))
        
        # Undulating dune and trenches
        dune1 = 0.45 * math.exp(-(((y - 4.0 * math.sin(0.15 * x))**2) / (5.0**2)))
        dune2 = 0.35 * math.exp(-(((y + 16.0 + 3.0 * math.cos(0.12 * x))**2) / (6.0**2)))
        
        return h1 + h2 + h3 + c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + dune1 + dune2

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

# Comprehensive registry of 28 bomb mines across the expanded terrain
mines_data = [
    # Anti-tank mines
    {"id": "mine_at_01", "type": "anti_tank", "x": 4.5, "y": 1.5, "notes": "Near border path entrance"},
    {"id": "mine_at_02", "type": "anti_tank", "x": 6.5, "y": -4.0, "notes": "Gentle slope area"},
    {"id": "mine_at_03", "type": "anti_tank", "x": 9.5, "y": 4.2, "notes": "Edge of Crater 1"},
    {"id": "mine_at_04", "type": "anti_tank", "x": 10.2, "y": 3.8, "notes": "Inside Crater 1 blast pit"},
    {"id": "mine_at_05", "type": "anti_tank", "x": 13.5, "y": -2.0, "notes": "Crest of central hill"},
    {"id": "mine_at_06", "type": "anti_tank", "x": 17.5, "y": 12.0, "notes": "Near Crater 2 blast ridge"},
    {"id": "mine_at_07", "type": "anti_tank", "x": 18.2, "y": 11.8, "notes": "Deep inside Crater 2"},
    {"id": "mine_at_08", "type": "anti_tank", "x": 22.5, "y": 2.5, "notes": "East dune incline"},
    {"id": "mine_at_09", "type": "anti_tank", "x": 26.2, "y": -6.0, "notes": "Inside deep Crater 4"},
    {"id": "mine_at_10", "type": "anti_tank", "x": 30.5, "y": 14.0, "notes": "Mid-field rocky mound"},
    {"id": "mine_at_11", "type": "anti_tank", "x": 38.0, "y": 8.0, "notes": "Deep inside Crater 5"},
    {"id": "mine_at_12", "type": "anti_tank", "x": 44.5, "y": -19.5, "notes": "Inside Crater 6 depression"},
    {"id": "mine_at_13", "type": "anti_tank", "x": 55.8, "y": 2.2, "notes": "Deep inside massive Crater 7"},
    {"id": "mine_at_14", "type": "anti_tank", "x": 64.0, "y": 10.0, "notes": "Far eastern border perimeter"},

    # Anti-personnel mines
    {"id": "mine_ap_01", "type": "anti_personnel", "x": 3.5, "y": 6.0, "notes": "Border sector north"},
    {"id": "mine_ap_02", "type": "anti_personnel", "x": 5.0, "y": -8.5, "notes": "Border sector south"},
    {"id": "mine_ap_03", "type": "anti_personnel", "x": 8.0, "y": -2.0, "notes": "Near rock outcrop"},
    {"id": "mine_ap_04", "type": "anti_personnel", "x": 11.5, "y": 14.0, "notes": "North hill incline"},
    {"id": "mine_ap_05", "type": "anti_personnel", "x": 14.0, "y": -17.5, "notes": "Edge of Crater 3"},
    {"id": "mine_ap_06", "type": "anti_personnel", "x": 16.5, "y": -10.0, "notes": "Southern uneven gully"},
    {"id": "mine_ap_07", "type": "anti_personnel", "x": 20.0, "y": -18.0, "notes": "South-east rocky mound"},
    {"id": "mine_ap_08", "type": "anti_personnel", "x": 24.0, "y": 18.0, "notes": "North-east hill crest"},
    {"id": "mine_ap_09", "type": "anti_personnel", "x": 28.0, "y": -12.0, "notes": "Mid-field gully"},
    {"id": "mine_ap_10", "type": "anti_personnel", "x": 35.0, "y": -4.0, "notes": "Central saddle depression"},
    {"id": "mine_ap_11", "type": "anti_personnel", "x": 42.0, "y": 16.0, "notes": "Northern high mound"},
    {"id": "mine_ap_12", "type": "anti_personnel", "x": 49.0, "y": -8.0, "notes": "East rolling slope"},
    {"id": "mine_ap_13", "type": "anti_personnel", "x": 58.0, "y": -18.0, "notes": "Far south-east boundary"},
    {"id": "mine_ap_14", "type": "anti_personnel", "x": 66.0, "y": -5.0, "notes": "Far perimeter border ridge"}
]

mines_yaml_records = []
for m in mines_data:
    z = get_terrain_elevation(m["x"], m["y"])
    roll, pitch = get_roll_pitch(m["x"], m["y"])
    m["z"] = round(z, 3)
    m["roll"] = round(roll, 3)
    m["pitch"] = round(pitch, 3)
    m["yaw"] = round(math.atan2(m["y"], m["x"]), 3)
    m["status"] = "armed"
    m["defused"] = False
    mines_yaml_records.append(m)

os.makedirs(CONFIG_DIR, exist_ok=True)
with open(os.path.join(CONFIG_DIR, 'mine_field_coordinates.yaml'), 'w') as f:
    yaml.dump({"mines": mines_yaml_records}, f, sort_keys=False)

rocks_data = [
    {"x": 6.5, "y": 6.5, "yaw": 0.4},
    {"x": 8.0, "y": -11.0, "yaw": 1.2},
    {"x": 12.5, "y": -3.5, "yaw": 2.1},
    {"x": 16.0, "y": 18.0, "yaw": -0.8},
    {"x": 22.0, "y": 8.0, "yaw": 1.7},
    {"x": 27.5, "y": -20.0, "yaw": -1.4},
    {"x": 34.0, "y": 12.0, "yaw": 0.9},
    {"x": 40.0, "y": -15.0, "yaw": 2.4},
    {"x": 48.0, "y": 6.0, "yaw": -1.1},
    {"x": 54.0, "y": -10.0, "yaw": 0.6},
    {"x": 63.0, "y": 15.0, "yaw": 1.8}
]

def include_model(name, model_dir_name, x, y, z, roll=0.0, pitch=0.0, yaw=0.0, is_static=True):
    return f"""
    <!-- {name} -->
    <include>
      <name>{name}</name>
      <uri>model://{model_dir_name}</uri>
      <pose>{x:.3f} {y:.3f} {z:.3f} {roll:.3f} {pitch:.3f} {yaw:.3f}</pose>
      <static>{str(is_static).lower()}</static>
    </include>"""

world_models_xml = []

# 1. Expanded Uneven Terrain (140m x 110m)
world_models_xml.append(include_model("border_terrain", "uneven_minefield_terrain", 0, 0, 0))

# ==============================================================================
# 2. ARMY CAMP - VEHICLES (TANKS & TRUCKS)
# ==============================================================================
# Main Battle Tanks in tactical defensive bays
world_models_xml.append(include_model("army_tank_1", "army_tank", -26.0, 18.0, 0.0, yaw=0.0))
world_models_xml.append(include_model("army_tank_2", "army_tank", -26.0, -18.0, 0.0, yaw=0.0))
world_models_xml.append(include_model("army_tank_3", "army_tank", -36.0, 0.0, 0.0, yaw=0.0))

# Heavy 6x6 Military Tactical Cargo Trucks
world_models_xml.append(include_model("army_truck_1", "army_truck", -28.0, 8.5, 0.0, yaw=0.15))
world_models_xml.append(include_model("army_truck_2", "army_truck", -28.0, -8.5, 0.0, yaw=-0.15))

# Sentry soldiers standing guard at the vehicle staging area
world_models_xml.append(include_model("vehicle_sentry_north", "soldier_standing_sentry", -21.0, 14.0, 0.0, yaw=0.0))
world_models_xml.append(include_model("vehicle_sentry_south", "soldier_standing_sentry", -21.0, -14.0, 0.0, yaw=0.0))

# ==============================================================================
# 3. ARMY CAMP - COMMAND HQ, BARRACKS & COURTYARD
# ==============================================================================
# Command HQ Tent
world_models_xml.append(include_model("hq_command_tent", "army_command_tent", -16.0, 0.0, 0.0, yaw=0.0))
# Sitting soldier inside Command HQ tent at tactical planning table
world_models_xml.append(include_model("soldier_sitting_hq", "soldier_sitting", -15.2, 0.0, 0.0, yaw=3.14))

# Barracks Tents
world_models_xml.append(include_model("barracks_tent_north", "army_barracks_tent", -16.0, 10.0, 0.0, yaw=-0.15))
world_models_xml.append(include_model("barracks_tent_south", "army_barracks_tent", -16.0, -10.0, 0.0, yaw=0.15))

# Courtyard briefing bench with 2 seated soldiers in discussion
world_models_xml.append(include_model("soldiers_briefing_bench", "soldier_sitting_bench", -11.0, -5.0, 0.0, yaw=0.0))
world_models_xml.append(include_model("ammo_crate_courtyard", "military_ammo_crate", -9.0, -5.0, 0.0, yaw=0.0))
world_models_xml.append(include_model("soldier_sitting_courtyard", "soldier_sitting", -7.8, -5.0, 0.0, yaw=3.14))

# Soldiers resting bench outside North Barracks
world_models_xml.append(include_model("soldiers_resting_bench", "soldier_sitting_bench", -12.0, 10.0, 0.0, yaw=0.0))

# ==============================================================================
# 4. BORDER CHECKPOINT, OPERATOR & SENTRIES
# ==============================================================================
# Soldier Robot Operator holding Mobile Robot Remote Control Console
world_models_xml.append(include_model("soldier_robot_controller", "soldier_robot_operator", -3.5, 0.0, 0.0, yaw=0.0))

# *** ALL-TERRAIN AUTONOMOUS MOBILE ROBOT (AMR) WITH 4D LIDAR & DEFUSAL PROBE ***
# Placed in the camp staging lane facing the border gate and minefield
world_models_xml.append(include_model("army_mine_amr", "army_mine_amr", -5.5, 0.0, 0.05, yaw=0.0, is_static=False))

# Sentry Soldiers holding Assault Rifles at Checkpoint and Bunker
world_models_xml.append(include_model("checkpoint_sentry_north", "soldier_standing_sentry", -3.5, 3.8, 0.0, yaw=0.0))
world_models_xml.append(include_model("bunker_sentry_south", "soldier_standing_sentry", -3.0, -8.0, 0.0, yaw=0.0))

# Military Watchtowers with Sentry Soldiers on top platforms (3.6m elevation)
world_models_xml.append(include_model("camp_watchtower_north", "military_watchtower", -5.0, 20.0, 0.0, yaw=0.0))
world_models_xml.append(include_model("watchtower_sentry_north", "soldier_standing_sentry", -5.0, 20.0, 3.6, yaw=0.0))

world_models_xml.append(include_model("camp_watchtower_south", "military_watchtower", -5.0, -20.0, 0.0, yaw=0.0))
world_models_xml.append(include_model("watchtower_sentry_south", "soldier_standing_sentry", -5.0, -20.0, 3.6, yaw=0.0))

world_models_xml.append(include_model("camp_watchtower_rear", "military_watchtower", -46.0, 0.0, 0.0, yaw=0.0))
world_models_xml.append(include_model("watchtower_sentry_rear", "soldier_standing_sentry", -46.0, 0.0, 3.6, yaw=0.0))

# Fortifications: Sandbag bunker & walls
world_models_xml.append(include_model("sandbag_bunker_south", "sandbag_bunker", -3.0, -8.0, 0.0, yaw=0.0))
world_models_xml.append(include_model("sandbag_wall_gate_north", "sandbag_wall", -3.0, 4.5, 0.0, yaw=0.0))
world_models_xml.append(include_model("sandbag_wall_gate_south", "sandbag_wall", -3.0, -3.5, 0.0, yaw=0.0))
world_models_xml.append(include_model("sandbag_wall_hq_protect", "sandbag_wall", -12.0, 0.0, 0.0, yaw=1.57))

# ==============================================================================
# 5. LOGISTICS, COMMUNICATIONS & SUPPLIES
# ==============================================================================
world_models_xml.append(include_model("radio_comms_outpost", "military_radio_station", -38.0, -18.0, 0.0, yaw=0.4))
world_models_xml.append(include_model("fuel_drum_1", "military_fuel_drum", -39.5, -17.5, 0.0))
world_models_xml.append(include_model("fuel_drum_2", "military_fuel_drum", -39.5, -18.3, 0.0))
world_models_xml.append(include_model("fuel_drum_3", "military_fuel_drum", -39.0, -17.9, 0.0))
world_models_xml.append(include_model("fuel_drum_4", "military_fuel_drum", -33.5, -9.0, 0.0))
world_models_xml.append(include_model("fuel_drum_5", "military_fuel_drum", -33.5, 9.0, 0.0))

world_models_xml.append(include_model("ammo_crate_stack_1", "military_ammo_crate", -38.0, 18.0, 0.0))
world_models_xml.append(include_model("ammo_crate_stack_2", "military_ammo_crate", -38.0, 18.0, 0.4))
world_models_xml.append(include_model("ammo_crate_stack_3", "military_ammo_crate", -33.0, 17.5, 0.0))

# Camp Floodlights
world_models_xml.append(include_model("floodlight_north", "camp_floodlight", -4.5, 26.0, 0.0, yaw=-0.5))
world_models_xml.append(include_model("floodlight_south", "camp_floodlight", -4.5, -26.0, 0.0, yaw=0.5))
world_models_xml.append(include_model("floodlight_center", "camp_floodlight", -48.0, 0.0, 0.0, yaw=0.0))

# ==============================================================================
# 6. EXPANDED CAMP PERIMETER RAZOR WIRE FENCES
# ==============================================================================
# North Perimeter Fence (along y = 30.0)
for idx, x in enumerate(range(-50, -4, 4)):
    world_models_xml.append(include_model(f"fence_north_{idx}", "barbed_wire_fence", float(x), 30.0, 0.0))

# South Perimeter Fence (along y = -30.0)
for idx, x in enumerate(range(-50, -4, 4)):
    world_models_xml.append(include_model(f"fence_south_{idx}", "barbed_wire_fence", float(x), -30.0, 0.0))

# Rear Perimeter Fence (along x = -52.0)
for idx, y in enumerate(range(-28, 30, 4)):
    world_models_xml.append(include_model(f"fence_rear_{idx}", "barbed_wire_fence", -52.0, float(y), 0.0, yaw=1.57))

# ==============================================================================
# 7. BORDER DEMARCATION LINE & FORTIFICATIONS
# ==============================================================================
for idx, py in enumerate([-24.0, -16.0, -8.0, 8.0, 16.0, 24.0]):
    world_models_xml.append(include_model(f"border_post_{idx+1}", "border_boundary_post", 0.0, py, 0.0))

for idx, hy in enumerate([-18.0, -12.0, 12.0, 18.0]):
    world_models_xml.append(include_model(f"czech_hedgehog_{idx+1}", "czech_hedgehog", 0.0, hy, 0.0))

# Minefield Warning Signs along Border
world_models_xml.append(include_model("warning_sign_border_n2", "mine_warning_sign", 0.5, 22.0, 0.0, yaw=3.14))
world_models_xml.append(include_model("warning_sign_border_n", "mine_warning_sign", 0.5, 10.0, 0.0, yaw=3.14))
world_models_xml.append(include_model("warning_sign_gate_n", "mine_warning_sign", 0.5, 3.5, 0.0, yaw=3.14))
world_models_xml.append(include_model("warning_sign_gate_s", "mine_warning_sign", 0.5, -3.5, 0.0, yaw=3.14))
world_models_xml.append(include_model("warning_sign_border_s", "mine_warning_sign", 0.5, -10.0, 0.0, yaw=3.14))
world_models_xml.append(include_model("warning_sign_border_s2", "mine_warning_sign", 0.5, -22.0, 0.0, yaw=3.14))

# ==============================================================================
# 8. ROCKS & BOULDERS ON UNEVEN GROUND
# ==============================================================================
for idx, r in enumerate(rocks_data):
    rz = get_terrain_elevation(r["x"], r["y"])
    r_roll, r_pitch = get_roll_pitch(r["x"], r["y"])
    world_models_xml.append(include_model(
        f"boulder_{idx+1}", "rock_boulder", r["x"], r["y"], rz,
        roll=r_roll, pitch=r_pitch, yaw=r["yaw"]
    ))

for s_idx, (sx, sy) in enumerate([(8.0, 0.0), (16.0, 8.0), (22.0, -12.0), (36.0, 4.0), (52.0, -6.0)]):
    sz = get_terrain_elevation(sx, sy)
    s_roll, s_pitch = get_roll_pitch(sx, sy)
    world_models_xml.append(include_model(
        f"warning_sign_field_{s_idx+1}", "mine_warning_sign", sx, sy, sz,
        roll=s_roll, pitch=s_pitch, yaw=3.14
    ))

# ==============================================================================
# 9. ALL 28 BOMB MINES ON UNEVEN GROUND
# ==============================================================================
for m in mines_yaml_records:
    model_name = "landmine_anti_tank" if m["type"] == "anti_tank" else "landmine_anti_personnel"
    world_models_xml.append(include_model(
        m["id"], model_name, m["x"], m["y"], m["z"] + 0.015,
        roll=m["roll"], pitch=m["pitch"], yaw=m["yaw"]
    ))

models_block = "\n".join(world_models_xml)

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

    <!-- Native Infinite Atmospheric Sky -->
    <scene>
      <ambient>0.65 0.65 0.65 1.0</ambient>
      <background>0.5 0.7 0.9 1.0</background>
      <shadows>true</shadows>
      <sky></sky>
    </scene>
    
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 35 0 0 0</pose>
      <diffuse>0.92 0.88 0.78 1</diffuse>
      <specular>0.3 0.3 0.25 1</specular>
      <direction>-0.5 0.2 -0.85</direction>
    </light>

{models_block}

  </world>
</sdf>
"""

os.makedirs(WORLDS_DIR, exist_ok=True)
world_file_path = os.path.join(WORLDS_DIR, 'army_border_minefield.sdf')
with open(world_file_path, 'w') as f:
    f.write(world_sdf)

print(f"Master World SDF regenerated successfully at: {world_file_path}")
print(f"Total models included: {len(world_models_xml)}")
