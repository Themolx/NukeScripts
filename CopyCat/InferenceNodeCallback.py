# InferenceNodeCallback.py v1.1
#
# DESCRIPTION:
# This script adds auto-coloring and naming functionality to Inference nodes.
# The callback runs both on node creation and when modelFile path is changed.
# 
# USAGE:
# Add this script to your menu.py
# The callback will automatically:
# 1. Run when node is created
# 2. Run when modelFile path is changed
# 3. Generate unique color based on the model path
# 4. Apply color and name to node
#
# Author: ChatGPT
# Date: 2024-01-25

import nuke
import colorsys
import re
import os
import hashlib

# User Variables
COLOR_SATURATION = 0.7  # Color saturation (0-1)
COLOR_VALUE = 0.9      # Color brightness (0-1)
DEBUG = False          # Set to True for debug prints

def generate_color_from_string(input_string):
    """Generate a consistent color from a string using hashing."""
    # Create hash of input string
    hash_object = hashlib.md5(input_string.encode())
    hash_hex = hash_object.hexdigest()
    
    # Use first 8 characters of hash to generate hue
    hue = int(hash_hex[:8], 16) / float(0xffffffff)
    
    # Convert HSV to RGB
    rgb = colorsys.hsv_to_rgb(hue, COLOR_SATURATION, COLOR_VALUE)
    
    # Convert to Nuke color integer format
    color_int = (int(rgb[0] * 255) << 24) + (int(rgb[1] * 255) << 16) + (int(rgb[2] * 255) << 8) + 255
    
    return color_int

def extract_model_info(path):
    """Extract meaningful info from model file path."""
    try:
        # Extract filename without extension
        filename = os.path.basename(path)
        filename = os.path.splitext(filename)[0]
        
        # Find version number pattern (e.g., v1, v2, etc.)
        version_match = re.search(r'_v(\d+)', path)
        version = version_match.group(1) if version_match else ""
        
        # Find shot number pattern (e.g., 2210, 2180, etc.)
        shot_match = re.search(r'(\d{4})_v', path)
        shot = shot_match.group(1) if shot_match else ""
        
        if not shot or not version:
            # Fallback: try to find any 4-digit number
            shot_match = re.search(r'(\d{4})', path)
            shot = shot_match.group(1) if shot_match else "0000"
        
        # Create node name
        node_name = f"Inference_{shot}_v{version}"
        return node_name
        
    except Exception as e:
        if DEBUG:
            print(f"Error processing path {path}: {str(e)}")
        return "Inference_unknown"

def update_inference_node(node):
    """Update the color and name of an Inference node."""
    try:
        model_path = node['modelFile'].value()
        if model_path:
            # Generate color based on model path
            color = generate_color_from_string(model_path)
            
            # Generate name based on model path
            node_name = extract_model_info(model_path)
            
            # Ensure unique name
            base_name = node_name
            counter = 1
            while nuke.exists(f"{node_name}"):
                if nuke.exists(f"{node_name}") and nuke.toNode(f"{node_name}") is node:
                    break
                node_name = f"{base_name}_{counter}"
                counter += 1
            
            # Apply color and name
            node['tile_color'].setValue(color)
            node['name'].setValue(node_name)
            
            if DEBUG:
                print(f"Updated node: {node_name} with color: {color}")
                
    except Exception as e:
        if DEBUG:
            print(f"Error in update_inference_node: {str(e)}")

def inference_knob_changed():
    """Callback function for Inference node knob changes."""
    node = nuke.thisNode()
    knob = nuke.thisKnob()
    
    if knob.name() == "modelFile":
        update_inference_node(node)

def onCreateCallback():
    """Callback function that runs when a node is created."""
    node = nuke.thisNode()
    # Run update immediately after creation
    update_inference_node(node)

def add_inference_callbacks():
    """Add all callbacks to Inference nodes."""
    # Add callback for knob changes
    nuke.addKnobChanged(inference_knob_changed, nodeClass='Inference')
    
    # Add callback for node creation
    nuke.addOnCreate(onCreateCallback, nodeClass='Inference')
    
    if DEBUG:
        print("Added callbacks to Inference nodes")

# Add menus or toolbar entries if needed
def setup_inference_menu():
    """Setup any menu items if needed."""
    pass  # Add any menu setup code here if needed

def setup_all():
    """Main setup function."""
    add_inference_callbacks()
    setup_inference_menu()

# Initialize everything
setup_all()
