# NewCompShot.py
#
# This script creates a new composition shot by:
# 1. Setting up the project
# 2. Loading lighting renders with backdrops
# 3. Importing a template
# 4. Loading a workspace
# 5. Updating the camera
#
# It combines functionality from multiple scripts and includes all necessary functions.

import nuke
import os
import re
import nukescripts


def debug_print(message):
    print(f"DEBUG: {message}")

def print_step(step):
    print(f"\n{'=' * 50}\n{step}\n{'=' * 50}")

def setup_2k_dcp_project():
    print_step("Setting up 2K DCP project")
    root = nuke.root()
    format_knob = root['format']
    
    desired_width, desired_height = 2048, 1080
    desired_pixel_aspect = 1.0
    desired_name = "2K_DCP"
    
    existing_format = None
    for format in nuke.formats():
        if (format.width() == desired_width and
            format.height() == desired_height and
            format.pixelAspect() == desired_pixel_aspect and
            format.name() == desired_name):
            existing_format = format
            break
    
    if existing_format:
        print(f"2K DCP format already exists. Setting project to use it.")
        format_knob.setValue(desired_name)
    else:
        print(f"2K DCP format not found. Creating and setting it.")
        new_format = f"{desired_width} {desired_height} {desired_pixel_aspect} {desired_name}"
        nuke.addFormat(new_format)
        format_knob.setValue(desired_name)
    
    root['lock_range'].setValue(True)
    
    current_format = format_knob.value()
    print(f"Project Format: {current_format.name()} ({current_format.width()}x{current_format.height()}, PAR: {current_format.pixelAspect()})")
    print(f"Lock Range: {root['lock_range'].value()}")

def set_viewer_process_rec709_aces():
    print_step("Setting viewer process to Rec.709 (ACES)")
    viewer_process = "Rec.709 (ACES)"
    viewers_updated = 0

    viewer_nodes = nuke.allNodes('Viewer')
    if not viewer_nodes:
        print("No Viewer nodes found. Creating a new Viewer node.")
        new_viewer = nuke.createNode('Viewer')
        viewer_nodes.append(new_viewer)

    for node in viewer_nodes:
        if 'viewerProcess' in node.knobs():
            node['viewerProcess'].setValue(viewer_process)
            viewers_updated += 1
        if 'monitorOutOutputTransform' in node.knobs():
            node['monitorOutOutputTransform'].setValue(viewer_process)
    
    print(f"Updated {viewers_updated} Viewer node(s) to {viewer_process}")

def set_default_flipbook_lut():
    print_step("Setting default Flipbook LUT")
    nukescripts.setFlipbookDefaultOption("lut", "Rec.709 (ACES)")
    print("Flipbook LUT set to Rec.709 (ACES)")

def create_main_backdrop(nodes, seq_num, shot_num):
    if not nodes:
        return None
    bdX = min([node.xpos() for node in nodes])
    bdY = min([node.ypos() for node in nodes])
    bdW = max([node.xpos() + node.screenWidth() for node in nodes]) - bdX
    bdH = max([node.ypos() + node.screenHeight() for node in nodes]) - bdY

    backdrop = nuke.nodes.BackdropNode(
        xpos = bdX - 150,
        bdwidth = bdW + 300,
        ypos = bdY - 300,
        bdheight = bdH + 500,
        tile_color = int("0x7171C680", 16),
        note_font_size=42,
        label=f'<center>SQ{seq_num} SH{shot_num}\nLighting Renders'
    )
    return backdrop

def create_layer_backdrop(read_node, layer_name):
    padding = 60
    backdrop_label = re.sub(r'^SQ\d+_SH\d+_', '', layer_name)
    backdrop = nuke.nodes.BackdropNode(
        xpos = read_node.xpos() - padding - 50,
        ypos = read_node.ypos() - padding - 50,
        bdwidth = read_node.screenWidth() + padding * 2 + 50,
        bdheight = read_node.screenHeight() + padding * 2 + 50,
        tile_color = int("0xAAAACC80", 16),
        note_font_size=24,
        label=backdrop_label
    )
    return backdrop

def arrange_nodes(nodes):
    spacing = 350
    start_x = 0
    start_y = 0
    for i, node in enumerate(nodes):
        node.setXYpos(start_x + i * spacing, start_y)

def find_latest_version(path):
    versions = [d for d in os.listdir(path) if d.startswith('v') and os.path.isdir(os.path.join(path, d))]
    return max(versions) if versions else None

def find_all_render_layers(shot_path):
    print_step(f"Finding render layers in: {shot_path}")
    render_layers = {}
    
    version_folders = [d for d in os.listdir(shot_path) if d.startswith('v') and os.path.isdir(os.path.join(shot_path, d))]
    version_folders.sort(reverse=True)
    
    for version in version_folders:
        version_path = os.path.join(shot_path, version)
        for layer in os.listdir(version_path):
            layer_path = os.path.join(version_path, layer)
            if os.path.isdir(layer_path):
                render_files = [f for f in os.listdir(layer_path) if f.endswith('.exr')]
                if render_files and layer not in render_layers:
                    render_layers[layer] = {"version": version, "file": render_files[0], "path": layer_path}
    
    if not render_layers:
        for root, dirs, files in os.walk(shot_path):
            for dir in dirs:
                if dir.startswith("exr."):
                    layer_name = dir.split(".")[-1]
                    layer_path = os.path.join(root, dir)
                    version = find_latest_version(layer_path)
                    if version:
                        version_path = os.path.join(layer_path, version)
                        render_files = [f for f in os.listdir(version_path) if f.endswith('.exr')]
                        if render_files:
                            render_layers[layer_name] = {"version": version, "file": render_files[0], "path": version_path}
    
    print(f"Found {len(render_layers)} render layers")
    return render_layers

def load_latest_renders(shot_path, seq_num, shot_num):
    print_step(f"Loading latest renders from: {shot_path}")
    render_layers = find_all_render_layers(shot_path)
    frame_ranges = {}
    created_nodes = []

    for layer_name, render_info in render_layers.items():
        version = render_info["version"]
        latest_render = render_info["file"]
        render_path = os.path.join(render_info["path"], latest_render).replace("\\", "/")
        
        read_node = nuke.createNode("Read")
        read_node["file"].setValue(render_path.replace(latest_render.split(".")[-2], "######"))
        
        frame_files = [f for f in os.listdir(os.path.dirname(render_path)) if f.endswith('.exr')]
        frame_numbers = [int(re.search(r'(\d+)\.exr$', f).group(1)) for f in frame_files]
        first_frame, last_frame = min(frame_numbers), max(frame_numbers)
        
        read_node["first"].setValue(first_frame)
        read_node["last"].setValue(last_frame)
        read_node["origfirst"].setValue(first_frame)
        read_node["origlast"].setValue(last_frame)
        read_node["name"].setValue(f"Read_{layer_name}_{version}")
        read_node["label"].setValue(f"{layer_name}\n(v{version.split('v')[1]})")
        
        frame_ranges[layer_name] = (first_frame, last_frame)
        created_nodes.append(read_node)
        print(f"Created Read node for {layer_name}")

    arrange_nodes(created_nodes)
    main_backdrop = create_main_backdrop(created_nodes, seq_num, shot_num)
    
    layer_backdrops = []
    for node in created_nodes:
        layer_name = node['label'].value().split('\n')[0]
        backdrop = create_layer_backdrop(node, layer_name)
        layer_backdrops.append(backdrop)
    
    for node, backdrop in zip(created_nodes, layer_backdrops):
        node.setXYpos(backdrop.xpos() + 50, backdrop.ypos() + 50)

    print(f"Total created nodes: {len(created_nodes)}")
    return created_nodes, frame_ranges

def import_template():
    print_step("Importing template")
    template_path = "Y:/20105_Pysna_film/tmp/martin.tomek/templates/TemplateStamps.nk"
    if os.path.exists(template_path):
        nuke.nodePaste(template_path)
        print(f"Template imported from: {template_path}")
    else:
        print(f"Template file not found: {template_path}")


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


def get_backdrop_coordinates(label_text):
    print_step(f"Finding backdrop coordinates for label containing '{label_text}'")
    nodes = nuke.allNodes('BackdropNode')
    
    for node in nodes:
        if label_text in node['label'].value():
            x = node['xpos'].value()
            y = node['ypos'].value()
            print(f"Found backdrop with coordinates: X={x}, Y={y}")
            return (x, y)
    
    print(f"No backdrop node with '{label_text}' in the label found.")
    return None

def create_new_comp_shot():
    print_step("Creating new composition shot")
    
    # Step 1: Set up the project
    setup_2k_dcp_project()
    set_viewer_process_rec709_aces()
    set_default_flipbook_lut()
    
    # Step 2: Load lighting renders
    sequence, shot = get_shot_info()
    if sequence and shot:
        shot_path = f"Y:/20105_Pysna_film/out/FILM/{sequence}/{shot}/lighting/render/"
        if os.path.exists(shot_path):
            created_nodes, frame_ranges = load_latest_renders(shot_path, sequence[2:], shot[2:])
        else:
            print(f"Shot path does not exist: {shot_path}")
    else:
        print("Unable to load lighting renders due to missing sequence/shot info")
    
    # Step 3: Import the template
    import_template()
    
    # Step 4: Update the camera
    load_or_update_camera()
    
    # Step 5: Find specific backdrop coordinates
    asset_coordinates = get_backdrop_coordinates("ASSETY")
    if asset_coordinates:
        print(f"Coordinates of 'ASSETY' backdrop: X={asset_coordinates[0]}, Y={asset_coordinates[1]}")
    else:
        print("'ASSETY' backdrop not found.")
    
    print_step("New composition shot creation complete")

# Run the script
if __name__ == "__main__":
    create_new_comp_shot()