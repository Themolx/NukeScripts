from __future__ import with_statement

import nuke
import os
import re

# User variables
WORK_ROOT = "Z:/20105_Pysna_film/work/FILM"
LIGHTNING_RENDER_SCRIPT = "Y:/20105_Pysna_film/tmp/martin.tomek/BetaScripts/LoadLightningRenderFromRender.py"

def print_debug(message):
    print(f"DEBUG: {message}")

def get_read_node_info(node):
    """Extract sequence, shot, and version information from the Read node."""
    try:
        file_path = node['file'].value()
        
        pattern = r'SQ(\d+)/SH(\d+)/compositing/render/v(\d+)/pp_FILM_SQ\d+_SH\d+_comp_v(\d+)'
        match = re.search(pattern, file_path)
        
        if match:
            seq_num, shot_num, render_version, comp_version = match.groups()
            return seq_num, shot_num, comp_version
        else:
            nuke.message("Invalid file path format in the Read node.")
            return None
    except:
        nuke.message("Error reading file path from node.")
        return None

def find_comp_file(seq_num, shot_num, version):
    """Find the comp file based on extracted information."""
    comp_dir = os.path.join(WORK_ROOT, f"SQ{seq_num}", f"SH{shot_num}", "compositing", "work")
    comp_file = f"FILM_SQ{seq_num}_SH{shot_num}_comp_v{version}.nk"
    return os.path.normpath(os.path.join(comp_dir, comp_file))

def open_comp_file():
    """Open the Nuke comp file corresponding to the Read node."""
    node = nuke.thisNode()
    try:
        info = get_read_node_info(node)
        if info:
            seq_num, shot_num, version = info
            comp_file = find_comp_file(seq_num, shot_num, version)
            
            if os.path.exists(comp_file):
                if nuke.ask(f"Do you want to open the comp file:\n{comp_file}"):
                    nuke.scriptOpen(comp_file)
                    nuke.message(f"Successfully opened comp file:\n{comp_file}")
                else:
                    nuke.message("Operation cancelled by user.")
            else:
                nuke.message(f"Comp file not found:\n{comp_file}\n\nPlease check if the file exists.")
    except Exception as e:
        nuke.message(f"An unexpected error occurred:\n{str(e)}")

def create_crypto_setup(read_node, selected_node):
    # Create Cryptomatte2 node
    crypto_node = nuke.nodes.Cryptomatte2(inputs=[read_node])
    crypto_node['name'].setValue(f"Crypto_{read_node.name()}")
    
    # Create Shuffle node with correct inputs and channel routing
    shuffle_node = nuke.nodes.Shuffle(
        name=f"Shuffle_{read_node.name()}",
        inputs=[selected_node, crypto_node]  # Switch inputs: input 1 to selected node, input 2 to Crypto
    )
    shuffle_node['in'].setValue('alpha')
    shuffle_node['in2'].setValue('rgba')
    shuffle_node['red'].setValue('red2')
    shuffle_node['green'].setValue('green2')
    shuffle_node['blue'].setValue('blue2')
    shuffle_node['alpha'].setValue('red')
    
    # Create Premult node
    premult_node = nuke.nodes.Premult(
        name=f"Premult_{read_node.name()}",
        inputs=[shuffle_node]
    )
    return crypto_node, shuffle_node, premult_node

def load_lightning_renders():
    """Load lightning renders and set up Cryptomatte nodes."""
    try:
        # Normalize the path to use correct slashes for the operating system
        script_path = os.path.normpath(LIGHTNING_RENDER_SCRIPT)
        print_debug(f"Attempting to load script from: {script_path}")
        
        # Read the content of the script file
        with open(script_path, 'r') as file:
            script_content = file.read()
        
        # Execute the script content within the correct Nuke context
        with nuke.Root():
            exec(script_content, {
                "print_debug": print_debug,
                "create_crypto_setup": create_crypto_setup,
                "nuke": nuke,
                "__file__": script_path
            })
    except Exception as e:
        nuke.message(f"An unexpected error occurred while loading lightning renders:\n{str(e)}")
        print_debug(f"Error details: {str(e)}")

def add_custom_tab(node):
    """Add custom MT tab and knobs to the Read node."""
    # Add MT tab
    mt_tab = nuke.Tab_Knob('MT', 'MT')
    node.addKnob(mt_tab)
    
    open_comp_btn = nuke.PyScript_Knob('open_comp', 'Open Comp File', 'open_comp_file()')
    node.addKnob(open_comp_btn)
    
    load_lightning_btn = nuke.PyScript_Knob('load_lightning', 'Load Lightning Renders', 'load_lightning_renders()')
    node.addKnob(load_lightning_btn)

def create_advanced_read_node():
    """Create an advanced Read node with all required knobs."""
    read = nuke.createNode("Read")
    
    # Set default values
    read['file_type'].setValue('exr')
    read['tile_color'].setValue(0xff0000ff)
    
    # Add custom MT tab and knobs
    add_custom_tab(read)
    
    return read

# Replace the default Read node with our advanced one
nuke.menu('Nodes').addCommand('Image/Read', create_advanced_read_node, 'r', icon='Read.png', shortcutContext=2)

# This ensures custom MT tab is added to any Read nodes created through other means
def onCreateCallback():
    node = nuke.thisNode()
    if node.Class() == 'Read':
        add_custom_tab(node)

# Register the callback
nuke.addOnCreate(onCreateCallback, nodeClass='Read')
