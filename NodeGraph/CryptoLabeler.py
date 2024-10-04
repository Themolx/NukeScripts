# CryptoLabeler.py v1.1
#
# This script adds a label to Cryptomatte nodes indicating the selected input layer
# and the contents of the Matte List knob.
# It updates the label whenever the Layer Selection or Matte List knobs are changed.

import nuke

def update_crypto_label():
    """
    Update the label of a Cryptomatte node based on its selected input layer
    and the contents of the Matte List knob.
    """
    node = nuke.thisNode()
    knob = nuke.thisKnob()
    
    if node.Class() in ['Cryptomatte', 'Cryptomatte2']:
        selected_layer = node['cryptoLayer'].value()
        matte_list = node['matteList'].value().strip()
        
        label_parts = [f"Input: {selected_layer}"]
        
        if matte_list:
            # Truncate matte_list if it's too long
            max_length = 30
            if len(matte_list) > max_length:
                matte_list = matte_list[:max_length] + "..."
            label_parts.append(f"Matte: {matte_list}")
        
        node['label'].setValue("\n".join(label_parts))

def setup_crypto_callback():
    """
    Set up the necessary callback for all existing and future Cryptomatte nodes.
    """
    nuke.removeKnobChanged(update_crypto_label)
    nuke.addKnobChanged(update_crypto_label, nodeClass='Cryptomatte')
    nuke.addKnobChanged(update_crypto_label, nodeClass='Cryptomatte2')

def update_existing_crypto_nodes():
    """
    Update the label of all existing Cryptomatte nodes in the current Nuke script.
    """
    for node in nuke.allNodes():
        if node.Class() in ['Cryptomatte', 'Cryptomatte2']:
            update_crypto_label()

def initialize_crypto_labeler():
    """
    Initialize the Cryptomatte labeling system.
    """
    setup_crypto_callback()
    update_existing_crypto_nodes()

# Run the initialization process when the script is loaded
initialize_crypto_labeler()

print("CryptoLabeler v1.1 initialized. Cryptomatte nodes will now display their input layer and Matte List in the label.")
