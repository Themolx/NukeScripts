# AnimatedNodeLabeler.py v2.2.0
#
# This script modifies the color of animatable Nuke nodes when they have animated values.
# It adds labels to indicate if a node is animated and shows the mix value when applicable.
# The color and label functionalities can be toggled independently.

import nuke
import colorsys

# User variables
ENABLE_DYNAMIC_LABELING = True  # Controls label updates (Animated, Mix)
ENABLE_COLOR_CHANGES = True    # Controls color changes for animated nodes
HUE_CHANGE = 0.02  # Amount to change the hue (0.0 to 1.0)
SATURATION_CHANGE = 0.5  # Amount to change the saturation (-1.0 to 1.0)
VALUE_CHANGE = 1  # Amount to change the value/brightness (-1.0 to 1.0)

# List of node classes to exclude from color modification
EXCLUDED_NODE_CLASSES = ['BackdropNode', 'StickyNote', 'Dot']

def is_valid_node(node):
    """
    Check if the node is valid and not in the excluded classes.
    """
    try:
        return node and node.Class() not in EXCLUDED_NODE_CLASSES
    except:
        return False

def modify_node_color(node, is_animated):
    """
    Modify the color of a given node if it's animated and color changes are enabled.
    Preserve custom colors for groups and other nodes.
    """
    if not ENABLE_COLOR_CHANGES or not is_valid_node(node):
        return
    try:
        # Get the current node color
        current_color = node['tile_color'].value()
        
        # If the current color is not the default (0), preserve it
        if current_color != 0:
            return
        
        # Get the default node color, skip if it's unavailable
        default_color = nuke.defaultNodeColor(node.Class())
        if default_color is None:
            return
        
        if is_animated:
            # Extract RGB values
            r = ((default_color >> 24) & 0xff) / 255.0
            g = ((default_color >> 16) & 0xff) / 255.0
            b = ((default_color >> 8) & 0xff) / 255.0
            
            # Convert to HSV for color modification
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            h = (h + HUE_CHANGE) % 1.0
            s = max(0, min(1, s + SATURATION_CHANGE))
            v = max(0, min(1, v + VALUE_CHANGE))
            
            # Convert back to RGB and set the new color
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            new_color = int(r * 255) << 24 | int(g * 255) << 16 | int(b * 255) << 8 | 0xff
        else:
            new_color = default_color
        
        # Apply the new color
        node['tile_color'].setValue(new_color)
    except Exception as e:
        print(f"Error modifying color for {node.name()}: {str(e)}")

def update_node_label(node):
    """
    Update the label of a single node based on its animation status and mix value.
    """
    if not ENABLE_DYNAMIC_LABELING or not is_valid_node(node):
        return False

    try:
        is_animated = any(knob.isAnimated() for knob in node.knobs().values())
        has_mix = 'mix' in node.knobs()
        
        label_components = []
        if is_animated:
            label_components.append("Animated")
        
        if has_mix:
            mix_value = node['mix'].value()
            if mix_value != 1.0:
                label_components.append(f"Mix: {mix_value:.2f}")
        
        original_label = node['label'].value()
        original_parts = original_label.split('\n')
        original_label = next((part for part in original_parts if not part.startswith(("Animated", "Mix:"))), "")
        
        if original_label:
            label_components.append(original_label)
        new_label = '\n'.join(label_components)
        
        node['label'].setValue(new_label)
        
        return is_animated
    except Exception as e:
        print(f"Error updating label for {node.name()}: {str(e)}")
        return False

def on_knob_changed():
    """
    Callback function triggered when any knob of a node is changed.
    Updates the node's color and/or label based on animation status and enabled functionalities.
    """
    if not (ENABLE_DYNAMIC_LABELING or ENABLE_COLOR_CHANGES):
        return

    node = nuke.thisNode()
    if not is_valid_node(node):
        return

    try:
        is_animated = update_node_label(node) if ENABLE_DYNAMIC_LABELING else any(knob.isAnimated() for knob in node.knobs().values())
        if ENABLE_COLOR_CHANGES:
            modify_node_color(node, is_animated)
    except Exception as e:
        print(f"Error in on_knob_changed for {node.name()}: {str(e)}")

def setup_callback():
    """
    Set up the necessary callback for all existing and future nodes.
    """
    nuke.removeKnobChanged(on_knob_changed)
    nuke.addKnobChanged(on_knob_changed, nodeClass='*')

def update_all_existing_nodes():
    """
    Update the label and/or color of all nodes already present in the current Nuke script.
    """
    for node in nuke.allNodes():
        if is_valid_node(node):
            try:
                is_animated = update_node_label(node) if ENABLE_DYNAMIC_LABELING else any(knob.isAnimated() for knob in node.knobs().values())
                if ENABLE_COLOR_CHANGES:
                    modify_node_color(node, is_animated)
            except Exception as e:
                print(f"Error updating {node.name()}: {str(e)}")

def initialize_dynamic_labeling_and_coloring():
    """
    Initialize the dynamic node labeling and coloring system if either functionality is enabled.
    """
    if ENABLE_DYNAMIC_LABELING or ENABLE_COLOR_CHANGES:
        setup_callback()
        update_all_existing_nodes()
    else:
        print("Both dynamic labeling and coloring are disabled.")

def toggle_dynamic_labeling():
    """
    Toggle the dynamic labeling functionality.
    """
    global ENABLE_DYNAMIC_LABELING
    ENABLE_DYNAMIC_LABELING = not ENABLE_DYNAMIC_LABELING
    print(f"Dynamic labeling {'enabled' if ENABLE_DYNAMIC_LABELING else 'disabled'}.")
    initialize_dynamic_labeling_and_coloring()

def toggle_color_changes():
    """
    Toggle the color change functionality.
    """
    global ENABLE_COLOR_CHANGES
    ENABLE_COLOR_CHANGES = not ENABLE_COLOR_CHANGES
    print(f"Color changes {'enabled' if ENABLE_COLOR_CHANGES else 'disabled'}.")
    initialize_dynamic_labeling_and_coloring()

# Run the initialization process when the script is loaded
initialize_dynamic_labeling_and_coloring()

# You can call toggle_dynamic_labeling() or toggle_color_changes() to turn each functionality on or off as needed
