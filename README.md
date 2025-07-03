<div align="center">

<p>
	<strong>## 3D Model to 360°</strong>
</p>
<p>
	<strong>Automated pipeline for extracting textures, generating renders, and creating rotation animations from 3D models</strong>
</p>

<p>
	<img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License">
	<img src="https://img.shields.io/badge/Blender-4.4+-orange?style=for-the-badge" alt="Blender Version">
	<img src="https://img.shields.io/badge/Python-3.9+-yellow?style=for-the-badge" alt="Python Version">
</p>

</div>

## Overview

A Python script designed to automate the processing of 3D models for professional rendering and animation. Whether you're a 3D artist, game developer, or content creator, this tool simplifies workflows by automating texture extraction, isometric rendering, and 360° rotation animations. It produces high-quality outputs, including QuickTime MOV and GIF files with alpha transparency, ideal for presentations, video editing, and asset visualization.

## Features

###  Texture Extraction
- Automatically extracts textures from 3D models and saves them as JPG files.
- Organized texture folder structure for easy access.

###  Rendering Modes
- **Solid View**: Uniform material for clean shape visualization.
- **Textured View**: Accurate representation of original materials.
- **Mesh View**: Polygon edges with transparent faces for technical analysis.

###  Animation Pipeline
- Generates seamless 360° rotation animations for each rendering mode.
- Transparent backgrounds for easy compositing.
- Outputs high-quality QuickTime MOV files using ProRes 4444 codec.
- Outputs high-quality GIF files with alpha transparency.

###  Optimized Output
- 1024x1024 resolution renders.
- Professional three-point lighting setup.
- Dynamic camera positioning based on model size.
- Organized output structure with consistent naming conventions.

### GIF Specifications
- **Transparency Support**: GIFs include alpha transparency for compositing.
- **Optimized Palette**: Uses palette generation for better color quality.
- **Frame Rate**: Default 30 FPS for smooth animations.
- **Small File Size**: Reasonable compression while maintaining quality.

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

### Output Structure
output/
└── model_name/
├── textures/              # Extracted JPG textures
├── mov_animations/        # QuickTime MOV files
│   ├── model_solid_rotation.mov
│   ├── model_textured_rotation.mov
│   └── model_mesh_rotation.mov
├── gif_animations/        # GIF animations
│   ├── model_solid_rotation.gif
│   ├── model_textured_rotation.gif
│   └── model_mesh_rotation.gif
├── solid_rotation/        # PNG frames (solid mode)
├── textured_rotation/     # PNG frames (textured mode)
├── mesh_rotation/         # PNG frames (mesh mode)
├── model_isometric_solid.png
├── model_isometric_textured.png
└── model_isometric_mesh.png

### Workflow
1. Place your 3D model file in a directory.
2. Run the script with the model path.
3. Retrieve processed files in the `output/model_name` directory.
4. Use MOV files directly in video editors, portfolio sites, or presentations.
5. Use GIF files for web sharing or lightweight animations.

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

## Limitations

- **Complex Materials**: May not fully replicate advanced node-based materials.
- **Large Models**: Very high-poly models may require extended processing time.
- **Texture Types**: Only diffuse textures are extracted by default.
- **Transparency Support**: Requires compatible software for MOV alpha playback.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
