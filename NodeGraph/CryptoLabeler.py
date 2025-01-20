# CryptoMatteTool.py v1.2

import nuke
import uuid

# User variable for vertical spacing (in pixels)
VERTICAL_SPACING = 50

# Unique identifier for nodes created by this script (hidden from user)
SCRIPT_ID = str(uuid.uuid4())

def is_our_keep_rgba_node(node):
    """Check if the given node is a Remove node created by this script."""
    return (node.Class() == 'Remove' and 
            node['operation'].value() == 'keep' and 
            node['channels'].value() == 'rgba' and
            node.knob('script_id') and node['script_id'].value() == SCRIPT_ID)

def find_our_keep_rgba_node(crypto_node):
    """Find an existing KeepRGBA node connected to the given Cryptomatte node and created by this script."""
    for dep in crypto_node.dependent():
        if is_our_keep_rgba_node(dep) and dep.input(0) == crypto_node:
            return dep
    return None

def create_keep_rgba_node(crypto_node):
    """Create a Remove node set to "keep rgba" after the given Cryptomatte node."""
    remove_node = nuke.nodes.Remove()
    remove_node['operation'].setValue('keep')
    remove_node['channels'].setValue('rgba')
    remove_node['label'].setValue("keep [value channels]")
    
    script_id_knob = nuke.String_Knob('script_id', 'Script ID')
    script_id_knob.setFlag(nuke.INVISIBLE)
    remove_node.addKnob(script_id_knob)
    remove_node['script_id'].setValue(SCRIPT_ID)
    
    remove_node.setInput(0, crypto_node)
    
    # Only set position if it's safe to do so
    try:
        x = crypto_node.xpos()
        y = crypto_node.ypos() + crypto_node.screenHeight() + VERTICAL_SPACING
        remove_node.setXYpos(x, y)
    except:
        print(f"Warning: Unable to set position for Remove node after {crypto_node.name()}")
    
    return remove_node

def update_crypto_node(node):
    """Update the label and add/update a Remove node after a Cryptomatte node."""
    if node.Class() in ['Cryptomatte', 'Cryptomatte2']:
        # Update label
        selected_layer = node['cryptoLayer'].value()
        matte_list = node['matteList'].value().strip()
        
        label_parts = [f"Input: {selected_layer}"]
        
        if matte_list:
            max_length = 30
            if len(matte_list) > max_length:
                matte_list = matte_list[:max_length] + "..."
            label_parts.append(f"Matte: {matte_list}")
        
        node['label'].setValue("\n".join(label_parts))

        # Check for existing KeepRGBA node created by this script
        our_keep_rgba = find_our_keep_rgba_node(node)
        
        if not our_keep_rgba:
            keep_rgba_node = create_keep_rgba_node(node)
            print(f"Added KeepRGBA node after {node.name()}")
        else:
            # Update position of existing Remove node if it's safe to do so
            try:
                x = node.xpos()
                y = node.ypos() + node.screenHeight() + VERTICAL_SPACING
                our_keep_rgba.setXYpos(x, y)
            except:
                print(f"Warning: Unable to update position for Remove node after {node.name()}")

def on_user_create():
    """Callback function triggered when a user creates a new node."""
    node = nuke.thisNode()
    if node and node.Class() in ['Cryptomatte', 'Cryptomatte2']:
        update_crypto_node(node)

def on_knob_changed():
    """Callback function triggered when any knob of a node is changed."""
    node = nuke.thisNode()
    knob = nuke.thisKnob()
    
    if node and node.Class() in ['Cryptomatte', 'Cryptomatte2']:
        # List of knobs that should trigger an update
        update_knobs = ['cryptoLayer', 'matteList']
        if knob is None or knob.name() in update_knobs:
            update_crypto_node(node)

def setup_callbacks():
    """Set up the necessary callbacks for all existing and future Cryptomatte nodes."""
    nuke.removeOnUserCreate(on_user_create)
    nuke.removeKnobChanged(on_knob_changed)
    
    nuke.addOnUserCreate(on_user_create, nodeClass='Cryptomatte')
    nuke.addOnUserCreate(on_user_create, nodeClass='Cryptomatte2')
    nuke.addKnobChanged(on_knob_changed, nodeClass='Cryptomatte')
    nuke.addKnobChanged(on_knob_changed, nodeClass='Cryptomatte2')

def update_existing_crypto_nodes():
    """Update all existing Cryptomatte nodes in the script."""
    for node in nuke.allNodes():
        if node.Class() in ['Cryptomatte', 'Cryptomatte2']:
            update_crypto_node(node)

def initialize_crypto_matte_tool():
    """Initialize the CryptoMatte Tool system."""
    setup_callbacks()
    nuke.addOnScriptLoad(update_existing_crypto_nodes)
    print(f"CryptoMatte Tool v1.2 initialized. Vertical spacing set to {VERTICAL_SPACING} pixels.")

# Run the initialization process when the script is loaded
initialize_crypto_matte_tool()

