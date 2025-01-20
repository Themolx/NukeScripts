# DeleteAllBackdrops.py v1.0
#
# This script deletes all backdrop nodes in the current Nuke script.
# It provides a simple way to clean up and remove all backdrop nodes at once.
#
# Usage:
# 1. Copy this script into your Nuke script editor
# 2. Run the script to delete all backdrops

import nuke

def delete_all_backdrops():
    # Find all backdrop nodes in the script
    backdrop_nodes = [node for node in nuke.allNodes() if node.Class() == "BackdropNode"]
    
    # Count the number of backdrops found
    num_backdrops = len(backdrop_nodes)
    
    # Delete each backdrop node
    for node in backdrop_nodes:
        nuke.delete(node)
    
    # Print a message with the number of backdrops deleted
    print(f"Deleted {num_backdrops} backdrop{'s' if num_backdrops != 1 else ''}.")

# Run the function to delete all backdrops
delete_all_backdrops()
