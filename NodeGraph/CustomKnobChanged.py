# AnimatedNodeSaturator.py v1.2.1
#
# This script increases the saturation of the tile color for all animated nodes in a Nuke script.
# If a node has any animated knobs, its tile color will turn red and "Animated" will be added to its label.
# It also adds "Mix: [value mix]" to the label when the mix knob is changed, and removes it when mix is 1.
# Otherwise, it stays at its default color and label.

import nuke

def update_node_color_and_label(node):
    """
    Update the color and label of a single node based on its animation status and mix value.
    If any of the node's knobs are animated, the tile color will change to red
    and "Animated" will be added to its label. If the node has a mix knob not equal to 1, its value will be shown in the label.
    """
    is_animated = False
    has_mix = 'mix' in node.knobs()
    
    # Iterate through all knobs in the node
    for knob in node.knobs().values():
        if knob.isAnimated():
            is_animated = True
            break
    
    # Prepare the label components
    label_components = []
    if is_animated:
        label_components.append("Animated")
    
    if has_mix:
        mix_value = node['mix'].value()
        if mix_value != 1.0:
            label_components.append(f"Mix: {mix_value:.2f}")
    
    # Get the original label (excluding our additions)
    original_label = node['label'].value()
    original_parts = original_label.split('\n')
    original_label = next((part for part in original_parts if not part.startswith(("Animated", "Mix:"))), "")
    
    # Combine all label components
    if original_label:
        label_components.append(original_label)
    new_label = '\n'.join(label_components)
    
    # Update the node color and label
    if is_animated:
        node['tile_color'].setValue(0xD00000FF)  # Set node's tile color to red (RGBA hexadecimal)
    else:
        node['tile_color'].setValue(0)  # Reset tile color to default (no color)
    
    node['label'].setValue(new_label)

def on_knob_changed():
    """
    Callback function triggered when any knob of a node is changed.
    Updates the node's color and label dynamically if any of its knobs become animated or if the mix value changes.
    """
    node = nuke.thisNode()
    knob = nuke.thisKnob()
    
    # Prevent recursive color/label change if the 'tile_color' or 'label' knob is itself changed
    if knob.name() in ['tile_color', 'label']:
        return
    
    update_node_color_and_label(node)

def on_user_create():
    """
    Callback function triggered when a user creates a new node.
    Updates the color and label of the new node based on its animation status and mix value.
    """
    node = nuke.thisNode()
    update_node_color_and_label(node)

def setup_callbacks():
    """
    Set up the necessary callbacks for all existing and future nodes.
    These callbacks will handle changes to nodes and automatically update their tile colors and labels.
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
    Update the tile color and label of all nodes already present in the current Nuke script.
    This ensures that existing nodes' colors and labels reflect their animation status and mix value.
    """
    for node in nuke.allNodes():
        update_node_color_and_label(node)

def initialize_dynamic_coloring():
    """
    Initialize the dynamic node coloring and labeling system.
    This sets up the callbacks and updates the colors and labels of all existing nodes.
    """
    setup_callbacks()
    update_all_existing_nodes()

# Run the initialization process when the script is loaded
initialize_dynamic_coloring()

# Future Update Plans (v1.3):
# - Implement a user interface to allow customization of the animated node color and label text.
# - Add an option to toggle the visibility of the "Animated" and "Mix" labels.
# - Explore the possibility of gradual color changes based on the complexity of animations in the node.
# - Add support for tracking and displaying values of other commonly used knobs (e.g., 'opacity', 'which').
