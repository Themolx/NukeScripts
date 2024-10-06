# LoadLightningRender_v8.py
#
# This script loads the latest lighting render layers for a given shot in Nuke.
# It creates Read nodes for each layer, arranges them neatly, and provides information about frame ranges.
# The script is designed to work in both GUI and non-GUI (frame server) modes.

import os
import re
import nuke

def print_debug(message):
    print(f"DEBUG: {message}")

def create_main_backdrop(nodes, seq_num, shot_num):
    if not nodes or not nuke.GUI:
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
    if not nuke.GUI:
        return None
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
    if not nuke.GUI:
        return
    spacing = 350
    start_x = 0
    start_y = 0
    for i, node in enumerate(nodes):
        node.setXYpos(start_x + i * spacing, start_y)

def find_latest_version(path):
    versions = [d for d in os.listdir(path) if d.startswith('v') and os.path.isdir(os.path.join(path, d))]
    return max(versions) if versions else None

def find_all_render_layers(shot_path):
    print_debug(f"Finding all render layers in: {shot_path}")
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
    
    print_debug(f"Found render layers: {render_layers}")
    return render_layers

def load_latest_renders(shot_path, seq_num, shot_num):
    print_debug(f"Loading latest renders from: {shot_path}")
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
        print_debug(f"Created Read node for {layer_name}")

    if created_nodes and nuke.GUI:
        arrange_nodes(created_nodes)
        create_main_backdrop(created_nodes, seq_num, shot_num)
        
        layer_backdrops = []
        for node in created_nodes:
            layer_name = node['label'].value().split('\n')[0]
            backdrop = create_layer_backdrop(node, layer_name)
            layer_backdrops.append(backdrop)
        
        for node, backdrop in zip(created_nodes, layer_backdrops):
            node.setXYpos(backdrop.xpos() + 50, backdrop.ypos() + 50)

    print_debug(f"Total created nodes: {len(created_nodes)}")
    return created_nodes, frame_ranges

def check_frame_range_mismatch(frame_ranges):
    print_debug("Checking frame range mismatches")
    if not frame_ranges:
        return "No frame ranges to compare."

    reference_range = next(iter(frame_ranges.values()))
    mismatches = []

    for layer, range in frame_ranges.items():
        if range != reference_range:
            mismatches.append(f"{layer}: {range[0]}-{range[1]}")

    if mismatches:
        return "Frame range mismatches detected:\n" + "\n".join(mismatches)
    else:
        return f"All layers have the same frame range: {reference_range[0]}-{reference_range[1]}"

def find_latest_renders():
    print_debug("Starting find_latest_renders function")
    script_path = nuke.root().name()
    match = re.search(r'SQ(\d+).*?SH(\d+)', script_path)
    if match:
        seq_num, shot_num = match.groups()
        shot_path = f"Y:/20105_Pysna_film/out/FILM/SQ{seq_num}/SH{shot_num}/lighting/render/"
        print_debug(f"Shot path: {shot_path}")
        if os.path.exists(shot_path):
            created_nodes, frame_ranges = load_latest_renders(shot_path, seq_num, shot_num)
            if created_nodes:
                loaded_layers = [f"{node['label'].value().split('(')[0].strip()} ({node['label'].value().split('(')[1]}" 
                                 for node in created_nodes]
                layers_message = "Loaded layers:\n" + "\n".join(loaded_layers)
                
                mismatch_message = check_frame_range_mismatch(frame_ranges)
                
                full_message = f"Loaded render layers for SQ{seq_num} SH{shot_num}\n\n{layers_message}\n\n{mismatch_message}"
                
                print_debug(full_message)
                if nuke.GUI:
                    nuke.message(full_message)
            else:
                print_debug("No render layers found.")
                if nuke.GUI:
                    nuke.message("No render layers found.")
        else:
            print_debug(f"Shot path does not exist: {shot_path}")
            if nuke.GUI:
                nuke.message(f"Shot path does not exist: {shot_path}")
    else:
        print_debug("Could not determine sequence and shot numbers from the script name.")
        if nuke.GUI:
            nuke.message("Could not determine sequence and shot numbers from the script name.")
