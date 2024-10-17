# sequenceloader_v27.py
#
# Sequence Loader for Nuke (Version 27)
# This script creates a color script for the entire movie by loading all sequences,
# creating Read nodes for each shot's MOV file, cropping to remove burn-in,
# reformatting them to fill without black edges, generating a ContactSheet,
# and ensuring a 4K final output.

import nuke
import os
import re
import random
import colorsys

# User variables
BASE_PATH = "Y:/20105_Pysna_film/out/FILM/"
FINAL_WIDTH = 3840  # 4K width
FINAL_HEIGHT = 2160  # 4K height
BACKDROP_PADDING = 50

# Crop settings
CROP_LEFT = 0
CROP_TOP = 85
CROP_RIGHT = 2048
CROP_BOTTOM = 1080

def find_all_sequences():
    return [d for d in os.listdir(BASE_PATH) if d.startswith('SQ') and os.path.isdir(os.path.join(BASE_PATH, d))]

def get_shot_numbers(sequence):
    sequence_path = os.path.join(BASE_PATH, sequence)
    return [d for d in os.listdir(sequence_path) if d.startswith('SH') and os.path.isdir(os.path.join(sequence_path, d))]

def find_latest_render(sequence, shot):
    base_path = os.path.join(BASE_PATH, sequence, shot, 'compositing', 'preview')
    if not os.path.exists(base_path):
        return None
    files = [f for f in os.listdir(base_path) if f.endswith('.mov')]
    return os.path.join(base_path, max(files)) if files else None

def create_read_crop_and_reformat_node(sequence, shot, render_path, color):
    unique_name = f"Read_{sequence}_{shot}_{random.randint(1000, 9999)}"
    
    read_node = nuke.nodes.Read(name=unique_name)
    read_node['file'].setValue(render_path.replace("\\", "/"))
    read_node['localizationPolicy'].setValue(1)  # Set to "on"
    read_node['tile_color'].setValue(int(color))
    read_node['colorspace'].setValue("Output - Rec.709")
    read_node['frame_mode'].setValue("start at")
    read_node['frame'].setValue(str(int(read_node['first'].getValue())))
    
    crop_node = nuke.nodes.Crop()
    crop_node.setInput(0, read_node)
    crop_node['box'].setValue((CROP_LEFT, CROP_TOP, CROP_RIGHT, CROP_BOTTOM))
    crop_node['reformat'].setValue(True)
    
    reformat_node = nuke.nodes.Reformat()
    reformat_node.setInput(0, crop_node)
    reformat_node['type'].setValue('to box')
    reformat_node['resize'].setValue('fill')
    reformat_node['center'].setValue(True)
    reformat_node['black_outside'].setValue(True)
    
    return reformat_node

def create_contact_sheet_auto(reformat_nodes):
    contact_sheet = nuke.nodes.ContactSheet(inputs=reformat_nodes)
    contact_sheet['name'].setValue(f'MovieColorScript_{random.randint(1000, 9999)}')
    contact_sheet['width'].setExpression('input.width*columns*resMult')
    contact_sheet['height'].setExpression('input.height*rows*resMult')
    contact_sheet['rows'].setExpression('[expr {int( (sqrt( [numvalue inputs] ) ) )} ] * [expr {int( ceil ( ([numvalue inputs] /(sqrt( [numvalue inputs] ) ) )) )} ] < [numvalue inputs]   ? [expr {int( (sqrt( [numvalue inputs] ) ) )} ] +1 : [expr {int( (sqrt( [numvalue inputs] ) ) )} ]')
    contact_sheet['columns'].setExpression('[expr {int( ceil ( ([numvalue inputs] /(sqrt( [numvalue inputs] )) )) )} ]')
    contact_sheet['center'].setValue(True)
    contact_sheet['roworder'].setValue('TopBottom')
    contact_sheet['tile_color'].setValue(0xff69f7ff)
    
    # Add custom knobs for resolution multiplier and crop values
    tab = nuke.Tab_Knob('Settings')
    res_mult = nuke.Double_Knob('resMult', 'Resolution Multiplier')
    res_mult.setRange(0.1, 2)
    res_mult.setValue(1)
    crop_left = nuke.Int_Knob('cropLeft', 'Crop Left')
    crop_left.setValue(CROP_LEFT)
    crop_top = nuke.Int_Knob('cropTop', 'Crop Top')
    crop_top.setValue(CROP_TOP)
    crop_right = nuke.Int_Knob('cropRight', 'Crop Right')
    crop_right.setValue(CROP_RIGHT)
    crop_bottom = nuke.Int_Knob('cropBottom', 'Crop Bottom')
    crop_bottom.setValue(CROP_BOTTOM)
    
    contact_sheet.addKnob(tab)
    contact_sheet.addKnob(res_mult)
    contact_sheet.addKnob(crop_left)
    contact_sheet.addKnob(crop_top)
    contact_sheet.addKnob(crop_right)
    contact_sheet.addKnob(crop_bottom)
    
    return contact_sheet

def create_reformat_to_4k(input_node):
    reformat = nuke.nodes.Reformat()
    reformat.setInput(0, input_node)
    reformat['type'].setValue('to box')
    reformat['box_width'].setValue(FINAL_WIDTH)
    reformat['box_height'].setValue(FINAL_HEIGHT)
    reformat['resize'].setValue('fit')
    reformat['center'].setValue(True)
    reformat['black_outside'].setValue(True)
    return reformat

def create_backdrop(nodes, sequences):
    bdX = min([node.xpos() for node in nodes])
    bdY = min([node.ypos() for node in nodes])
    bdW = max([node.xpos() + node.screenWidth() for node in nodes]) - bdX
    bdH = max([node.ypos() + node.screenHeight() for node in nodes]) - bdY

    backdrop = nuke.nodes.BackdropNode(
        xpos = bdX - BACKDROP_PADDING,
        bdwidth = bdW + BACKDROP_PADDING * 2,
        ypos = bdY - BACKDROP_PADDING,
        bdheight = bdH + BACKDROP_PADDING * 2,
        tile_color = int(0x808080ff),
        note_font_size=42,
        name = f'Movie_Color_Script_{random.randint(1000, 9999)}'
    )
    backdrop['label'].setValue(f"Movie Color Script\n{len(sequences)} sequences, {sum(len(shots) for shots in sequences.values())} shots")
    
    return backdrop

def generate_color(index, total):
    hue = index / total
    saturation = 0.3
    value = 0.7
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return int(r * 255) << 24 | int(g * 255) << 16 | int(b * 255) << 8 | 255

def load_all_sequences_and_create_color_script():
    all_reformat_nodes = []
    sequences = {}
    
    all_sequences = find_all_sequences()
    total_sequences = len(all_sequences)
    
    for index, sequence in enumerate(all_sequences):
        color = generate_color(index, total_sequences)
        shots = get_shot_numbers(sequence)
        sequences[sequence] = shots
        
        for shot in shots:
            render_path = find_latest_render(sequence, shot)
            if render_path:
                reformat_node = create_read_crop_and_reformat_node(sequence, shot, render_path, color)
                if reformat_node:
                    all_reformat_nodes.append(reformat_node)
            else:
                print(f"No render found for {sequence} {shot}")
    
    if all_reformat_nodes:
        contact_sheet = create_contact_sheet_auto(all_reformat_nodes)
        final_reformat = create_reformat_to_4k(contact_sheet)
        
        all_nodes = all_reformat_nodes + [contact_sheet, final_reformat]
        backdrop = create_backdrop(all_nodes, sequences)
        
        nuke.message(f"Created color script with {len(all_reformat_nodes)} shots from {len(sequences)} sequences.\nFinal size: {FINAL_WIDTH}x{FINAL_HEIGHT}")
    else:
        nuke.message("No shots were loaded.")

if __name__ == "__main__":
    load_all_sequences_and_create_color_script()
