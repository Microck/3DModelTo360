import bpy
import sys
import os
import math
import mathutils
import subprocess

# --- Helper Functions ---
def disable_addon(addon_name):
    try:
        bpy.ops.preferences.addon_disable(module=addon_name)
        print(f"Disabled addon: {addon_name}")
    except:
        print(f"Could not disable addon: {addon_name}")

def setup_lighting():
    light_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    light_data.energy = 2500
    light_data.size = 25.0
    light = bpy.data.objects.new(name="KeyLight", object_data=light_data)
    bpy.context.scene.collection.objects.link(light)
    light.location = (10, -10, 10)
    light.rotation_euler = (math.radians(45), 0, math.radians(45))

    fill_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_data.energy = 1500
    fill_data.size = 20.0
    fill = bpy.data.objects.new(name="FillLight", object_data=fill_data)
    bpy.context.scene.collection.objects.link(fill)
    fill.location = (-10, 10, 7)
    fill.rotation_euler = (math.radians(-45), 0, math.radians(-45))

    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background') or world.node_tree.nodes.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = 0.8

def create_solid_material():
    mat = bpy.data.materials.get("SolidMat")
    if not mat:
        mat = bpy.data.materials.new("SolidMat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF') or mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
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
        for node in nodes: nodes.remove(node)
        
        # Increase wireframe thickness for better visibility
        wire = nodes.new('ShaderNodeWireframe')
        wire.inputs['Size'].default_value = 0.005  # Increased from 0.002
        
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

def render_solid(scene, solid_material):
    for obj in scene.objects:
        if obj.type == 'MESH':
            obj.data.materials.clear()
            obj.data.materials.append(solid_material)

def render_textured(scene, original_materials):
    for obj in scene.objects:
        if obj.type == 'MESH' and obj.name in original_materials:
            obj.data.materials.clear()
            for mat_name in original_materials[obj.name]:
                if mat_name in bpy.data.materials:
                    obj.data.materials.append(bpy.data.materials[mat_name])

def render_mesh(scene, mesh_material):
    for obj in scene.objects:
        if obj.type == 'MESH':
            obj.data.materials.clear()
            obj.data.materials.append(mesh_material)

def render_image(scene, mode, filename, **kwargs):
    if mode == 'SOLID': render_solid(scene, kwargs['solid_material'])
    elif mode == 'TEXTURED': render_textured(scene, kwargs['original_materials'])
    elif mode == 'MESH': render_mesh(scene, kwargs['mesh_material'])
    
    scene.render.filepath = filename
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {filename}")

def render_rotation(scene, empty, mode, prefix, **kwargs):
    rotation_dir = os.path.join(output_dir, f"{prefix}_rotation")
    os.makedirs(rotation_dir, exist_ok=True)
    
    if mode == 'SOLID': render_solid(scene, kwargs['solid_material'])
    elif mode == 'TEXTURED': render_textured(scene, kwargs['original_materials'])
    elif mode == 'MESH': render_mesh(scene, kwargs['mesh_material'])
    
    empty.rotation_euler = (0, 0, 0)
    
    for i in range(kwargs.get('frames', 60)):
        angle = (i / kwargs.get('frames', 60)) * 2 * math.pi
        empty.rotation_euler = (0, 0, angle)
        frame_path = os.path.join(rotation_dir, f"frame_{i:03d}.png")
        scene.render.filepath = frame_path
        bpy.ops.render.render(write_still=True)
    
    print(f"Rendered {kwargs.get('frames', 60)} frames for {prefix} rotation in {rotation_dir}")
    return rotation_dir

def create_mov_animation(frame_dir, output_path, framerate=30):
    input_pattern = os.path.join(frame_dir, "frame_%03d.png")
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        cmd = ["ffmpeg", "-y", "-framerate", str(framerate), "-i", input_pattern, "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-vendor", "apl0", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Created QuickTime MOV: {output_path}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"FFmpeg failed for MOV. Error: {e}")

def create_gif_animation(frame_dir, output_path, framerate=30):
    input_pattern = os.path.join(frame_dir, "frame_%03d.png")
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        cmd = ["ffmpeg", "-y", "-framerate", str(framerate), "-i", input_pattern, "-vf", "split[a][b];[a]palettegen[p];[b][p]paletteuse", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Created GIF: {output_path}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"FFmpeg failed for GIF. Error: {e}")

# ===== MAIN SCRIPT =====
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
if not argv:
    print('Usage: blender --background --python process_model.py -- <model_path>')
    sys.exit(1)

model_path = argv[0]
model_name = os.path.splitext(os.path.basename(model_path))[0]
ext = os.path.splitext(model_path)[1].lower()

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output", model_name)
os.makedirs(output_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
disable_addon("io_scene_valvesource")

if ext == ".fbx": bpy.ops.import_scene.fbx(filepath=model_path)
elif ext in [".glb", ".gltf"]: bpy.ops.import_scene.gltf(filepath=model_path)
elif ext == ".blend":
    with bpy.data.libraries.load(model_path, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects
    for obj in data_to.objects:
        if obj: bpy.context.scene.collection.objects.link(obj)
else:
    print(f"Unsupported file extension: {ext}")
    sys.exit(1)

# Ensure all objects are visible
for obj in bpy.context.scene.objects:
    obj.hide_set(False)
    obj.hide_render = False

original_materials = {obj.name: [mat.name for mat in obj.data.materials] for obj in bpy.data.objects if obj.type == 'MESH'}

textures_dir = os.path.join(output_dir, "textures")
os.makedirs(textures_dir, exist_ok=True)
for mat in bpy.data.materials:
    if mat and mat.use_nodes:
        for node in mat.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                try:
                    img_path = os.path.join(textures_dir, f"{node.image.name}.jpg")
                    node.image.filepath_raw = img_path
                    node.image.file_format = 'JPEG'
                    node.image.save()
                    print(f"Saved texture: {img_path}")
                except Exception as e:
                    print(f"Could not save texture {node.image.name}: {e}")

setup_lighting()

scene = bpy.context.scene
cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

# Improved camera framing with headroom
mesh_objects = [obj for obj in scene.objects if obj.type == 'MESH']
if mesh_objects:
    # Calculate global bounding box in world space
    min_coord = [float('inf')] * 3
    max_coord = [float('-inf')] * 3
    
    for obj in mesh_objects:
        # Get world matrix
        world_matrix = obj.matrix_world
        # Get all corners of the object's bounding box in world space
        for corner in obj.bound_box:
            world_corner = world_matrix @ mathutils.Vector(corner)
            for i in range(3):
                min_coord[i] = min(min_coord[i], world_corner[i])
                max_coord[i] = max(max_coord[i], world_corner[i])
    
    # Add 25% headroom to ensure full visibility
    headroom = 1.25
    size = max(max_coord[i] - min_coord[i] for i in range(3)) * headroom
    center = mathutils.Vector((
        (min_coord[0] + max_coord[0]) / 2,
        (min_coord[1] + max_coord[1]) / 2,
        (min_coord[2] + max_coord[2]) / 2
    ))
    
    # Position camera with extra height for headroom
    cam.location = center + mathutils.Vector((1.8, -1.8, 1.2)) * size
    direction = center - cam.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = 30  # Wider angle lens to capture more

# Create rotation pivot at model center
bpy.ops.object.empty_add(type='PLAIN_AXES', location=center)
empty = bpy.context.active_object
empty.name = "RotationPivot"
for obj in mesh_objects: 
    obj.parent = empty

# Increased resolution to 2048x2048
scene.render.resolution_x = 2048
scene.render.resolution_y = 2048
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.engine = 'BLENDER_EEVEE_NEXT'

# Create materials with thicker wireframe
solid_material = create_solid_material()
mesh_material = create_mesh_material()
render_kwargs = {
    'original_materials': original_materials,
    'solid_material': solid_material,
    'mesh_material': mesh_material,
    'frames': 60
}

# Render isometric views
render_image(scene, 'SOLID', os.path.join(output_dir, f'{model_name}_isometric_solid.png'), **render_kwargs)
render_image(scene, 'TEXTURED', os.path.join(output_dir, f'{model_name}_isometric_textured.png'), **render_kwargs)
render_image(scene, 'MESH', os.path.join(output_dir, f'{model_name}_isometric_mesh.png'), **render_kwargs)

# Render rotation animations
solid_dir = render_rotation(scene, empty, 'SOLID', 'solid', **render_kwargs)
textured_dir = render_rotation(scene, empty, 'TEXTURED', 'textured', **render_kwargs)
mesh_dir = render_rotation(scene, empty, 'MESH', 'mesh', **render_kwargs)

# Create animation folders
mov_dir = os.path.join(output_dir, "mov_animations")
gif_dir = os.path.join(output_dir, "gif_animations")
os.makedirs(mov_dir, exist_ok=True)
os.makedirs(gif_dir, exist_ok=True)

# Create MOV animations
create_mov_animation(solid_dir, os.path.join(mov_dir, f"{model_name}_solid_rotation.mov"))
create_mov_animation(textured_dir, os.path.join(mov_dir, f"{model_name}_textured_rotation.mov"))
create_mov_animation(mesh_dir, os.path.join(mov_dir, f"{model_name}_mesh_rotation.mov"))

# Create GIF animations with higher quality
create_gif_animation(solid_dir, os.path.join(gif_dir, f"{model_name}_solid_rotation.gif"))
create_gif_animation(textured_dir, os.path.join(gif_dir, f"{model_name}_textured_rotation.gif"))
create_gif_animation(mesh_dir, os.path.join(gif_dir, f"{model_name}_mesh_rotation.gif"))

print(f"\nAll done! Output saved to: {output_dir}")
