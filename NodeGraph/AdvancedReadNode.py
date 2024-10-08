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
        return None
    except:
        return None

def find_comp_file(seq_num, shot_num, version):
    """Find the comp file based on extracted information."""
    comp_dir = os.path.join(WORK_ROOT, f"SQ{seq_num}", f"SH{shot_num}", "compositing", "work")
    comp_file = f"FILM_SQ{seq_num}_SH{shot_num}_comp_v{version}.nk"
    return os.path.normpath(os.path.join(comp_dir, comp_file))

def open_comp_file_from_node():
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
                nuke.message(f"Comp file not found:\n{comp_file}\n\nPlease check if the file exists.")
    except Exception as e:
        nuke.message(f"An unexpected error occurred:\n{str(e)}")

def add_mt_tab(node):
    """Add the MT tab with the Open Comp button to the Read node."""
    # Check if MT tab already exists
    existing_knobs = [k.name() for k in node.knobs().values()]
    if 'MT' not in existing_knobs:
        tab = nuke.Tab_Knob('MT', 'MT')
        node.addKnob(tab)
        
        open_comp_btn = nuke.PyScript_Knob('open_comp', 'Open Comp File', 'read_node_callback.open_comp_file_from_node()')
        node.addKnob(open_comp_btn)

def onCreateCallback():
    """Callback function that runs when a Read node is created."""
    node = nuke.thisNode()
    if node.Class() == 'Read':
        # Add default PFX tab stuff here if needed
        add_mt_tab(node)

# Register the callback
nuke.addOnCreate(onCreateCallback, nodeClass='Read')
