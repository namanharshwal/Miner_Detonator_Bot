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
    <name>Army Mine Bot Simulator</name>
    <email>army_mine_bot@simulation.org</email>
  </author>
  <description>{desc}</description>
</model>
"""
    with open(os.path.join(model_dir, 'model.config'), 'w') as f:
        f.write(config_content)

print("Starting 3D model generation...")
