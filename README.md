# NukeScripts
Collection of my scripts that i made to make my life easier


"""
Sequence Loader for Nuke

Overview:
The Sequence Loader is a Python script designed to automate the process of loading and reviewing multiple shot sequences in Nuke. It enhances efficiency by automating tedious tasks, improving quality control, and simplifying communication between artists and supervisors.

Key Features:
- Automatic Sequence Detection:
  - Automatically detects the sequence number from the Nuke script name.
  - Allows manual input for flexibility.
  
- Multi-Sequence Support:
  - Supports loading multiple sequences in one operation.
  - Remembers the next logical sequence number for faster iterations.
  
- Smart Render Version Detection:
  - Finds and loads the latest render version for each shot.
  - Supports both regular and denoise render paths.
  
- Dynamic Read Node Creation:
  - Creates Read nodes with appropriate file paths and frame ranges.
  - Sets localization policy for efficient file management.
  
- Automatic Contact Sheet Generation:
  - Generates a ContactSheet node to combine all loaded shots.
  - Adjusts layout dynamically based on the number of shots.
  
- Custom Overlay Information:
  - Adds text overlays to each shot with sequence, shot number, and render type.
  
- Flexible Render Type Selection:
  - Allows choice between compositing and denoise renders.
  
- Visual Organization:
  - Arranges nodes logically in the Node Graph.
  - Adds labeled backdrops for clarity.
  
- User-Friendly Interface:
  - Provides interactive dialogs for sequence selection and feedback.

Technical Implementation:
- Developed using Python in Nuke's scripting environment.
- Uses Nuke's file system interaction, node graph manipulation, and UI creation.
- Employs dynamic node creation, advanced file path handling, and custom UI elements.

Usage Scenarios:
- Artist Self-Review: Load and review sequences for progress checks.
- Supervisor Reviews: Efficiently review sequences for approvals or feedback.
- Team Presentations: Prepare sequences for team discussions.
- Render Comparisons: Compare compositing and denoise renders easily.
"""
