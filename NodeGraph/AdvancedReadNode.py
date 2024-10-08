# read_node_callback.py
import nuke
import os
import re

# User variables
WORK_ROOT = "Z:/20105_Pysna_film/work/FILM"

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

def add_mt_tab(node):
    """Add the MT tab with the Open Comp button to the Read node."""
    # Only add if it doesn't already exist
    if 'MT' not in node.knobs():
        tab = nuke.Tab_Knob('MT', 'MT')
        node.addKnob(tab)
        
        open_comp_btn = nuke.PyScript_Knob('open_comp', 'Open Comp File', 'open_comp_file()')
        node.addKnob(open_comp_btn)

def create_custom_read_node():
    """Create a custom Read node with all required knobs."""
    read = nuke.createNode("Read")
    
    # Set default values
    read['file_type'].setValue('exr')
    read['tile_color'].setValue(0xff0000ff)
    
    # Add PFX tab and knobs
    tab = nuke.Tab_Knob('PFX', 'PFX')
    read.addKnob(tab)
    
    fast_tier_label = nuke.Text_Knob('fast_tier_storage_label', ' ', 'FAST TIER STORAGE')
    read.addKnob(fast_tier_label)
    
    status = nuke.Text_Knob('fast_tier_storage_status', 'Status:             ', 'not used')
    read.addKnob(status)
    
    sequence_status = nuke.Text_Knob('fast_tier_storage_sequence_status', 'File sequence:   ', 'not localized')
    read.addKnob(sequence_status)
    
    localize_btn = nuke.PyScript_Knob('try_to_localize_btn', '        Try to localize        ', 
                                      'from sc.nuke.pfx_nodes import pfx_read\npfx_read.try_to_localize_btn_hndl()')
    read.addKnob(localize_btn)
    
    tier_switch_btn = nuke.PyScript_Knob('tier_switch_btn', '     Switch to Fast Tier     ',
                                         'from sc.nuke.pfx_nodes import pfx_read\npfx_read.tier_switch_btn_hndl()')
    read.addKnob(tier_switch_btn)
    
    # Add MT tab and button
    add_mt_tab(read)
    
    return read

# Replace the default Read node with our custom one
nuke.menu('Nodes').addCommand('Image/Read', create_custom_read_node, 'r', icon='Read.png', shortcutContext=2)

# This ensures the MT tab is added to any Read nodes created through other means
def onCreateCallback():
    node = nuke.thisNode()
    if node.Class() == 'Read':
        add_mt_tab(node)

# Register the callback
nuke.addOnCreate(onCreateCallback, nodeClass='Read')
