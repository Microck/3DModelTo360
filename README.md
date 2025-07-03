<div align="center">

# **3D Model to 360°**

### **Automated pipeline for extracting textures, generating renders, and creating rotation animations from 3D models**

<p>
	<img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License">
	<img src="https://img.shields.io/badge/Blender-4.4+-orange?style=for-the-badge" alt="Blender Version">
	<img src="https://img.shields.io/badge/Python-3.9+-yellow?style=for-the-badge" alt="Python Version">
</p>

</div>

## Overview

A Python script designed to automate the processing of 3D models for professional rendering and animation. Whether you're a 3D artist, game developer, or content creator, this tool simplifies workflows by automating texture extraction, isometric rendering, and 360° rotation animations. It produces high-quality outputs, including QuickTime MOV and GIF files with alpha transparency, ideal for presentations, video editing, and asset visualization.

## Features

- Texture Extraction: Extracts textures from 3D models as JPG files.
- Rendering Modes: Generates solid, textured, and mesh views for visualization and analysis.
- Animation Pipeline: Creates 360° rotation animations with transparent backgrounds in QuickTime MOV and GIF formats.
- GIF Specifications: Supports alpha transparency, 30 FPS, optimized palette, and small file sizes.

## Requirements

- **Python 3.x**
- **Blender 4.4+** - [Download Blender](https://www.blender.org/download/)
- **FFmpeg** (for video conversion) - [Download FFmpeg](https://ffmpeg.org/download.html)
- **Libraries**: `numpy`, `mathutils`, `subprocess`

Install the required libraries using the provided `requirements.txt` file:
```bash
pip install -r requirements.txt
```

- **Supported Formats**: FBX, GLB, GLTF

## Installation

1. **Install Blender 4.4+** from [official website](https://www.blender.org/download/).
2. **Install FFmpeg** and add it to your system PATH:
   - Windows: [Download FFmpeg for Windows](https://www.gyan.dev/ffmpeg/builds/)
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
3. **Download the script**:
   ```bash
   git clone https://github.com/Microck/3DModelTo360.git
   ```

## Usage

### Basic Command
```bash
blender --background --python process_model.py -- "path/to/your/model.glb"
```

### Command Options
| Parameter | Description | Example |
|-----------|-------------|---------|
| Model path | Path to 3D model file | `"D:\assets\character.glb"` |

Here’s the rewritten **Output Structure** section for clarity and better organization:


### Output Structure

```
output/
└── model_name/
    ├── textures/              # Extracted textures from the 3D model (JPG format)
    ├── mov_animations/        # QuickTime MOV files (ProRes 4444 with alpha transparency)
    │   ├── model_solid_rotation.mov
    │   ├── model_textured_rotation.mov
    │   └── model_mesh_rotation.mov
    ├── gif_animations/        # GIF animations (with alpha transparency)
    │   ├── model_solid_rotation.gif
    │   ├── model_textured_rotation.gif
    │   └── model_mesh_rotation.gif
    ├── solid_rotation/        # PNG frames for the solid view rotation
    │   ├── frame_000.png
    │   ├── frame_001.png
    │   └── ...
    ├── textured_rotation/     # PNG frames for the textured view rotation
    │   ├── frame_000.png
    │   ├── frame_001.png
    │   └── ...
    ├── mesh_rotation/         # PNG frames for the mesh view rotation
    │   ├── frame_000.png
    │   ├── frame_001.png
    │   └── ...
    ├── model_isometric_solid.png      # Isometric render (solid view)
    ├── model_isometric_textured.png   # Isometric render (textured view)
    └── model_isometric_mesh.png       # Isometric render (mesh view)
```

## Example Output

### Isometric Renders
![Isometric Renders Example](https://via.placeholder.com/1024x300/333333/ffffff?text=Solid+Textured+Mesh+Renders)
*Professional isometric renders: solid, textured, and mesh views.*

### Rotation Animation
![Rotation Animation Example](https://via.placeholder.com/1024x300/333333/ffffff?text=360°+Rotation+Animation)
*Transparent rotation animation in QuickTime Player.*

## Technical Details

### Lighting Setup
- **Key Light**: Primary directional light (1000 energy).
- **Fill Light**: Secondary complementary light (500 energy).
- **Ambient Light**: Global illumination with adjustable intensity.
- Optimized for neutral, professional presentation.

### Camera System
- 45° isometric angle.
- Dynamic distance calculation based on model size.
- Automatic focus on model center.
- Perspective projection.

### Transparency Handling
- RGBA PNG format with alpha channel.
- ProRes 4444 codec for QuickTime MOV files.
- Compatible with professional video editors.

### Mesh Visualization
- Custom shader for edge detection.
- Adjustable wireframe thickness.
- Transparent face rendering.
- Black edges on light gray background.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
