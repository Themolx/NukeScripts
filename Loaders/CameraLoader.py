# Camera Loader and Updater for Nuke
#
# This script automatically loads or updates the camera for the current shot.
# It extracts shot information from the script name, finds the latest camera file,
# and either updates an existing CameraHERO node or creates a new one.
# The script uses the 'suppress_dialog' knob to prevent confirmation prompts.

import nuke
import os
import re

def debug_print(message):
    print(f"DEBUG: {message}")

def get_shot_info():
    script_name = nuke.root().name()
    debug_print(f"Script name: {script_name}")
    
    match = re.search(r'SQ(\d{4}).*?SH(\d{4})', script_name)
    
    if match:
        sequence = f"SQ{match.group(1)}"
        shot = f"SH{match.group(2)}"
        debug_print(f"Extracted sequence: {sequence}, shot: {shot}")
        return sequence, shot
    else:
        debug_print("Failed to extract sequence and shot from script name")
        return None, None

def get_latest_camera_file(base_path, sequence, shot):
    camera_path = os.path.join(base_path, sequence, shot, "animation", "camera")
    camera_path = camera_path.replace('\\', '/')
    debug_print(f"Searching for camera files in: {camera_path}")
    
    if not os.path.exists(camera_path):
        debug_print(f"Camera path does not exist: {camera_path}")
        return None
    
    camera_files = [f for f in os.listdir(camera_path) if f.endswith(".abc") and "anim.cam" in f]
    debug_print(f"Found camera files: {camera_files}")
    
    if not camera_files:
        debug_print("No matching camera files found")
        return None
    
    camera_files.sort(key=lambda x: int(re.search(r'v(\d+)', x).group(1)), reverse=True)
    latest_file = os.path.join(camera_path, camera_files[0]).replace('\\', '/')
    debug_print(f"Latest camera file: {latest_file}")
    
    return latest_file

def find_camera_node():
    for node in nuke.allNodes('Camera2'):
        if node.name().lower().startswith('camerahero'):
            debug_print(f"Found existing camera node: {node.name()}")
            return node
    debug_print("No existing CameraHERO node found")
    return None

def create_backdrop(node):
    backdrop = nuke.nodes.BackdropNode(
        xpos = node.xpos() - 10,
        ypos = node.ypos() - 80,
        bdwidth = 230,
        bdheight = node.screenHeight() + 160,
        tile_color = 0xaaaaaa00,
        note_font_size = 42,
        label = "CAMERA HERO\n"
    )
    return backdrop

def load_or_update_camera():
    base_path = "Y:/20105_Pysna_film/out/FILM"
    debug_print(f"Base path: {base_path}")
    
    sequence, shot = get_shot_info()
    
    if not sequence or not shot:
        nuke.message("Unable to determine sequence and shot numbers from the script name.")
        return
    
    latest_camera_file = get_latest_camera_file(base_path, sequence, shot)
    if not latest_camera_file:
        nuke.message(f"No camera file found for {sequence} {shot}.")
        return
    
    existing_camera = find_camera_node()
    if existing_camera:
        existing_camera['suppress_dialog'].setValue(True)
        existing_camera['file'].setValue(latest_camera_file)
        existing_camera['read_from_file'].setValue(True)
        debug_print(f"Updated {existing_camera.name()} with file: {latest_camera_file}")
        nuke.message(f"Updated {existing_camera.name()} with file: {latest_camera_file}")
    else:
        camera = nuke.createNode("Camera2", 'suppress_dialog True', inpanel=False)
        camera['file'].setValue(latest_camera_file)
        camera['name'].setValue("CameraHERO1")
        camera['read_from_file'].setValue(True)
        camera['focal'].setValue(40)
        camera['haperture'].setValue(48.00600052)
        camera['vaperture'].setValue(25.39999962)
        camera['near'].setValue(2)
        camera['far'].setValue(5000000)
        camera['focal_point'].setValue(5)
        camera['fstop'].setValue(5.599999905)
        
        backdrop = create_backdrop(camera)
        
        debug_print(f"Created new CameraHERO1 with file: {latest_camera_file}")
        nuke.message(f"Created new CameraHERO1 with file: {latest_camera_file}")

def run_script():
    with nuke.root():
        load_or_update_camera()

# Run the script
run_script()
