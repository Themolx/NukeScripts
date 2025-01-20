# OpenCompFromRender.py v4.2
#
# This script opens the corresponding Nuke comp file based on the selected Read node.
# It extracts sequence, shot, and version information from the Read node's file path
# and opens the matching .nk file. It also provides user feedback via dialogue windows.

import nuke
import os
import re

# User variables
WORK_ROOT = "Z:/20105_Pysna_film/work/FILM"

def get_read_node_info():
    """Extract sequence, shot, and version information from the selected Read node."""
    selected_nodes = nuke.selectedNodes('Read')
    if not selected_nodes:
        raise ValueError("No Read node selected. Please select a Read node.")
    
    read_node = selected_nodes[0]
    file_path = read_node['file'].value()
    
    pattern = r'SQ(\d+)/SH(\d+)/compositing/render/v(\d+)/pp_FILM_SQ\d+_SH\d+_comp_v(\d+)'
    match = re.search(pattern, file_path)
    
    if match:
        seq_num, shot_num, render_version, comp_version = match.groups()
        return seq_num, shot_num, comp_version
    else:
        raise ValueError("Invalid file path format in the selected Read node.")

def find_comp_file(seq_num, shot_num, version):
    """Find the comp file based on extracted information."""
    comp_dir = os.path.join(WORK_ROOT, f"SQ{seq_num}", f"SH{shot_num}", "compositing", "work")
    comp_file = f"FILM_SQ{seq_num}_SH{shot_num}_comp_v{version}.nk"
    return os.path.normpath(os.path.join(comp_dir, comp_file))

def open_comp_file():
    """Open the Nuke comp file corresponding to the selected Read node."""
    try:
        seq_num, shot_num, version = get_read_node_info()
        comp_file = find_comp_file(seq_num, shot_num, version)
        
        if os.path.exists(comp_file):
            if nuke.ask(f"Do you want to open the comp file:\n{comp_file}"):
                nuke.scriptOpen(comp_file)
                nuke.message(f"Successfully opened comp file:\n{comp_file}")
            else:
                nuke.message("Operation cancelled by user.")
        else:
            nuke.message(f"Comp file not found:\n{comp_file}\n\nPlease check if the file exists.")
    
    except ValueError as e:
        nuke.message(str(e))
    except Exception as e:
        nuke.message(f"An unexpected error occurred:\n{str(e)}\n\nPlease check your script and try again.")

# Add to Nuke menu
nuke.menu('Nuke').addCommand('Custom/Open Comp from Read Node', open_comp_file)

# For testing in script editor
if __name__ == "__main__":
    open_comp_file()
