# Custom Nuke Tools Documentation
By Martin Tomek

## Table of Contents
- [Overview](#overview)
- [Tools](#tools)
  - [1. Nuke Grab Tool](#1-nuke-grab-tool)
  - [2. Sequence Loader](#2-sequence-loader)
  - [3. Mask Checker](#3-mask-checker)
  - [4. Lock Cryptos](#4-lock-cryptos)
  - [5. ZDefocus Controller](#5-zdefocus-controller)
  - [6. Node Management Suite](#6-node-management-suite)
    - [Dynamic Shuffle Labeler](#dynamic-shuffle-labeler)
    - [CryptoMatte Tool](#crypto-label-tool)
    - [Animated Node Labeler](#animated-node-labeler)
- [Installation](#installation)
- [Conclusion](#conclusion)

## Overview
As a Compositor and Technical Director, I've developed various tools to enhance workflow efficiency and solve common problems in Nuke compositing pipelines. This documentation outlines the functionality and benefits of each tool.

## Tools

### 1. Nuke Grab Tool
- **Problem Solved**: Difficulty in organizing nodes when zoomed out
- **Key Features**:
  - Blender-inspired 'grab' functionality
  - Keyboard shortcut activation ('E')
  - Confirm with left-click or Enter, cancel with Esc

### 2. Sequence Loader
- **Problem Solved**: Time-consuming manual import of multiple shots
- **Key Features**:
  - Automatic sequence detection
  - Multi-sequence support
  - Consistent arrangement for review

### 3. Mask Checker
- **Problem Solved**: Error-prone manual inspection of mask channels
- **Key Features**:
  - Automated mask verification
  - Grade node integration for enhanced visibility

### 4. Lock Cryptos
- **Problem Solved**: Unexpected Cryptomatte layer changes causing errors
- **Key Features**:
  - Automatic Cryptomatte detection
  - Layer locking mechanism
  - Dynamic labeling

### 5. ZDefocus Controller
- **Problem Solved**: Inconsistent management of multiple defocus nodes
- **Key Features**:
  - Centralized control interface
  - Automatic camera integration
  - Render farm compatibility

### 6. Node Management Suite
An integrated suite of tools for enhanced node organization and management.

#### Dynamic Shuffle Labeler
- **Problem Solved**: Time-consuming manual labeling of Shuffle nodes
- **Key Features**:
  - Automatic labeling with input channel
  - Postage stamp activation for non-RGBA shuffles
  - Automatic keep node for RGBA channels

#### CryptoLabel Tool
- **Problem Solved**: Unclear labeling and RGBA output issues in CryptoMatte nodes
- **Key Features**:
  - Dynamic labeling with layer and matte information
  - Automatic RGBA preservation
  - Intelligent node positioning

#### Animated Node Labeler
- **Problem Solved**: Difficulty in identifying animated nodes
- **Key Features**:
  - Automatic animation detection
  - Mix value display
  - Color coding for easy identification
  - Toggleable functionality

## Installation
1. Download the tools package
2. Place scripts in your Nuke plugins directory
3. Add to your `init.py`:
```python
nuke.pluginAddPath("/path/to/custom_tools")
```
4. Restart Nuke

## Conclusion
These tools represent a comprehensive approach to solving common VFX production challenges. They offer significant time savings, improved consistency, and enhanced quality control in daily tasks. As a Technical Director, I remain committed to refining and expanding this toolkit based on user feedback and evolving production needs.

Feel free to reach out with questions, suggestions, or specific workflow challenges that might benefit from similar custom solutions.
