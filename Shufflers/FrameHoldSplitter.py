# FrameHoldSplitter_v1.3.py
#
# This script takes a selected node, gets its frame range, adds a FrameRange node,
# and creates multiple FrameHold nodes with evenly distributed intervals across that range. 
#
# Fixed bug with FrameRange node creation and time knob handling

import nuke
import random
import math

# User variables
VERTICAL_SPACING = 50  # Spacing between nodes vertically
HORIZONTAL_SPACING = 150  # Spacing between nodes horizontally
MAX_NODES_PER_ROW = 20  # Maximum number of nodes in a row before starting new row
BACKDROP_PADDING = 50  # Padding around nodes in backdrop

def get_frame_range(node):
    """Get the frame range of the input node."""
    first_frame = node.firstFrame()
    last_frame = node.lastFrame()
    return first_frame, last_frame

def create_frame_range_node(input_node, first_frame, position):
    """Create a FrameRange node after the input node."""
    frame_range = nuke.nodes.FrameRange()
    frame_range.setInput(0, input_node)
    
    # Set frame range - ensure values are integers
    frame_range['first_frame'].setValue(int(first_frame))
    frame_range['last_frame'].setValue(int(first_frame))
    
    # Don't set the time knob - let it use its default value
    
    # Set position
    frame_range.setXYpos(position[0], position[1])
    
    # Add label for clarity
    frame_range['label'].setValue(f"Hold at frame {first_frame}")
    
    return frame_range

def calculate_frame_holds(first_frame, last_frame, num_holds):
    """Calculate evenly distributed frame numbers for holds."""
    # Calculate total number of frames
    total_frames = last_frame - first_frame
    
    # Calculate the interval between holds
    # We subtract 1 from num_holds because we want to include both first and last frames
    interval = total_frames / (num_holds - 1) if num_holds > 1 else 0
    
    # Generate frame numbers
    frame_holds = []
    for i in range(num_holds):
        frame = first_frame + (i * interval)
        # Round to nearest integer
        frame_holds.append(int(round(frame)))
    
    # Ensure we include the last frame if it's not already included
    if frame_holds[-1] != last_frame:
        frame_holds[-1] = last_frame
        
    # Print debug information
    print(f"Frame range: {first_frame} - {last_frame}")
    print(f"Number of holds: {num_holds}")
    print(f"Interval: {interval}")
    print(f"Frame holds: {frame_holds}")
    
    return frame_holds

def create_frame_hold_node(input_node, frame_number, position):
    """Create a FrameHold node with specified frame number."""
    frame_hold = nuke.nodes.FrameHold()
    frame_hold.setInput(0, input_node)
    
    # Set the frame value - ensure it's an integer
    frame_hold['firstFrame'].setValue(int(frame_number))
    
    # Set position
    frame_hold.setXYpos(position[0], position[1])
    
    # Set label to show which frame is held
    frame_hold['label'].setValue(f"Frame: {frame_number}")
    
    # Give it a slight color tint to make it more visible
    frame_hold['tile_color'].setValue(int(0x7171C600))
    
    return frame_hold

def create_append_clip(frame_hold_nodes, position):
    """Create an AppendClip node connected to all frame hold nodes."""
    append_clip = nuke.nodes.AppendClip(inputs=frame_hold_nodes)
    append_clip.setXYpos(position[0], position[1])
    append_clip['name'].setValue(f'FrameHoldAppend_{random.randint(1000, 9999)}')
    
    # Add a helpful label
    append_clip['label'].setValue(f"Total Frames: {len(frame_hold_nodes)}")
    
    return append_clip

def create_backdrop(nodes, label):
    """Create a backdrop around the created nodes."""
    # Calculate bounds
    bdX = min([node.xpos() for node in nodes]) - BACKDROP_PADDING
    bdY = min([node.ypos() for node in nodes]) - BACKDROP_PADDING
    bdW = max([node.xpos() + node.screenWidth() for node in nodes]) - bdX + BACKDROP_PADDING
    bdH = max([node.ypos() + node.screenHeight() for node in nodes]) - bdY + BACKDROP_PADDING

    backdrop = nuke.nodes.BackdropNode(
        xpos = bdX,
        bdwidth = bdW,
        ypos = bdY,
        bdheight = bdH,
        tile_color = int(0x6B6B6B00),  # Dark gray
        note_font_size=42,
        name = f'FrameHoldSplitter_{random.randint(1000, 9999)}'
    )
    backdrop['label'].setValue(label)
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
    frame_range_node = create_frame_range_node(
        selected_node, 
        first_frame,
        (selected_node.xpos(), selected_node.ypos() + 50)
    )

    # Create frame hold nodes
    frame_hold_nodes = []
    start_x = selected_node.xpos()
    start_y = selected_node.ypos() + 150  # Increased to make room for FrameRange node

    for i, frame_number in enumerate(frame_numbers):
        # Calculate position (grid layout)
        row = i // MAX_NODES_PER_ROW
        col = i % MAX_NODES_PER_ROW
        x_pos = start_x + (col * HORIZONTAL_SPACING)
        y_pos = start_y + (row * VERTICAL_SPACING)

        frame_hold = create_frame_hold_node(frame_range_node, frame_number, (x_pos, y_pos))
        frame_hold_nodes.append(frame_hold)

    # Create AppendClip node
    append_x = start_x + ((MAX_NODES_PER_ROW - 1) * HORIZONTAL_SPACING) // 2
    append_y = start_y + (((len(frame_hold_nodes) - 1) // MAX_NODES_PER_ROW + 1) * VERTICAL_SPACING) + 50
    append_clip = create_append_clip(frame_hold_nodes, (append_x, append_y))

    # Create backdrop
    all_nodes = [frame_range_node] + frame_hold_nodes + [append_clip]
    backdrop = create_backdrop(
        all_nodes, 
        f"Frame Hold Splitter\n{num_holds} holds\nInterval: {int(round(total_frames/(num_holds-1)))} frames"
    )

    nuke.message(
        f"Created {num_holds} frame holds\n"
        f"Frame range: {first_frame}-{last_frame}\n"
        f"Interval: {int(round(total_frames/(num_holds-1)))} frames"
    )

if __name__ == "__main__":
    main()
