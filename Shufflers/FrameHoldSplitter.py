# FrameHoldSplitter_v1.5.py
#
# This script takes a selected node, gets its frame range, adds a FrameRange node,
# and creates multiple FrameHold nodes with evenly distributed intervals across that range.
# Each FrameHold gets its own backdrop with proper spacing between them.

import nuke
import random

# User variables for customization
HORIZONTAL_SPACING = 600  # Spacing between nodes horizontally
VERTICAL_SPACING = 600   # Spacing between node rows
BACKDROP_COLOR = 0x7171C600  # Light purple color
MAIN_BACKDROP_COLOR = 0x6B6B6B00  # Dark gray color
SMALL_BACKDROP_PADDING = 200  # Padding around individual nodes
MAIN_BACKDROP_PADDING = 300   # Padding for main backdrop
BACKDROP_LABEL_FONT_SIZE = 42
SMALL_BACKDROP_FONT_SIZE = 28
SMALL_BACKDROP_WIDTH = 500    # Width of individual backdrops
SMALL_BACKDROP_HEIGHT = 500   # Height of individual backdrops

def get_frame_range(node):
    """Get the frame range of the input node."""
    first_frame = node.firstFrame()
    last_frame = node.lastFrame()
    return first_frame, last_frame

def calculate_frame_holds(first_frame, last_frame, num_holds):
    """Calculate evenly distributed frame numbers for holds."""
    total_frames = last_frame - first_frame
    interval = total_frames / (num_holds - 1) if num_holds > 1 else 0
    
    frame_holds = []
    for i in range(num_holds):
        frame = first_frame + (i * interval)
        frame_holds.append(int(round(frame)))
    
    if frame_holds[-1] != last_frame:
        frame_holds[-1] = last_frame
        
    print(f"Frame range: {first_frame} - {last_frame}")
    print(f"Number of holds: {num_holds}")
    print(f"Interval: {interval}")
    print(f"Frame holds: {frame_holds}")
    
    return frame_holds

def create_frame_range_node(input_node, first_frame, position):
    """Create a FrameRange node after the input node."""
    frame_range = nuke.nodes.FrameRange()
    frame_range.setInput(0, input_node)
    
    frame_range['first_frame'].setValue(int(first_frame))
    frame_range['last_frame'].setValue(int(first_frame))
    frame_range.setXYpos(position[0], position[1])
    frame_range['label'].setValue(f"Hold at frame {first_frame}")
    
    return frame_range

def create_frame_hold_node(input_node, frame_number, position):
    """Create a FrameHold node with specified frame number."""
    frame_hold = nuke.nodes.FrameHold()
    frame_hold.setInput(0, input_node)
    frame_hold['firstFrame'].setValue(int(frame_number))
    frame_hold.setXYpos(position[0], position[1])
    frame_hold['label'].setValue(f"Frame: {frame_number}")
    frame_hold['tile_color'].setValue(int(0x7171C600))
    
    return frame_hold

def create_small_backdrop(node, frame_number, index):
    """Create a backdrop for an individual frame hold node."""
    # Center the node within the backdrop
    bdX = node.xpos() - (SMALL_BACKDROP_WIDTH - node.screenWidth()) // 2
    bdY = node.ypos() - SMALL_BACKDROP_PADDING
    
    backdrop = nuke.nodes.BackdropNode(
        xpos = bdX,
        ypos = bdY,
        bdwidth = SMALL_BACKDROP_WIDTH,
        bdheight = SMALL_BACKDROP_HEIGHT,
        tile_color = BACKDROP_COLOR,
        note_font_size = SMALL_BACKDROP_FONT_SIZE,
        name = f'Frame_{frame_number}_Backdrop',
        label = f"Hold {index + 1}\nFrame {frame_number}"
    )
    
    return backdrop

def create_append_clip(frame_hold_nodes, position):
    """Create an AppendClip node connected to all frame hold nodes."""
    append_clip = nuke.nodes.AppendClip(inputs=frame_hold_nodes)
    append_clip.setXYpos(position[0], position[1])
    append_clip['name'].setValue(f'FrameHoldAppend_{random.randint(1000, 9999)}')
    append_clip['label'].setValue(f"Total Frames: {len(frame_hold_nodes)}")
    
    return append_clip

def create_main_backdrop(nodes, label):
    """Create the main backdrop around all nodes."""
    # Calculate bounds but with smaller padding
    bdX = min([node.xpos() for node in nodes]) - MAIN_BACKDROP_PADDING
    bdY = min([node.ypos() for node in nodes]) - MAIN_BACKDROP_PADDING
    bdW = max([node.xpos() + node.screenWidth() for node in nodes]) - bdX + (MAIN_BACKDROP_PADDING * 2)
    bdH = max([node.ypos() + node.screenHeight() for node in nodes]) - bdY + (MAIN_BACKDROP_PADDING * 2)

    backdrop = nuke.nodes.BackdropNode(
        xpos = bdX,
        bdwidth = bdW,
        ypos = bdY,
        bdheight = bdH,
        tile_color = MAIN_BACKDROP_COLOR,
        note_font_size = BACKDROP_LABEL_FONT_SIZE,
        name = f'FrameHoldSplitter_{random.randint(1000, 9999)}',
        label = label
    )
    
    return backdrop

def main():
    # Get selected node
    try:
        selected_node = nuke.selectedNode()
    except:
        nuke.message("Please select a node first.")
        return

    # Get frame range
    first_frame, last_frame = get_frame_range(selected_node)
    total_frames = last_frame - first_frame

    # Ask user for number of frame holds
    try:
        num_holds = int(nuke.getInput(
            f'How many frame holds?\n\n'
            f'Frame range: {first_frame}-{last_frame}\n'
            f'Total frames: {total_frames}', '10'))
        
        if num_holds <= 1:
            nuke.message("Please enter a number greater than 1.")
            return
            
        if num_holds > total_frames:
            nuke.message(f"Number of holds ({num_holds}) cannot be greater than total frames ({total_frames}).")
            return
            
    except ValueError:
        nuke.message("Please enter a valid number.")
        return

    # Calculate frame numbers for holds
    frame_numbers = calculate_frame_holds(first_frame, last_frame, num_holds)

    # Create FrameRange node
    start_x = selected_node.xpos()
    start_y = selected_node.ypos() + VERTICAL_SPACING
    
    frame_range_node = create_frame_range_node(
        selected_node, 
        first_frame,
        (start_x, start_y)
    )

    # Create frame hold nodes and their backdrops
    frame_hold_nodes = []
    backdrop_nodes = []
    
    for i, frame_number in enumerate(frame_numbers):
        # Calculate position with extra spacing for backdrops
        x_pos = start_x + (i * HORIZONTAL_SPACING)
        y_pos = start_y + VERTICAL_SPACING

        # Create FrameHold node
        frame_hold = create_frame_hold_node(frame_range_node, frame_number, (x_pos, y_pos))
        frame_hold_nodes.append(frame_hold)
        
        # Create individual backdrop for this frame hold
        backdrop = create_small_backdrop(frame_hold, frame_number, i)
        backdrop_nodes.append(backdrop)

    # Create AppendClip node
    append_x = start_x + ((len(frame_numbers) - 1) * HORIZONTAL_SPACING // 2)
    append_y = start_y + (VERTICAL_SPACING * 2)
    append_clip = create_append_clip(frame_hold_nodes, (append_x, append_y))

    # Create main backdrop
    all_nodes = [frame_range_node] + frame_hold_nodes + [append_clip]  # Don't include backdrop_nodes
    interval = int(round(total_frames/(num_holds-1)))
    main_backdrop = create_main_backdrop(
        all_nodes,
        f"Frame Hold Splitter\n{num_holds} holds\nInterval: {interval} frames"
    )

    nuke.message(
        f"Created {num_holds} frame holds\n"
        f"Frame range: {first_frame}-{last_frame}\n"
        f"Interval: {interval} frames"
    )

if __name__ == "__main__":
    main()
