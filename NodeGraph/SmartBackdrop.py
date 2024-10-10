# AutoBackdrop.py v1.0
# Automatically creates a backdrop node for selected nodes in Nuke

import nuke
import random
import colorsys

def get_copy_node_channel(nodes):
    for node in nodes:
        if node.Class() == 'Copy':
            for i in range(4):  # Check up to 4 'to' channels
                knob_name = f'to{i}'
                if knob_name in node.knobs():
                    channel_value = node[knob_name].value()
                    if channel_value:  # If the channel is not empty
                        return channel_value.split('.')[0]  # Return the main channel name (before the dot)
    return None

def create_auto_backdrop():
    nodes = nuke.selectedNodes()
    if not nodes:
        return

    # Calculate bounds
    bdX = min(node.xpos() for node in nodes)
    bdY = min(node.ypos() for node in nodes)
    bdW = max(node.xpos() + node.screenWidth() for node in nodes) - bdX
    bdH = max(node.ypos() + node.screenHeight() for node in nodes) - bdY

    # Expand the bounds
    left, top, right, bottom = (-80, -140, 80, 80)
    bdX += left
    bdY += top
    bdW += (right - left)
    bdH += (bottom - top)

    # Generate a light, unsaturated color
    hue = random.random()
    saturation = random.uniform(0.1, 0.3)
    value = random.uniform(0.7, 0.9)
    r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(hue, saturation, value)]
    hex_color = int('%02x%02x%02x%02x' % (r, g, b, 255), 16)

    # Check for existing backdrops, groups, and nodes
    existing_backdrops = [n for n in nodes if n.Class() == 'BackdropNode']
    groups = [n for n in nodes if n.Class() == 'Group']
    copy_nodes = [n for n in nodes if n.Class() == 'Copy']
    shuffles = [n for n in nodes if n.Class() in ['Shuffle', 'Shuffle2']]

    # Find the node with the most inputs
    node_with_most_inputs = max(nodes, key=lambda n: n.inputs())

    # Determine the backdrop name
    copy_channel = get_copy_node_channel(nodes)
    
    if copy_channel:
        backdrop_name = f"{copy_channel}"
    elif groups:
        backdrop_name = f"{groups[0].name().rstrip('0123456789')}"
    elif shuffles:
        shuffle_values = set()
        for n in shuffles:
            if 'in1' in n.knobs():
                shuffle_values.add(n['in1'].value())
        backdrop_name = ", ".join(sorted(shuffle_values))
    elif existing_backdrops:
        backdrop_name = f"{existing_backdrops[0].name().rstrip('0123456789')}_sub"
    else:
        backdrop_name = f"{node_with_most_inputs.Class()}_{node_with_most_inputs.name().rstrip('0123456789')}"

    # Create backdrop
    new_backdrop = nuke.nodes.BackdropNode(
        xpos=bdX,
        bdwidth=bdW,
        ypos=bdY,
        bdheight=bdH,
        tile_color=hex_color,
        note_font_size=42,
        name=backdrop_name
    )
    new_backdrop['label'].setValue(backdrop_name)

    # Set z-order
    if existing_backdrops:
        lowest_z_order = min(b['z_order'].value() for b in existing_backdrops)
        new_backdrop['z_order'].setValue(lowest_z_order - 1)
    else:
        new_backdrop['z_order'].setValue(0)

# Add the Auto Backdrop command to Nuke's menu
nuke.menu('Nuke').addCommand('Edit/Auto Backdrop', create_auto_backdrop, 'shift+b')
