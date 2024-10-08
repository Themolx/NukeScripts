# sequenceloader_v14.py
#
# Sequence Loader for Nuke (Version 14)
# This script loads multiple sequences, creates Read nodes for each shot,
# adds text overlays with dynamic labels, and generates a ContactSheet for easy review.
# It now strictly loads only denoise renders when that option is selected.
# The backdrop is 15% smaller, gray, and the entire setup is 500px lower.
# Each sequence now has its own dimmer color for easier visual distinction.
# The script always starts by showing the current sequence number from the script name.

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

def create_contact_sheet_auto(read_nodes):
    contact_sheet = nuke.nodes.ContactSheet(inputs=read_nodes)
    contact_sheet['name'].setValue(f'ContactSheetAuto_{random.randint(1000, 9999)}')
    contact_sheet['width'].setExpression('input.width*columns*resMult')
    contact_sheet['height'].setExpression('input.height*rows*resMult')
    contact_sheet['rows'].setExpression('[expr {int( (sqrt( [numvalue inputs] ) ) )} ] * [expr {int( ceil ( ([numvalue inputs] /(sqrt( [numvalue inputs] ) ) )) )} ] < [numvalue inputs]   ? [expr {int( (sqrt( [numvalue inputs] ) ) )} ] +1 : [expr {int( (sqrt( [numvalue inputs] ) ) )} ]')
    contact_sheet['columns'].setExpression('[expr {int( ceil ( ([numvalue inputs] /(sqrt( [numvalue inputs] )) )) )} ]')
    contact_sheet['center'].setValue(True)
    contact_sheet['roworder'].setValue('TopBottom')
    contact_sheet['tile_color'].setValue(0xff69f7ff)
    
    tab = nuke.Tab_Knob('Settings')
    res_mult = nuke.Double_Knob('resMult', 'Resolution Multiplier')
    res_mult.setRange(0.1, 2)
    res_mult.setValue(0.5)
    contact_sheet.addKnob(tab)
    contact_sheet.addKnob(res_mult)
    
    return contact_sheet

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

def load_sequence_and_create_contact_sheet():
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
        
        contact_sheet = create_contact_sheet_auto(all_read_nodes)
        contact_sheet.setXYpos(start_x + 2 * spacing_x, start_y + ((len(all_read_nodes) - 1) // 5 + 1) * spacing_y + text_offset_y + 100)
        
        all_nodes = all_read_nodes + [contact_sheet]
        backdrop = create_backdrop(all_nodes, sequences)
        
        nuke.message(f"Loaded {len(all_read_nodes)} shots from {len(sequences)} sequences: {', '.join(sequences)}")
    else:
        nuke.message("No shots were loaded.")

if __name__ == "__main__":
    load_sequence_and_create_contact_sheet()
