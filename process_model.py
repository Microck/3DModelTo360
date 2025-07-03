import bpy
import sys
import os
import math
import mathutils
import subprocess

# --- Disable problematic addon ---
def disable_addon(addon_name):
    try:
        bpy.ops.preferences.addon_disable(module=addon_name)
        print(f"Disabled addon: {addon_name}")
    except:
        print(f"Could not disable addon: {addon_name}")

# --- Set up soft lighting ---
def setup_lighting():
    # Create large area light for soft shadows
    light_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    light_data.energy = 1000
    light_data.size = 10.0
    light = bpy.data.objects.new(name="KeyLight", object_data=light_data)
    bpy.context.scene.collection.objects.link(light)
    light.location = (5, -5, 5)
    light.rotation_euler = (0.785398, 0, 0.785398)
    
    # Create fill light
    fill_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_data.energy = 500
    fill_data.size = 8.0
    fill = bpy.data.objects.new(name="FillLight", object_data=fill_data)
    bpy.context.scene.collection.objects.link(fill)
    fill.location = (-5, 5, 3)
    fill.rotation_euler = (-0.785398, 0, -0.785398)
    
    # Create ambient light
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if not bg:
        bg = world.node_tree.nodes.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = 0.3

# --- Create materials ---
def create_solid_material():
    mat = bpy.data.materials.get("SolidMat")
    if not mat:
        mat = bpy.data.materials.new("SolidMat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if not bsdf:
            bsdf = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1)
        bsdf.inputs['Roughness'].default_value = 0.5
    return mat

def create_mesh_material():
    mat = bpy.data.materials.get("MeshMat")
    if not mat:
        mat = bpy.data.materials.new("MeshMat")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Clear default nodes
        for node in nodes:
            nodes.remove(node)
        
        # Create wireframe node
        wire = nodes.new('ShaderNodeWireframe')
        wire.inputs['Size'].default_value = 0.0005
        
        # Create transparent shader for faces
        transparent = nodes.new('ShaderNodeBsdfTransparent')
        
        # Create emission shader for edges
        emission = nodes.new('ShaderNodeEmission')
        emission.inputs['Color'].default_value = (0, 0, 0, 1)
        
        # Create mix shader
        mix = nodes.new('ShaderNodeMixShader')
        
        # Create output node
        output = nodes.new('ShaderNodeOutputMaterial')
        
        # Link nodes
        links.new(wire.outputs[0], mix.inputs[0])
        links.new(transparent.outputs[0], mix.inputs[1])
        links.new(emission.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], output.inputs[0])
    return mat

# --- Render functions ---
def render_solid(scene):
    """Apply solid material to all objects"""
    for obj in scene.objects:
        if obj.type == 'MESH':
            obj.data.materials.clear()
            obj.data.materials.append(solid_material)

def render_textured(scene, original_materials):
    """Restore original materials"""
    for obj in scene.objects:
        if obj.type == 'MESH' and obj.name in original_materials:
            obj.data.materials.clear()
            for mat_name in original_materials[obj.name]:
                if mat_name in bpy.data.materials:
                    obj.data.materials.append(bpy.data.materials[mat_name])

def render_mesh(scene):
    """Apply mesh material to all objects"""
    for obj in scene.objects:
        if obj.type == 'MESH':
            obj.data.materials.clear()
            obj.data.materials.append(mesh_material)

def render_image(scene, mode, filename, original_materials):
    if mode == 'SOLID':
        render_solid(scene)
    elif mode == 'TEXTURED':
        render_textured(scene, original_materials)
    elif mode == 'MESH':
        render_mesh(scene)
    
    scene.render.filepath = filename
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {filename}")

def render_rotation(scene, empty, mode, prefix, frames=60, original_materials=None):
    rotation_dir = os.path.join(output_dir, f"{prefix}_rotation")
    os.makedirs(rotation_dir, exist_ok=True)
    
    # Set initial mode
    if mode == 'SOLID':
        render_solid(scene)
    elif mode == 'TEXTURED':
        render_textured(scene, original_materials)
    elif mode == 'MESH':
        render_mesh(scene)
    
    # Reset rotation
    empty.rotation_euler = (0, 0, 0)
    
    # Create rotation animation
    for i in range(frames):
        # Rotate the model
        angle = (i / frames) * 2 * math.pi
        empty.rotation_euler = (0, 0, angle)
        
        # Render frame
        frame_path = os.path.join(rotation_dir, f"frame_{i:03d}.png")
        scene.render.filepath = frame_path
        bpy.ops.render.render(write_still=True)
    
    print(f"Rendered {frames} frames for {prefix} rotation in {rotation_dir}")
    return rotation_dir

# --- Generate QuickTime MOV animations ---
def create_mov_animation(frame_dir, output_path, framerate=30):
    """Convert PNG frames to QuickTime MOV with alpha transparency"""
    input_pattern = os.path.join(frame_dir, "frame_%03d.png")
    
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(framerate),
            "-i", input_pattern,
            "-c:v", "prores_ks",
            "-profile:v", "4444",
            "-pix_fmt", "yuva444p10le",
            "-vendor", "apl0",
            output_path
        ]
        subprocess.run(cmd, check=True)
        print(f"Created QuickTime MOV: {output_path}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("FFmpeg not found. Skipping MOV creation.")
        return False

# --- Generate GIF animations ---
def create_gif_animation(frame_dir, output_path, framerate=30):
    """Convert PNG frames to transparent GIF"""
    input_pattern = os.path.join(frame_dir, "frame_%03d.png")
    
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(framerate),
            "-i", input_pattern,
            "-vf", "split [a][b];[a] palettegen [p];[b][p] paletteuse",
            output_path
        ]
        subprocess.run(cmd, check=True)
        print(f"Created GIF: {output_path}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("FFmpeg not found. Skipping GIF creation.")
        return False

# ===== MAIN SCRIPT =====
# --- Get model path from command line ---
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []

if len(argv) < 1:
    print('Usage: blender --background --python process_model.py -- <model_path>')
    sys.exit(1)

model_path = argv[0]
model_name = os.path.splitext(os.path.basename(model_path))[0]
ext = os.path.splitext(model_path)[1].lower()

# Create output directory
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output", model_name)
os.makedirs(output_dir, exist_ok=True)

# --- Clear existing scene ---
bpy.ops.wm.read_factory_settings(use_empty=True)

# Disable problematic addon
disable_addon("io_scene_valvesource")

# --- Import model ---
if ext == ".fbx":
    bpy.ops.import_scene.fbx(filepath=model_path)
elif ext in [".glb", ".gltf"]:
    bpy.ops.import_scene.gltf(filepath=model_path)
else:
    print(f"Unsupported file extension: {ext}")
    sys.exit(1)

# --- Backup original materials ---
original_materials = {}
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        original_materials[obj.name] = [mat.name for mat in obj.data.materials]

# --- Extract textures ---
textures_dir = os.path.join(output_dir, "textures")
os.makedirs(textures_dir, exist_ok=True)

for mat in bpy.data.materials:
    if mat.use_nodes:
        for node in mat.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                img = node.image
                img_path = os.path.join(textures_dir, f"{img.name}.jpg")
                img.filepath_raw = img_path
                img.file_format = 'JPEG'
                try:
                    img.save()
                    print(f"Saved texture: {img_path}")
                except Exception as e:
                    print(f"Could not save {img.name}: {e}")

# --- Set up lighting ---
setup_lighting()

# --- Set up camera ---
scene = bpy.context.scene
cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

# Center model
bpy.ops.object.select_all(action='DESELECT')
for obj in scene.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
bpy.ops.object.location_clear()
bpy.ops.object.select_all(action='DESELECT')

# Create rotation pivot
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
empty = bpy.context.active_object
empty.name = "RotationPivot"

# Parent meshes to empty
for obj in scene.objects:
    if obj.type == 'MESH':
        obj.parent = empty

# Calculate bounding box
min_co = [float('inf')] * 3
max_co = [float('-inf')] * 3
for obj in scene.objects:
    if obj.type == 'MESH':
        for v in obj.bound_box:
            for i in range(3):
                min_co[i] = min(min_co[i], v[i] + obj.location[i])
                max_co[i] = max(max_co[i], v[i] + obj.location[i])
center = [(min_co[i] + max_co[i]) / 2 for i in range(3)]
size = max(max_co[i] - min_co[i] for i in range(3))

# Place camera
distance = size * 2.2
cam.location.x = center[0] + distance * math.cos(math.radians(45))
cam.location.y = center[1] - distance * math.sin(math.radians(45))
cam.location.z = center[2] + distance * 0.8
cam.data.lens = 50
cam.data.type = 'PERSP'

# Point camera at center
direction = mathutils.Vector(center) - mathutils.Vector(cam.location)
rot_quat = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()

# Set render settings
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.engine = 'BLENDER_EEVEE_NEXT'

# Create materials
solid_material = create_solid_material()
mesh_material = create_mesh_material()

# --- Render isometric images ---
render_image(scene, 'SOLID', os.path.join(output_dir, f'{model_name}_isometric_solid.png'), original_materials)
render_image(scene, 'TEXTURED', os.path.join(output_dir, f'{model_name}_isometric_textured.png'), original_materials)
render_image(scene, 'MESH', os.path.join(output_dir, f'{model_name}_isometric_mesh.png'), original_materials)

# --- Render 360° rotations ---
solid_dir = render_rotation(scene, empty, 'SOLID', 'solid', 60, original_materials)
textured_dir = render_rotation(scene, empty, 'TEXTURED', 'textured', 60, original_materials)
mesh_dir = render_rotation(scene, empty, 'MESH', 'mesh', 60, original_materials)

# --- Create animation folders ---
mov_dir = os.path.join(output_dir, "mov_animations")
gif_dir = os.path.join(output_dir, "gif_animations")
os.makedirs(mov_dir, exist_ok=True)
os.makedirs(gif_dir, exist_ok=True)

# Create QuickTime MOV animations
create_mov_animation(solid_dir, os.path.join(mov_dir, f"{model_name}_solid_rotation.mov"))
create_mov_animation(textured_dir, os.path.join(mov_dir, f"{model_name}_textured_rotation.mov"))
create_mov_animation(mesh_dir, os.path.join(mov_dir, f"{model_name}_mesh_rotation.mov"))

# Create GIF animations
create_gif_animation(solid_dir, os.path.join(gif_dir, f"{model_name}_solid_rotation.gif"))
create_gif_animation(textured_dir, os.path.join(gif_dir, f"{model_name}_textured_rotation.gif"))
create_gif_animation(mesh_dir, os.path.join(gif_dir, f"{model_name}_mesh_rotation.gif"))

print(f"\nAll done! Output saved to: {output_dir}")