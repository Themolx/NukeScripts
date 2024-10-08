# sequenceloader_v26.py
#
# Sequence Loader for Nuke (Version 26)
# This script loads multiple sequences, creates Read nodes for each shot,
# adds text overlays with dynamic labels, and generates a single AppendClip node for easy review.
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

def find_latest_render(sequence, shot, task_type):
    base_path = f"Y:/20105_Pysna_film/out/FILM/SQ{sequence}/SH{shot}/{'compositing_denoise' if task_type == 'denoise' else 'compositing'}/render/"
    if not os.path.exists(base_path):
        return None
    versions = [d for d in os.listdir(base_path) if d.startswith('v')]
    return os.path.join(base_path, max(versions, key=lambda x: int(x[1:]))) if versions else None

def find_frame_range(render_path, sequence, shot, version, task_type):
    file_pattern = f"pp_FILM_SQ{sequence}_SH{shot}_{'compositing_denoise' if task_type == 'denoise' else 'comp'}_{version}.*.exr"
    files = [f for f in os.listdir(render_path) if re.match(file_pattern.replace('*', '\d+'), f)]
    if files:
        frames = [int(re.search(r'\.(\d+)\.', f).group(1)) for f in files]
        return min(frames), max(frames)
    
    print(f"No frames found for SQ{sequence} SH{shot} in {render_path}")
    return None, None

def create_read_node(sequence, shot, render_path, task_type, color):
    version = os.path.basename(render_path)
    file_pattern = f"pp_FILM_SQ{sequence}_SH{shot}_{'compositing_denoise' if task_type == 'denoise' else 'comp'}_{version}.%06d.exr"
    full_path = os.path.join(render_path, file_pattern)
    
    first_frame, last_frame = find_frame_range(render_path, sequence, shot, version, task_type)
    if first_frame is None or last_frame is None:
        return None
    
    unique_name = f"Read_SQ{sequence}_SH{shot}_{task_type}_{random.randint(1000, 9999)}"
    
    read_node = nuke.nodes.Read(name=unique_name)
    read_node['file'].setValue(full_path.replace("\\", "/"))
    read_node['first'].setValue(first_frame)
    read_node['last'].setValue(last_frame)
    read_node['localizationPolicy'].setValue(1)  # Set to "on"
    read_node['tile_color'].setValue(int(color))
    
    return read_node

def create_text_node(sequence, shot, task_type, color):
    text_node = nuke.nodes.Text2()
    text_node['message'].setValue(f"SQ{sequence}\nSH{shot}\n{task_type.upper()}")
    text_node['font_size'].setValue(50)
    text_node['global_font_scale'].setValue(0.5)
    text_node['box'].setValue([0, 0, 1920, 1080])
    text_node['xjustify'].setValue('center')
    text_node['yjustify'].setValue('bottom')
    text_node['color'].setValue([1, 1, 1, 1])
    text_node['label'].setValue("[value message]")
    text_node['tile_color'].setValue(int(color))
    return text_node

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
    
    is_denoise_script = 'denoise' in nuke.root().name().lower()
    task_type = 'denoise' if is_denoise_script and nuke.choice("Render Selection", "Choose which renders to load:", ["Regular (Comp)", "Denoised"]) == 1 else 'comp'
    
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
            render_path = find_latest_render(sequence, shot.split('_')[1], task_type)
            if render_path:
                read_node = create_read_node(sequence, shot.split('_')[1], render_path, task_type, color)
                if read_node:
                    text_node = create_text_node(sequence, shot.split('_')[1], task_type, color)
                    text_node.setInput(0, read_node)
                    all_read_nodes.append(text_node)
            elif task_type == 'denoise':
                print(f"No denoise render found for SQ{sequence} SH{shot.split('_')[1]}")
    
    if all_read_nodes:
        spacing_x, spacing_y, text_offset_y = 250, 250, 107
        
        for i, node in enumerate(all_read_nodes):
            read_node = node.input(0)
            read_node.setXYpos(start_x + (i % 5) * spacing_x, start_y + (i // 5) * spacing_y)
            node.setXYpos(read_node.xpos(), read_node.ypos() + text_offset_y)
        
        append_clip = create_append_clip(all_read_nodes)
        print(f"Debug: AppendClip node created: {append_clip.name()}")
        append_clip.setXYpos(start_x + 2 * spacing_x, start_y + ((len(all_read_nodes) - 1) // 5 + 1) * spacing_y + text_offset_y + 100)
        
        all_nodes = all_read_nodes + [append_clip]
        backdrop = create_backdrop(all_nodes, sequences)
        
        nuke.message(f"Loaded {len(all_read_nodes)} shots from {len(sequences)} sequences: {', '.join(sequences)}")
    else:
        nuke.message("No shots were loaded.")

if __name__ == "__main__":
    load_sequence_and_create_append_clip()
