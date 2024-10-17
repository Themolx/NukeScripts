# LightChannelSplitter_v5.py
#
# This script splits light channels from selected nodes and arranges all nodes horizontally.
# Merge nodes are aligned with the X positions of the Shuffle nodes.
# A Dot node is added before the first Shuffle for visual symmetry.
# It creates a backdrop to group the resulting nodes and provides user-customizable variables.

import nuke

# Global variables for user customization
OFFSET_X = 250  # Horizontal spacing between nodes
OFFSET_Y = 100  # Vertical spacing between node rows
BACKDROP_COLOR = 0x7F7F7FFF  # Gray color
BACKDROP_LABEL_FONT_SIZE = 42
BACKDROP_PADDING = 100  # Padding around nodes inside backdrop

def split_light_channels(node):
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

    start_x = node.xpos() + BACKDROP_PADDING
    start_y = node.ypos() + node.height() + BACKDROP_PADDING

    # Create initial Dot node
    initial_dot = nuke.nodes.Dot()
    initial_dot.setInput(0, node)
    initial_dot.setXYpos(start_x, start_y)
    dot_nodes.append(initial_dot)

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
        dot_node.setXYpos(xpos, start_y)
        shuf_node.setXYpos(xpos - 34, start_y + OFFSET_Y)
        remove_node.setXYpos(xpos - 34, start_y + OFFSET_Y * 2)
        shuffle_nodes.append(shuf_node)
        remove_nodes.append(remove_node)
        dot_nodes.append(dot_node)

    # Connect Dot nodes
    for i, dot in enumerate(dot_nodes):
        if i == 0:
            continue  # Skip the initial dot, it's already connected
        elif i == 1:
            dot.setInput(0, initial_dot)
        else:
            dot.setInput(0, dot_nodes[i - 1])

    # Create Merge nodes to combine shuffled and removed channels
    for i, remove in enumerate(remove_nodes[1:], 1):
        merge = nuke.nodes.Merge2(
            inputs=[remove_nodes[0] if i == 1 else merge_nodes[-1], remove],
            operation="plus",
            label=shuffle_nodes[i].name(),
            output="rgb"
        )
        merge.setXYpos(shuffle_nodes[i].xpos(), start_y + OFFSET_Y * 3)
        merge_nodes.append(merge)

    # Create backdrop
    all_nodes = dot_nodes + shuffle_nodes + remove_nodes + merge_nodes
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
