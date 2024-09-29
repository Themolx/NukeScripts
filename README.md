<a href="https://yourwebsite.com"><img src="https://yourwebsite.com/images/logo.png" alt="Your Logo"></a>

# Sequence Loader for Nuke

Streamline the loading and review process for multiple shot sequences in VFX compositions with **Sequence Loader**, an automated script designed for Nuke.

---

# Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
  - [Automatic Sequence Detection](#automatic-sequence-detection)
  - [Multi-Sequence Support](#multi-sequence-support)
  - [Smart Render Version Detection](#smart-render-version-detection)
  - [Dynamic Read Node Creation](#dynamic-read-node-creation)
  - [Automatic Contact Sheet Generation](#automatic-contact-sheet-generation)
  - [Custom Overlay Information](#custom-overlay-information)
  - [Flexible Render Type Selection](#flexible-render-type-selection)
  - [Visual Organization](#visual-organization)
  - [User-Friendly Interface](#user-friendly-interface)
- [Technical Implementation](#technical-implementation)
- [Usage Scenarios](#usage-scenarios)

---

## Overview
**Sequence Loader** is a Python script for Nuke that automates the process of importing and reviewing multiple shot sequences. It improves workflow efficiency, quality control, and communication between artists and supervisors.

---

## Key Features

### Automatic Sequence Detection
- Detects the current sequence number from the Nuke script name.
- Supports manual input for flexibility.

### Multi-Sequence Support
- Load multiple sequences in one operation.
- Remembers the next sequence number for faster iterations.

### Smart Render Version Detection
- Automatically loads the latest render version for each shot.
- Supports both regular compositing and denoise render paths.

### Dynamic Read Node Creation
- Generates Read nodes for each shot with correct file paths and frame ranges.
- Automatically sets the localization policy for file management.

### Automatic Contact Sheet Generation
- Combines all loaded shots into a single ContactSheet node.
- Dynamically adjusts layout based on the number of shots.

### Custom Overlay Information
- Adds text overlays for sequence, shot number, and render type on each shot.
  
<a href="https://yourwebsite.com/images/sequence_loader_01.png"><img src="https://yourwebsite.com/images/sequence_loader_01.png" alt="Custom Overlay Example"></a>

### Flexible Render Type Selection
- Choose between compositing and denoise renders depending on your review needs.

### Visual Organization
- Automatically arranges nodes logically in the Node Graph.
- Adds labeled backdrops for easy organization.

### User-Friendly Interface
- Interactive dialogs for sequence selection and configuration.
- Provides feedback during the loading process.

---

## Technical Implementation

**Sequence Loader** is written in Python, utilizing Nuke's scripting environment. It interacts with the file system, manipulates the Node Graph, and provides a custom user interface for sequence management. It is designed to integrate smoothly into existing Nuke workflows and is customizable to meet specific pipeline requirements.

---

## Usage Scenarios

### Artist Self-Review
Quickly load and check progress on assigned sequences.

### Supervisor Reviews
Efficiently review multiple sequences for approval or feedback.

### Team Presentations
Prepare comprehensive sequence presentations for team discussions.

### Render Comparisons
Easily compare regular compositing and denoise renders side by side.
