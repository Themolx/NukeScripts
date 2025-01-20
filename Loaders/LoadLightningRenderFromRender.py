# LoadLightningRenderAndSetupCrypto_v8.py
#
# This script loads the latest lighting render layers for a given shot in Nuke,
# creates Read nodes for each layer, and then sets up a Cryptomatte, Shuffle, and Premult
# node chain for each Read node. The Shuffle node's input 1 is connected to the initially
# selected node, and input 2 is connected to the Cryptomatte node. It arranges all nodes 
# neatly and wraps them in backdrops for easy organization. The script works based on a 
# selected Read node or the current script name.

import os
import re
import nuke

# User customizable variables
NODE_SPACING_X = 280  # Horizontal spacing between node groups
NODE_SPACING_Y = 1000  # Vertical spacing between rows
NODES_PER_ROW = 5     # Number of node groups per row
CRYPTO_OFFSET_X = -100 # Offset for Crypto node on X-axis

def print_debug(message):
    print(f"DEBUG: {message}")

def create_main_backdrop(nodes, seq_num, shot_num):
    if not nodes or not nuke.GUI:
        return None
    bdX = min([node.xpos() for node in nodes]) - 50
    bdY = min([node.ypos() for node in nodes]) - 50
    bdW = max([node.xpos() + node.screenWidth() for node in nodes]) - bdX + 100
    bdH = max([node.ypos() + node.screenHeight() for node in nodes]) - bdY + 100

    backdrop = nuke.nodes.BackdropNode(
        xpos = bdX,
        bdwidth = bdW,
        ypos = bdY,
        bdheight = bdH,
        tile_color = int("0x7171C680", 16),
        note_font_size=42,
        label=f'<center>SQ{seq_num} SH{shot_num}\nLighting Renders'
    )
    return backdrop

def create_layer_backdrop(read_node, layer_name):
    if not nuke.GUI:
        return None
    padding = 20
    backdrop_label = re.sub(r'^SQ\d+_SH\d+_', '', layer_name)
    backdrop = nuke.nodes.BackdropNode(
        xpos = read_node.xpos() - padding - 10,
        ypos = read_node.ypos() - padding,
        bdwidth = NODE_SPACING_X - 20,
        bdheight = read_node.screenHeight() * 4 + padding * 5,
        tile_color = int("0xAAAACC80", 16),
        note_font_size=24,
        label=backdrop_label
    )
    return backdrop

def arrange_nodes(nodes, start_x, start_y):
    if not nuke.GUI:
        return
    for i, node in enumerate(nodes):
        row = i // (4 * NODES_PER_ROW)
        col = (i // 4) % NODES_PER_ROW
        node_type = i % 4
        node_x = start_x + col * NODE_SPACING_X
        node_y = start_y + row * NODE_SPACING_Y + node_type * 60
        
        if node_type == 1:  # Crypto node
            node_x += CRYPTO_OFFSET_X
        
        node.setXYpos(int(node_x), int(node_y))

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

def create_crypto_setup(read_node, selected_node):
    # Create Cryptomatte node
    crypto_node = nuke.nodes.Cryptomatte(inputs=[read_node])
    crypto_node['name'].setValue(f"Crypto_{read_node.name()}")
    # Create Shuffle node with correct inputs and channel routing
    shuffle_node = nuke.nodes.Shuffle(
        name=f"Shuffle_{read_node.name()}",
        inputs=[selected_node, crypto_node]  # Switch inputs: input 1 to selected node, input 2 to Crypto
    )
    shuffle_node['in'].setValue('alpha')
    shuffle_node['in2'].setValue('rgba')
    shuffle_node['red'].setValue('red2')
    shuffle_node['green'].setValue('green2')
    shuffle_node['blue'].setValue('blue2')
    shuffle_node['alpha'].setValue('red')
    # Create Premult node
    premult_node = nuke.nodes.Premult(
        name=f"Premult_{read_node.name()}",
        inputs=[shuffle_node]
    )
    return crypto_node, shuffle_node, premult_node

def load_latest_renders(shot_path, seq_num, shot_num, start_x, start_y, selected_node):
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

        # Create Cryptomatte setup for each Read node
        crypto_node, shuffle_node, premult_node = create_crypto_setup(read_node, selected_node)
        created_nodes.extend([crypto_node, shuffle_node, premult_node])

    if created_nodes and nuke.GUI:
        arrange_nodes(created_nodes, start_x, start_y)
        create_main_backdrop(created_nodes, seq_num, shot_num)
        
        layer_backdrops = []
        for i in range(0, len(created_nodes), 4):  # Group every 4 nodes (Read, Crypto, Shuffle, Premult)
            read_node = created_nodes[i]
            layer_name = read_node['label'].value().split('\n')[0]
            backdrop = create_layer_backdrop(read_node, layer_name)
            layer_backdrops.append(backdrop)

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

def get_seq_shot_from_read_node(node):
    file_path = node['file'].value()
    match = re.search(r'SQ(\d+)/SH(\d+)', file_path)
    if match:
        return match.group(1), match.group(2)
    return None, None

def find_latest_renders_and_setup_crypto():
    print_debug("Starting find_latest_renders_and_setup_crypto function")
    
    # Try to get sequence and shot from selected Read node
    selected_nodes = nuke.selectedNodes('Read')
    if selected_nodes:
        read_node = selected_nodes[0]
        seq_num, shot_num = get_seq_shot_from_read_node(read_node)
        start_x = read_node.xpos()
        start_y = read_node.ypos() + 500  # 500px lower than the selected node
        selected_node = read_node
    else:
        # Fallback to getting sequence and shot from script name
        script_path = nuke.root().name()
        match = re.search(r'SQ(\d+).*?SH(\d+)', script_path)
        if match:
            seq_num, shot_num = match.groups()
            start_x = 0
            start_y = 0
            selected_node = None
        else:
            seq_num, shot_num = None, None
            start_x = 0
            start_y = 0
            selected_node = None

    if seq_num and shot_num:
        shot_path = f"Y:/20105_Pysna_film/out/FILM/SQ{seq_num}/SH{shot_num}/lighting/render/"
        print_debug(f"Shot path: {shot_path}")
        if os.path.exists(shot_path):
            created_nodes, frame_ranges = load_latest_renders(shot_path, seq_num, shot_num, start_x, start_y, selected_node)
            if created_nodes:
                loaded_layers = [f"{node['label'].value().split('(')[0].strip()} ({node['label'].value().split('(')[1]}" 
                                 for node in created_nodes if 'Read' in node.name()]
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
        print_debug("Could not determine sequence and shot numbers.")
        if nuke.GUI:
            nuke.message("Could not determine sequence and shot numbers. Please select a Read node or ensure the script name contains SQ and SH information.")

# Run the script
find_latest_renders_and_setup_crypto()
