# CryptoMatteFixer.py v2.6
#
# This script fixes issues with Cryptomatte nodes by detecting the correct layer
# based on the keyer expression and updating the node accordingly.

import nuke
import re

# User variable to enable/disable the fix
ENABLE_CRYPTOMATTE_FIX = True

def detect_crypto_layer(node):
    """Detect the correct Cryptomatte layer based on the keyer expression."""
    expression = node['expression'].value()
    
    layer_patterns = {
        'cryptomatte_mat': r'cryptomatte_mat\d+\.',
        'cryptomatte_obj': r'cryptomatte_obj\d+\.',
        'cryptomatte_asset': r'cryptomatte_asset\d+\.'
    }
    
    for layer, pattern in layer_patterns.items():
        if re.search(pattern, expression):
            return layer
    
    # If no match found, return the current layer
    return node['cryptoLayer'].value()

def update_crypto_node(node):
    """Update the Cryptomatte node with the correct layer."""
    current_layer = node['cryptoLayer'].value()
    detected_layer = detect_crypto_layer(node)
    
    if current_layer != detected_layer:
        node['cryptoLayer'].setValue(detected_layer)
        print(f"Updated {node.name()} from {current_layer} to {detected_layer}")
    
    # Update label
    label = detected_layer.replace('cryptomatte_', '')
    node['label'].setValue(label)

def process_cryptomattes():
    """Process all Cryptomatte nodes in the script."""
    processed_nodes = 0
    mismatched_nodes = 0
    
    for node in nuke.allNodes():
        if node.Class() in ['Cryptomatte', 'Cryptomatte2']:
            current_layer = node['cryptoLayer'].value()
            update_crypto_node(node)
            if current_layer != node['cryptoLayer'].value():
                mismatched_nodes += 1
            processed_nodes += 1
    
    if processed_nodes > 0:
        print(f"Processed {processed_nodes} Cryptomatte node(s). "
              f"Fixed {mismatched_nodes} node(s) with mismatched layers.")
    else:
        print("No Cryptomatte nodes found in the script.")

def on_node_create():
    """Callback function for when a Cryptomatte node is created."""
    node = nuke.thisNode()
    if node.Class() in ['Cryptomatte', 'Cryptomatte2']:
        update_crypto_node(node)

def on_knob_changed():
    """Callback function for when a knob is changed on a Cryptomatte node."""
    node = nuke.thisNode()
    knob = nuke.thisKnob()
    if node.Class() in ['Cryptomatte', 'Cryptomatte2']:
        if knob.name() in ['expression', 'cryptoLayer', 'in00', 'cryptoLayerChoice']:
            update_crypto_node(node)

def on_script_load():
    """Callback function for when a script is loaded."""
    process_cryptomattes()

def setup_callbacks():
    """Set up the necessary callbacks for Cryptomatte nodes."""
    nuke.addOnCreate(on_node_create, nodeClass='Cryptomatte')
    nuke.addOnCreate(on_node_create, nodeClass='Cryptomatte2')
    nuke.addKnobChanged(on_knob_changed, nodeClass='Cryptomatte')
    nuke.addKnobChanged(on_knob_changed, nodeClass='Cryptomatte2')
    nuke.addOnScriptLoad(on_script_load)

def run_cryptomatte_fixer():
    """Run the Cryptomatte fixer manually."""
    if ENABLE_CRYPTOMATTE_FIX:
        process_cryptomattes()
        nuke.message("CryptoMatteFixer has processed all Cryptomatte nodes.")
    else:
        nuke.message("CryptoMatteFixer is disabled. Set ENABLE_CRYPTOMATTE_FIX to True to enable.")

def initialize_cryptomatte_fixer():
    """Initialize the Cryptomatte fixer if enabled."""
    if ENABLE_CRYPTOMATTE_FIX:
        setup_callbacks()
        print("CryptoMatteFixer initialized. Cryptomatte layers will be automatically detected.")
    else:
        print("CryptoMatteFixer is disabled. Set ENABLE_CRYPTOMATTE_FIX to True to enable.")

# Run the initialization
initialize_cryptomatte_fixer()

# To add a menu item for manual execution, add this to your menu.py:
# nuke.menu('Nuke').addCommand('Custom/Fix Cryptomatte Nodes', run_cryptomatte_fixer)
