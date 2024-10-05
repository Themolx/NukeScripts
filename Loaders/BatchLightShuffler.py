import nuke


# LightChannelSplitter.py v1.1
#
# This script splits light channels from selected Nuke nodes and creates a network
# of Shuffle and Merge nodes to separate and recombine them.
#
# Usage:
# 1. Select one or more nodes containing light channels in Nuke
# 2. Run this script
# 3. The script will create a network of nodes for each light channel, wrapped in a backdrop
#
# Features:
# - Automatically detects and splits light channels based on user-defined keywords
# - Creates Shuffle nodes for each light channel
# - Adds Remove nodes to keep only RGB channels
# - Merges all channels back together
# - Wraps the entire network in a labeled backdrop
#
# Customization:
# Adjust the user variables at the top of the script to change node spacing,
# backdrop color, light channel detection keywords, and other visual aspects.

import nuke

# User variables for customization
OFFSET_X = 250  # Horizontal spacing between node columns
OFFSET_Y = 200  # Vertical spacing between nodes
MERGE_OFFSET_Y = 400  # Vertical offset for Merge nodes
BACKDROP_COLOR = 0x7F7F7FFF  # Gray color
BACKDROP_LABEL_FONT_SIZE = 42
BACKDROP_PADDING = 100  # Padding around nodes inside backdrop

# Light channel detection keywords
LIGHT_KEYWORDS = ['light', 'lght']  # Add or modify keywords as needed
EXCLUDE_KEYWORDS = ['lighting', 'lightning']  # Keywords to exclude from detection

def split_light_channels(node):
    # Get all channels and filter for light channels based on user-defined keywords
    all_channels = node.channels()
    light_channels = [chan.split('.')[0] for chan in all_channels
                      if any(keyword in chan.lower() for keyword in LIGHT_KEYWORDS)
                      and not any(keyword in chan.lower() for keyword in EXCLUDE_KEYWORDS)]
    light_channels = list(set(light_channels))  # Remove duplicates
    light_channels.sort(key=str.lower)

    if not light_channels:
        nuke.message(f"No suitable light channels found in node: {node.name()}")
        return

    dot_nodes = []
    shuffle_nodes = []
    remove_nodes = []
    merge_nodes = []
    second_dot_nodes = []

    # Calculate the starting position
    start_x = node.xpos() + BACKDROP_PADDING
    start_y = node.ypos() + BACKDROP_PADDING

    # Create Dot, Shuffle, and Remove nodes for each light channel
    for i, chan in enumerate(light_channels):
        dot_node = nuke.nodes.Dot()
        shuf_node = nuke.nodes.Shuffle2(
            name=f"{node.name()}_{chan}",
            inputs=[dot_node],
            postage_stamp=True,
            hide_input=False
        )
        shuf_node["in1"].setValue(chan)
        remove_node = nuke.nodes.Remove(
            operation="keep",
            channels="rgb",
            name=f"Keep_{node.name()}_{chan}",
            label="keep [value channels]",
            inputs=[shuf_node]
        )
        xpos = start_x + OFFSET_X * i
        ypos = start_y + OFFSET_Y
        dot_node.setXYpos(xpos, ypos)
        shuf_node.setXYpos(xpos - 34, dot_node.ypos() + 100)
        remove_node.setXYpos(xpos - 34, shuf_node.ypos() + 100)
        shuffle_nodes.append(shuf_node)
        remove_nodes.append(remove_node)
        dot_nodes.append(dot_node)

    # Connect Dot nodes
    for i, dot in enumerate(dot_nodes):
        if i == 0:
            dot.setInput(0, node)
        else:
            dot.setInput(0, dot_nodes[i - 1])

    # Create Merge nodes to combine shuffled and removed channels
    for i, remove in enumerate(remove_nodes):
        if i == 0:
            continue
        else:
            dot_node = nuke.nodes.Dot()
            second_dot_nodes.append(dot_node)
            dot_node.setInput(0, remove)
            merge = nuke.nodes.Merge2(
                inputs=[remove_nodes[0] if i == 1 else merge_nodes[-1], dot_node],
                operation="plus",
                label=shuffle_nodes[i].name(),
                output="rgb"
            )
            merge.setXYpos(remove_nodes[0].xpos(), remove_nodes[0].ypos() + MERGE_OFFSET_Y + (i - 1) * 100)
            dot_node.setXYpos(remove.xpos() + 34, merge.ypos() + 5)
            merge_nodes.append(merge)

    # Create backdrop
    all_nodes = dot_nodes + shuffle_nodes + remove_nodes + merge_nodes + second_dot_nodes
    bdX = min(node.xpos() for node in all_nodes) - BACKDROP_PADDING
    bdY = min(node.ypos() for node in all_nodes) - BACKDROP_PADDING
    bdW = max(node.xpos() + node.screenWidth() for node in all_nodes) - bdX + BACKDROP_PADDING * 2
    bdH = max(node.ypos() + node.screenHeight() for node in all_nodes) - bdY + BACKDROP_PADDING * 2

    backdrop = nuke.nodes.BackdropNode(
        xpos = bdX,
        bdwidth = bdW,
        ypos = bdY,
        bdheight = bdH,
        tile_color = BACKDROP_COLOR,
        note_font_size = BACKDROP_LABEL_FONT_SIZE,
        label = f"Light Channel Splitter - {node.name()}"
    )

def batch_split_light_channels():
    selected_nodes = nuke.selectedNodes()
    if not selected_nodes:
        nuke.message("Please select at least one node.")
        return

    for node in selected_nodes:
        split_light_channels(node)

    nuke.message(f"Processed {len(selected_nodes)} node(s).")

# Run the batch operation
batch_split_light_channels()



# Global variables for user customization
OFFSET_X = 250
OFFSET_Y = 200
MERGE_OFFSET_Y = 400
BACKDROP_COLOR = 0x7F7F7FFF  # Gray color
BACKDROP_LABEL_FONT_SIZE = 42
BACKDROP_PADDING = 100  # Padding around nodes inside backdrop

def split_light_channels(node):
    # Get all channels and filter for light channels, excluding 'lighting' and 'lightning'
    all_channels = node.channels()
    light_channels = [chan.split('.')[0] for chan in all_channels
                      if ('light' in chan.lower() or 'lght' in chan.lower())
                      and not chan.lower().startswith(('lighting', 'lightning'))]
    light_channels = list(set(light_channels))  # Remove duplicates
    light_channels.sort(key=str.lower)

    if not light_channels:
        nuke.message(f"No suitable light channels found in node: {node.name()}")
        return

    dot_nodes = []
    shuffle_nodes = []
    remove_nodes = []
    merge_nodes = []
    second_dot_nodes = []

    # Calculate the starting position
    start_x = node.xpos() + BACKDROP_PADDING
    start_y = node.ypos() + BACKDROP_PADDING

    # Create Dot, Shuffle, and Remove nodes for each light channel
    for i, chan in enumerate(light_channels):
        dot_node = nuke.nodes.Dot()
        shuf_node = nuke.nodes.Shuffle2(
            name=f"{node.name()}_{chan}",
            inputs=[dot_node],
            postage_stamp=True,
            hide_input=False
        )
        shuf_node["in1"].setValue(chan)
        remove_node = nuke.nodes.Remove(
            operation="keep",
            channels="rgb",
            name=f"Keep_{node.name()}_{chan}",
            label="keep [value channels]",
            inputs=[shuf_node]
        )
        xpos = start_x + OFFSET_X * i
        ypos = start_y + OFFSET_Y
        dot_node.setXYpos(xpos, ypos)
        shuf_node.setXYpos(xpos - 34, dot_node.ypos() + 100)
        remove_node.setXYpos(xpos - 34, shuf_node.ypos() + 100)
        shuffle_nodes.append(shuf_node)
        remove_nodes.append(remove_node)
        dot_nodes.append(dot_node)

    # Connect Dot nodes
    for i, dot in enumerate(dot_nodes):
        if i == 0:
            dot.setInput(0, node)
        else:
            dot.setInput(0, dot_nodes[i - 1])

    # Create Merge nodes to combine shuffled and removed channels
    for i, remove in enumerate(remove_nodes):
        if i == 0:
            continue
        else:
            dot_node = nuke.nodes.Dot()
            second_dot_nodes.append(dot_node)
            dot_node.setInput(0, remove)
            merge = nuke.nodes.Merge2(
                inputs=[remove_nodes[0] if i == 1 else merge_nodes[-1], dot_node],
                operation="plus",
                label=shuffle_nodes[i].name(),
                output="rgb"
            )
            merge.setXYpos(remove_nodes[0].xpos(), remove_nodes[0].ypos() + MERGE_OFFSET_Y + (i - 1) * 100)
            dot_node.setXYpos(remove.xpos() + 34, merge.ypos() + 5)
            merge_nodes.append(merge)

    # Create backdrop
    all_nodes = dot_nodes + shuffle_nodes + remove_nodes + merge_nodes + second_dot_nodes
    bdX = min(node.xpos() for node in all_nodes) - BACKDROP_PADDING
    bdY = min(node.ypos() for node in all_nodes) - BACKDROP_PADDING
    bdW = max(node.xpos() + node.screenWidth() for node in all_nodes) - bdX + BACKDROP_PADDING * 2
    bdH = max(node.ypos() + node.screenHeight() for node in all_nodes) - bdY + BACKDROP_PADDING * 2

    backdrop = nuke.nodes.BackdropNode(
        xpos = bdX,
        bdwidth = bdW,
        ypos = bdY,
        bdheight = bdH,
        tile_color = BACKDROP_COLOR,
        note_font_size = BACKDROP_LABEL_FONT_SIZE,
        label = f"Light Channel Splitter - {node.name()}"
    )

def batch_split_light_channels():
    selected_nodes = nuke.selectedNodes()
    if not selected_nodes:
        nuke.message("Please select at least one node.")
        return

    for node in selected_nodes:
        split_light_channels(node)

    nuke.message(f"Processed {len(selected_nodes)} node(s).")

# Run the batch operation
batch_split_light_channels()