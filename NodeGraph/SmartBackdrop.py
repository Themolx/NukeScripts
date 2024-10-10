# AutoBackdrop.py v1.6
# Automatically creates a backdrop node for selected nodes in Nuke

import nuke
import random
import colorsys

# User variables
PADDING = 50  # Padding around nodes
BACKDROP_OFFSET = (-10, -80, 10, 10)  # Offset for left, top, right, bottom
SATURATION_RANGE = (0.05, 0.15)  # Range for color saturation
VALUE_RANGE = (0.8, 0.9)  # Range for color value
FONT_SIZE = 42  # Font size for the backdrop label

def get_backdrop_name(nodes):
    node_classes = set(node.Class() for node in nodes)
    
    has_anchor = any(node.Class() == "NoOp" and node.knob("identifier") and node.knob("identifier").value() == "anchor" for node in nodes)
    has_crypto = any(node.Class() == "Cryptomatte" for node in nodes)
    
    if has_anchor:
        if has_crypto:
            return "MASKY"
        else:
            return "ASSETY"
    
    stamp_nodes = [n for n in nodes if n.Class() == 'PostageStamp' and 'title' in n.knobs()]
    if stamp_nodes:
        stamp_title = stamp_nodes[0]['title'].value()
        if "mask" in stamp_title.lower():
            return "MASKY"
    
    shuffle_nodes = [n for n in nodes if n.Class() in ['Shuffle', 'Shuffle2']]
    if shuffle_nodes:
        shuffle_values = set()
        light_count = 0
        for n in shuffle_nodes:
            if 'in1' in n.knobs():
                value = n['in1'].value().lower()
                shuffle_values.add(value)
                if value in ['lght', 'light']:
                    light_count += 1
        if light_count > 0:
            return "Lightgroup"
        return ", ".join(sorted(shuffle_values))
    
    if node_classes.issubset({'Cryptomatte', 'ColorCorrect', 'Grade'}):
        return "CC"
    
    groups = [n for n in nodes if n.Class() == 'Group']
    if groups:
        return groups[0].name().rstrip('0123456789')
    
    if stamp_nodes:
        return stamp_nodes[0]['title'].value()
    
    copy_nodes = [n for n in nodes if n.Class() == 'Copy']
    if copy_nodes:
        for i in range(4):
            knob_name = f'to{i}'
            if knob_name in copy_nodes[0].knobs():
                channel_value = copy_nodes[0][knob_name].value()
                if channel_value:
                    return channel_value.split('.')[0]
    
    node_with_most_inputs = max(nodes, key=lambda n: n.inputs())
    return f"{node_with_most_inputs.Class()}_{node_with_most_inputs.name().rstrip('0123456789')}"

def create_auto_backdrop():
    nodes = nuke.selectedNodes()
    if not nodes:
        return

    # Calculate bounds
    bdX = min(node.xpos() for node in nodes)
    bdY = min(node.ypos() for node in nodes)
    bdW = max(node.xpos() + node.screenWidth() for node in nodes) - bdX
    bdH = max(node.ypos() + node.screenHeight() for node in nodes) - bdY

    # Add padding
    bdX -= PADDING
    bdY -= PADDING
    bdW += 2 * PADDING
    bdH += 2 * PADDING

    # Apply backdrop offset
    left, top, right, bottom = BACKDROP_OFFSET
    bdX += left
    bdY += top
    bdW += (right - left)
    bdH += (bottom - top)

    # Generate a light, unsaturated color
    hue = random.random()
    saturation = random.uniform(*SATURATION_RANGE)
    value = random.uniform(*VALUE_RANGE)
    r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(hue, saturation, value)]
    hex_color = int('%02x%02x%02x%02x' % (r, g, b, 255), 16)

    # Determine the backdrop name
    backdrop_name = get_backdrop_name(nodes)

    # Create backdrop
    backdrop = nuke.nodes.BackdropNode(
        xpos = bdX,
        bdwidth = bdW,
        ypos = bdY,
        bdheight = bdH,
        tile_color = hex_color,
        note_font_size = FONT_SIZE,
        name = backdrop_name
    )
    backdrop['label'].setValue(backdrop_name)

    return backdrop

# Add the Auto Backdrop command to Nuke's menu
nuke.menu('Nuke').addCommand('Edit/Auto Backdrop', create_auto_backdrop, 'shift+b')
