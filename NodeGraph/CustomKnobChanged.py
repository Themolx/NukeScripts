# AnimatedNodeSaturator.py v1.0
#
# This script increases the saturation of the tile color for all animated nodes in a Nuke script.
# It loops through all nodes, checks if any knob is animated, and if so, increases the saturation of the node's tile color.
#
# Usage: Run the script in Nuke's Script Editor or as a menu item.

import nuke
import colorsys

# User variable for saturation increase (1.5 means 50% increase)
SATURATION_INCREASE = 1.5

def make_color_more_saturated(tile_color):
    """
    Increase the saturation of a given tile color.
    
    Args:
    tile_color (int): The original tile color as a 32-bit integer.
    
    Returns:
    int: The new tile color with increased saturation.
    """
    # Extract RGB from the 32-bit hex tile color (RGBA format)
    r = ((tile_color >> 24) & 0xFF) / 255.0
    g = ((tile_color >> 16) & 0xFF) / 255.0
    b = ((tile_color >> 8) & 0xFF) / 255.0
    
    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    # Increase the saturation (up to a max of 1.0)
    s = min(s * SATURATION_INCREASE, 1.0)
    
    # Convert HSV back to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    
    # Convert RGB back to the 32-bit hex tile color (keeping alpha at 0xFF)
    new_tile_color = int(r * 255) << 24 | int(g * 255) << 16 | int(b * 255) << 8 | 0xFF
    return new_tile_color

def is_node_animated(node):
    """
    Check if any knob in the node is animated.
    
    Args:
    node (nuke.Node): The node to check.
    
    Returns:
    bool: True if the node has any animated knob, False otherwise.
    """
    for knob in node.knobs().values():
        if knob.isAnimated():
            return True
    return False

def set_nodes_more_saturated_if_animated():
    """
    Increase the saturation of tile colors for all animated nodes in the script.
    """
    for node in nuke.allNodes():
        if is_node_animated(node):
            current_color = node['tile_color'].value()
            new_color = make_color_more_saturated(current_color)
            node['tile_color'].setValue(new_color)

def main():
    """
    Main function to run the script.
    """
    set_nodes_more_saturated_if_animated()
    nuke.message("Animated nodes have been made more saturated!")

# Run the main function when the script is executed
if __name__ == "__main__":
    main()
