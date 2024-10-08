# sequenceloader_v27.py
#
# Sequence Loader for Nuke (Version 27)
# This script loads multiple sequences, creates Read nodes for each shot,
# and generates a single AppendClip node for easy review.
# It now includes a "Play" button that simply simulates Alt+F and Enter key presses.

import nuke
import os
import re
import random
import colorsys

def get_current_sequence():
    script_name = nuke.root().name()
    match = re.search(r'SQ(\d{4})', script_name)
    if match:
        return match.group(1)
    match = re.search(r'SQ.*?(\d{4})', script_name)
    if match:
        return match.group(1)
    return None

def get_sequence_from_user(current_sequence):
    default_value = current_sequence or ''
    sequence = nuke.getInput(f'Enter sequence number (e.g., {default_value}):', default_value)
    return sequence

def get_shot_numbers(sequence):
    return [f"{sequence}_{i:04d}" for i in range(10, 1000, 10)]

def find_latest_render(sequence, shot):
    base_path = f"Y:/20105_Pysna_film/out/FILM/SQ{sequence}/SH{shot}/compositing/preview/"
    if not os.path.exists(base_path):
        return None
    files = [f for f in os.listdir(base_path) if f.endswith('.mov')]
    return os.path.join(base_path, max(files)) if files else None

def create_read_node(sequence, shot, render_path, color):
    full_path = render_path
    
    unique_name = f"Read_SQ{sequence}_SH{shot}_{random.randint(1000, 9999)}"
    
    read_node = nuke.nodes.Read(name=unique_name)
    read_node['file'].setValue(full_path.replace("\\", "/"))
    read_node['localizationPolicy'].setValue(1)  # Set to "on"
    read_node['tile_color'].setValue(int(color))
    read_node['colorspace'].setValue("Output - Rec.709")
    read_node['frame_mode'].setValue("start at")
    read_node['frame'].setValue(str(int(read_node['first'].getValue())))
    
    return read_node
def create_append_clip(read_nodes):
    append_clip = nuke.nodes.AppendClip(inputs=read_nodes)
    append_clip['name'].setValue(f'AppendClip_{random.randint(1000, 9999)}')
    append_clip['tile_color'].setValue(0xff69f7ff)
    
    # Add Python button
    play_button = nuke.PyScript_Knob('play', 'Play in Flipbook')
    play_button.setFlag(nuke.STARTLINE)
    append_clip.addKnob(play_button)
    
    # Set the callback for the button with debug prints
    append_clip['play'].setValue("""
import nuke

print("Debug: Button clicked")
node = nuke.thisNode()
print(f"Debug: Node type: {type(node)}")
print(f"Debug: Node name: {node.name()}")

try:
    print("Debug: Attempting to launch flipbook")
    node.setSelected(True)
    nuke.execute("alt+f")
    nuke.execute("Return") 
    print("Debug: Flipbook launched successfully")
except Exception as e:
    print(f"Debug: An unexpected error occurred: {e}")
""")
    
    return append_clip

def create_backdrop(nodes, sequences):
    bdX = min([node.xpos() for node in nodes])
    bdY = min([node.ypos() for node in nodes])
    bdW = max([node.xpos() + node.screenWidth() for node in nodes]) - bdX
    bdH = max([node.ypos() + node.screenHeight() for node in nodes]) - bdY

    backdrop_padding = 340
    bdX += backdrop_padding * 0.15
    bdY += backdrop_padding * 0.15
    bdW *= 0.85
    bdH *= 0.85

    backdrop = nuke.nodes.BackdropNode(
        xpos = bdX - backdrop_padding,
        bdwidth = bdW + backdrop_padding * 2,
        ypos = bdY - backdrop_padding,
        bdheight = bdH + backdrop_padding * 2,
        tile_color = int(0x808080ff),
        note_font_size=42,
        name = f'SEQ_Check_{"-".join(sequences)}_{random.randint(1000, 9999)}'
    )
    backdrop['label'].setValue(f"SEQ Check {', '.join(sequences)}")
    
    return backdrop

def find_write_node():
    write_nodes = [node for node in nuke.allNodes('Write') if node.name().startswith('PFX_Write_MAIN')]
    return write_nodes[0] if write_nodes else None

def generate_color(index, total):
    hue = index / total
    saturation = 0.3  # Reduced from 0.7 to make colors dimmer
    value = 0.7  # Reduced from 0.9 to make colors dimmer
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return int(r * 255) << 24 | int(g * 255) << 16 | int(b * 255) << 8 | 255

def load_sequence_and_create_append_clip():
    write_node = find_write_node()
    if not write_node:
        nuke.message("Could not find PFX_Write_MAIN node.")
        return
    
    start_x = write_node.xpos() - 500
    start_y = write_node.ypos() + 900
    
    all_read_nodes = []
    sequences = []
    
    current_sequence = get_current_sequence()
    
    while True:
        sequence = get_sequence_from_user(current_sequence)
        if not sequence:
            break
        
        sequences.append(sequence)
        current_sequence = f"{int(sequence) + 10:04d}"  # Increment for next iteration
    
    for index, sequence in enumerate(sequences):
        color = generate_color(index, len(sequences))
        
        for shot in get_shot_numbers(sequence):
            render_path = find_latest_render(sequence, shot.split('_')[1])
            if render_path:
                read_node = create_read_node(sequence, shot.split('_')[1], render_path, color)
                all_read_nodes.append(read_node)
    
    if all_read_nodes:
        spacing_x, spacing_y = 250, 250
        
        for i, node in enumerate(all_read_nodes):
            node.setXYpos(start_x + (i % 5) * spacing_x, start_y + (i // 5) * spacing_y)
        
        append_clip = create_append_clip(all_read_nodes)
        print(f"Debug: AppendClip node created: {append_clip.name()}")
        append_clip.setXYpos(start_x + 2 * spacing_x, start_y + ((len(all_read_nodes) - 1) // 5 + 1) * spacing_y + 100)
        
        all_nodes = all_read_nodes + [append_clip]
        backdrop = create_backdrop(all_nodes, sequences)
        
        nuke.message(f"Loaded {len(all_read_nodes)} shots from {len(sequences)} sequences: {', '.join(sequences)}")
    else:
        nuke.message("No shots were loaded.")

if __name__ == "__main__":
    load_sequence_and_create_append_clip()
