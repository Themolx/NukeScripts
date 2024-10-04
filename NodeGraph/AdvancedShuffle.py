# DynamicShuffleLabeler.py v2.0

import nuke
import uuid

# User variable for vertical spacing (in pixels)
VERTICAL_SPACING = 10  # You can adjust this value as needed

# Unique identifier for nodes created by this script (hidden from user)
SCRIPT_ID = str(uuid.uuid4())

def is_keep_rgba_node(node):
    """
    Check if the given node is a Remove node set to keep rgb or rgba channels.
    """
    return (node.Class() == 'Remove' and 
            node['operation'].value() == 'keep' and 
            node['channels'].value() in ['rgba', 'rgb'])

def find_keep_rgba_node(shuffle_node):
    """
    Find an existing KeepRGBA node connected to the given Shuffle node.
    """
    for dep in shuffle_node.dependent():
        if is_keep_rgba_node(dep) and dep.input(0) == shuffle_node:
            return dep
    return None

def update_shuffle_node(node):
    """
    Update the label and postage stamp of a Shuffle or Shuffle2 node based on its input.
    Only add a label if the input is not 'rgba'.
    """
    if node.Class() in ['Shuffle', 'Shuffle2']:
        # Get the input value
        if node.Class() == 'Shuffle':
            in1_value = node['in1'].value()
        else:  # Shuffle2
            in1_value = node['in1'].value().split('.')[-1]  # Get the last part of the in1 value
        
        # Set label and postage stamp based on input
        if in1_value.lower() != 'rgba':
            node['label'].setValue('[value in1]')
            node['postage_stamp'].setValue(True)
            print(f"Updated {node.name()}: Label set to '[value in1]', postage stamp turned on (in1: {in1_value})")
        else:
            node['label'].setValue('')  # Clear the label if input is 'rgba'
            node['postage_stamp'].setValue(False)
            print(f"Updated {node.name()}: Label cleared, postage stamp turned off (in1: rgba)")

def on_user_create():
    """
    Callback function triggered when a user creates a new node.
    """
    node = nuke.thisNode()
    update_shuffle_node(node)

def on_knob_changed():
    """
    Callback function triggered when any knob of a node is changed.
    """
    node = nuke.thisNode()
    knob = nuke.thisKnob()
    
    # Update if the 'in1' knob is changed or if it's a new node (no knob specified)
    if knob is None or knob.name() == 'in1':
        update_shuffle_node(node)

def setup_callbacks():
    """
    Set up the necessary callbacks for all existing and future Shuffle and Shuffle2 nodes.
    """
    # Remove any existing callbacks to prevent duplicates
    nuke.removeOnUserCreate(on_user_create)
    nuke.removeKnobChanged(on_knob_changed)
    
    # Add callbacks for Shuffle nodes
    nuke.addOnUserCreate(on_user_create, nodeClass='Shuffle')
    nuke.addKnobChanged(on_knob_changed, nodeClass='Shuffle')
    
    # Add callbacks for Shuffle2 nodes
    nuke.addOnUserCreate(on_user_create, nodeClass='Shuffle2')
    nuke.addKnobChanged(on_knob_changed, nodeClass='Shuffle2')

def update_existing_shuffle_nodes():
    """
    Update all existing Shuffle and Shuffle2 nodes in the script.
    """
    for node in nuke.allNodes():
        if node.Class() in ['Shuffle', 'Shuffle2']:
            update_shuffle_node(node)

def initialize_dynamic_shuffle_labeler():
    """
    Initialize the dynamic Shuffle node labeling system.
    """
    setup_callbacks()
    update_existing_shuffle_nodes()

# Run the initialization process when the script is loaded
initialize_dynamic_shuffle_labeler()

print(f"Dynamic Shuffle Labeler v2.0 initialized. Vertical spacing set to {VERTICAL_SPACING} pixels.")
