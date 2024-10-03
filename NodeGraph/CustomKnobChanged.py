# AnimatedNodeSaturator.py v1.0.2
#
# This script increases the saturation of the tile color for all animated nodes in a Nuke script.
# If a node has any animated knobs, its tile color will turn red. Otherwise, it stays at its default color.
# Version 1.0.2 includes minor improvements and prepares for future updates that will make animated nodes' colors brighter.

import nuke

def update_node_color(node):
    """
    Update the color of a single node based on its animation status.
    If any of the node's knobs are animated, the tile color will change to red.
    """
    is_animated = False  # Flag to track if the node has any animated knobs

    # Iterate through all knobs in the node
    for knob in node.knobs().values():
        if knob.isAnimated():
            is_animated = True  # If any knob is animated, set flag to True
            break  # Exit loop as we only need one animated knob to change the color
    
    if is_animated:
        node['tile_color'].setValue(0xD00000FF)  # Set node's tile color to red (RGBA hexadecimal)
    else:
        node['tile_color'].setValue(0)  # Reset tile color to default (no color)

def on_knob_changed():
    """
    Callback function triggered when any knob of a node is changed.
    Updates the node's color dynamically if any of its knobs become animated.
    """
    node = nuke.thisNode()  # Get the node where the knob was changed
    knob = nuke.thisKnob()  # Get the knob that was changed

    # Prevent recursive color change if the 'tile_color' knob is itself changed
    if knob.name() == 'tile_color':
        return  # Exit function if 'tile_color' knob is the one being changed

    # Call function to update the node's color
    update_node_color(node)

def on_user_create():
    """
    Callback function triggered when a user creates a new node.
    Updates the color of the new node based on its animation status.
    """
    node = nuke.thisNode()  # Get the newly created node
    update_node_color(node)  # Update its color according to its animation state

def setup_callbacks():
    """
    Set up the necessary callbacks for all existing and future nodes.
    These callbacks will handle changes to nodes and automatically update their tile colors.
    """
    # First, remove any pre-existing callbacks to prevent duplicate triggers
    nuke.removeKnobChanged(on_knob_changed)
    nuke.removeOnUserCreate(on_user_create)
    
    # Add new callback for knob changes across all nodes
    nuke.addKnobChanged(on_knob_changed, nodeClass='*')

    # Add callback for when new nodes are created by the user
    nuke.addOnUserCreate(on_user_create, nodeClass='*')

def update_all_existing_nodes():
    """
    Update the tile color of all nodes already present in the current Nuke script.
    This ensures that existing nodes' colors reflect their animation status.
    """
    for node in nuke.allNodes():  # Loop through all nodes in the current script
        update_node_color(node)  # Update each node's tile color

def initialize_dynamic_coloring():
    """
    Initialize the dynamic node coloring system.
    This sets up the callbacks and updates the colors of all existing nodes.
    """
    setup_callbacks()  # Set up the callbacks for dynamic color updating
    update_all_existing_nodes()  # Update the tile color of all existing nodes

# Run the initialization process when the script is loaded
initialize_dynamic_coloring()


# Future Update Plans (v1.1):
# - In the next version, we plan to further enhance the visual feedback by making the tile colors of animated nodes brighter.
#   This will involve adjusting the brightness of the tile color dynamically based on the animation state of the node's knobs.
# - Nodes with animated knobs will not only turn red but will also have an increased brightness for better visual distinction.
