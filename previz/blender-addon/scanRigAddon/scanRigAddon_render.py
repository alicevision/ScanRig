import sys
import os
import math
import re
import bpy
from glob import glob

"""
Render functions
"""


def render(context, imgDir, imgName):
    """ Render the scene.

    Args:
        context : the scene context
        imgDir (str): the image save directory
        imgName (str): the image name
    """

    # Set up rendering
    scene = context.scene
    render = context.scene.render
    renderProp = context.scene.RenderPropertyGroup

    scene.use_nodes = True
    if bpy.app.version < (3, 0, 0):
        scene.view_layers["View Layer"].use_pass_normal = True
        scene.view_layers["View Layer"].use_pass_diffuse_color = True
        scene.view_layers["View Layer"].use_pass_object_index = True

    nodes = context.scene.node_tree.nodes
    links = context.scene.node_tree.links

    # Clear default nodes
    for n in nodes:
        nodes.remove(n)

    # Create input render layer node
    render_layers = nodes.new('CompositorNodeRLayers')

    format = 'PNG'
    color_depth = '8'

    if renderProp.bool_depth:
        # Create depth output nodes
        depth_file_output = nodes.new(type="CompositorNodeOutputFile")
        depth_file_output.label = 'Depth Output'
        depth_file_output.base_path = ''
        depth_file_output.file_slots[0].use_node_format = True
        depth_file_output.format.file_format = format
        depth_file_output.format.color_depth = color_depth
        if format == 'OPEN_EXR':
            links.new(render_layers.outputs['Depth'],
                      depth_file_output.inputs[0])
        else:
            depth_file_output.format.color_mode = "BW"

            # Remap as other types can not represent the full range of depth.
            map = nodes.new(type="CompositorNodeMapValue")
            # Size is chosen kind of arbitrarily, try out until you're satisfied with resulting depth map.
            map.offset = [-0.7]
            map.size = [1.4]
            map.use_min = True
            map.min = [0]

            links.new(render_layers.outputs['Depth'], map.inputs[0])
            links.new(map.outputs[0], depth_file_output.inputs[0])

    if renderProp.bool_normal:
        # Create normal output nodes
        scale_node = nodes.new(type="CompositorNodeMixRGB")
        scale_node.blend_type = 'MULTIPLY'
        # scale_node.use_alpha = True
        scale_node.inputs[2].default_value = (0.5, 0.5, 0.5, 1)
        links.new(render_layers.outputs['Normal'], scale_node.inputs[1])

        bias_node = nodes.new(type="CompositorNodeMixRGB")
        bias_node.blend_type = 'ADD'
        # bias_node.use_alpha = True
        bias_node.inputs[2].default_value = (0.5, 0.5, 0.5, 0)
        links.new(scale_node.outputs[0], bias_node.inputs[1])

        normal_file_output = nodes.new(type="CompositorNodeOutputFile")
        normal_file_output.label = 'Normal Output'
        normal_file_output.base_path = ''
        normal_file_output.file_slots[0].use_node_format = True
        normal_file_output.format.file_format = format
        links.new(bias_node.outputs[0], normal_file_output.inputs[0])

    if renderProp.bool_albedo:
        # Create albedo output nodes
        alpha_albedo = nodes.new(type="CompositorNodeSetAlpha")
        links.new(render_layers.outputs['DiffCol'],
                  alpha_albedo.inputs['Image'])
        links.new(render_layers.outputs['Alpha'], alpha_albedo.inputs['Alpha'])

        albedo_file_output = nodes.new(type="CompositorNodeOutputFile")
        albedo_file_output.label = 'Albedo Output'
        albedo_file_output.base_path = ''
        albedo_file_output.file_slots[0].use_node_format = True
        albedo_file_output.format.file_format = format
        albedo_file_output.format.color_mode = 'RGBA'
        albedo_file_output.format.color_depth = color_depth
        links.new(alpha_albedo.outputs['Image'], albedo_file_output.inputs[0])

    if renderProp.bool_id:
        # Create id map output nodes
        id_file_output = nodes.new(type="CompositorNodeOutputFile")
        id_file_output.label = 'ID Output'
        id_file_output.base_path = ''
        id_file_output.file_slots[0].use_node_format = True
        id_file_output.format.file_format = format
        id_file_output.format.color_depth = color_depth

        if format == 'OPEN_EXR':
            links.new(
                render_layers.outputs['IndexOB'], id_file_output.inputs[0])
        else:
            id_file_output.format.color_mode = 'BW'

            divide_node = nodes.new(type='CompositorNodeMath')
            divide_node.operation = 'DIVIDE'
            divide_node.use_clamp = False
            divide_node.inputs[1].default_value = 2 ** int(color_depth)

            links.new(render_layers.outputs['IndexOB'], divide_node.inputs[0])
            links.new(divide_node.outputs[0], id_file_output.inputs[0])

    # Get and define the respective render file paths
    fp = os.path.join(imgDir, imgName)
    render_file_path = fp

    if renderProp.bool_beauty:
        scene.render.filepath = render_file_path
    if renderProp.bool_depth:
        depth_file_output.file_slots[0].path = render_file_path + "_depth"
    if renderProp.bool_normal:
        normal_file_output.file_slots[0].path = render_file_path + "_normal"
    if renderProp.bool_albedo:
        albedo_file_output.file_slots[0].path = render_file_path + "_albedo"
    if renderProp.bool_id:
        id_file_output.file_slots[0].path = render_file_path + "_id"

    bpy.ops.render.render(write_still=True)  # render still

    # For debugging the workflow
    # bpy.ops.wm.save_as_mainfile(filepath='debug.blend')
