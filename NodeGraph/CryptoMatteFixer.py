# CryptoMatteFixer.py v1.0
#
# This script fixes the issue with Cryptomatte nodes losing their layer selection when copied.
# It stores the selected crypto layer in a custom knob and restores it when the node is copied or pasted.

import nuke

# User variable to enable/disable the fix
ENABLE_CRYPTOMATTE_FIX = True

def store_crypto_layer():
    """Store the selected crypto layer in a custom knob."""
    node = nuke.thisNode()
    if node.Class() in ['Cryptomatte', 'Cryptomatte2']:
        selected_layer = node['cryptoLayer'].value()
        if 'storedCryptoLayer' not in node.knobs():
            k = nuke.String_Knob('storedCryptoLayer', 'Stored Crypto Layer')
            k.setVisible(False)
            node.addKnob(k)
        node['storedCryptoLayer'].setValue(selected_layer)

def restore_crypto_layer():
    """Restore the stored crypto layer if available."""
    node = nuke.thisNode()
    if node.Class() in ['Cryptomatte', 'Cryptomatte2']:
        if 'storedCryptoLayer' in node.knobs():
            stored_layer = node['storedCryptoLayer'].value()
            if stored_layer:
                node['cryptoLayer'].setValue(stored_layer)

def setup_callbacks():
    """Set up the necessary callbacks for Cryptomatte nodes."""
    nuke.addOnUserCreate(store_crypto_layer, nodeClass='Cryptomatte')
    nuke.addOnUserCreate(store_crypto_layer, nodeClass='Cryptomatte2')
    nuke.addOnCreate(restore_crypto_layer, nodeClass='Cryptomatte')
    nuke.addOnCreate(restore_crypto_layer, nodeClass='Cryptomatte2')
    nuke.addKnobChanged(store_crypto_layer, nodeClass='Cryptomatte')
    nuke.addKnobChanged(store_crypto_layer, nodeClass='Cryptomatte2')

def initialize_cryptomatte_fixer():
    """Initialize the Cryptomatte fixer if enabled."""
    if ENABLE_CRYPTOMATTE_FIX:
        setup_callbacks()
        print("CryptoMatteFixer initialized. Layer selection will be preserved when copying nodes.")
    else:
        print("CryptoMatteFixer is disabled. Set ENABLE_CRYPTOMATTE_FIX to True to enable.")

# Run the initialization
initialize_cryptomatte_fixer()
