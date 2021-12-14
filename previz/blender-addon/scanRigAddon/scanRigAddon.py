#---------- Imports ----------#
import os
import bpy
import sys
import math
import mathutils

# Dome Creation functions imports
from scanRigAddon import scanRigAddon_icoCreation
from scanRigAddon import scanRigAddon_uvCreation
from scanRigAddon import scanRigAddon_sphereCreation
# Render functions import
from scanRigAddon import scanRigAddon_render

#from OpenImageIO import ImageInput, ImageOutput
#from OpenImageIO import ImageBuf, ImageSpec, ImageBufAlgo

# For OpenGL Calibration Poses documentation files
#import json

#---------- Class ----------#
class ScanRigPanel(bpy.types.Panel):
    bl_idname = 'SCANRIG_PT_ScanRig'
    bl_label = 'ScanRig Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ScanRig"

    def draw(self, context):
        layout = self.layout
        
        pan_col1 = layout.column()
        pan_col1.label(text="Scene Management")
        row = pan_col1.row()
        row.operator('object.scanrig_settings')
        row = pan_col1.row()
        row.operator('object.scanrig_clean')
        row = pan_col1.row()
        row.prop(context.scene.RenderPropertyGroup, "domeShape")   # Dome shape parameter
        row = pan_col1.row()
        row.operator('object.scanrig_setup')

        layout.separator()

        if context.scene.RenderPropertyGroup.renderReady:

            pan_col2 = layout.column()
            pan_col2.label(text="Photometry Management")
            row = pan_col2.row()        
            row.prop(context.scene.RenderPropertyGroup, "rotAngle")
            row = pan_col2.row()        
            row.prop(context.scene.RenderPropertyGroup, "stepDividerPhotometry")
            row = layout.row()  

            layout.separator()

            pan_col3 = layout.column()
            pan_col3.label(text="Render Management")
            row = pan_col3.row()
            row.prop(context.scene.RenderPropertyGroup, "renderMode")
            row = pan_col3.row()
            row.prop(context.scene.RenderPropertyGroup, "bool_albedo")
            row = pan_col3.row()    
            row.prop(context.scene.RenderPropertyGroup, "bool_depth")
            row = pan_col3.row()      
            row.prop(context.scene.RenderPropertyGroup, "bool_normal")
            row = pan_col3.row()    
            row.prop(context.scene.RenderPropertyGroup, "bool_id")
            row = pan_col3.row()      
            row.prop(context.scene.RenderPropertyGroup, "bool_basic")
            row = pan_col3.row()
            row.prop(context.scene.RenderPropertyGroup, "exportFolder")
            row = pan_col3.row()
            row.operator('object.scanrig_render')
        else:
            row = layout.row()
            row.label(text = "Render not ready")

#---------- Clear scene ----------#
class CleanSceneOperator(bpy.types.Operator):
    bl_idname = "object.scanrig_clean"
    bl_label = "Clean The Scene"
    bl_description = "Clean completely the scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Clean the whole scene
        for o in bpy.data.objects:
            bpy.data.objects.remove(o, do_unlink=True)
        for c in bpy.data.cameras:
            bpy.data.cameras.remove(c, do_unlink=True)
        for l in bpy.data.lights:
            bpy.data.lights.remove(l, do_unlink=True)
        for c in bpy.data.collections:
            bpy.data.collections.remove(c, do_unlink=True)

        context.scene.RenderPropertyGroup.renderReady = False

        return {'FINISHED'}

#---------- Project settings ----------#
class SettingsOperator(bpy.types.Operator):
    bl_idname = "object.scanrig_settings"
    bl_label = "Set Project Settings"
    bl_description = "Set the project settings corresponding to the FSCAM_CU135 cameras"
    bl_options = {'REGISTER', 'UNDO'}

    tileSize: bpy.props.IntProperty(name="Tiles Size", description="Size of the rendering tiles", default=256, min=64, max=1024, step=32)
    renderSamplesNumber: bpy.props.IntProperty(name="Samples", description="Number of samples for rendering", default=128, min=16, max=1024, step=16)

    def execute(self, context):

        # Useful variables
        rdr = context.scene.render
        cle = context.scene.cycles

        rdr.engine = 'CYCLES'
        cle.device = 'GPU'
        cle.samples = self.renderSamplesNumber
        cle.caustics_reflective = False
        cle.caustics_refractive = False

        rdr.resolution_x = 4208
        rdr.resolution_y = 3120

        rdr.tile_x = self.tileSize
        rdr.tile_y = self.tileSize

        # World settings
        context.scene.world.use_nodes = False
        context.scene.world.color = (0, 0, 0)

        return {'FINISHED'}

#---------- Settings for setting up the ScanRig model ----------#
class SetupOperator(bpy.types.Operator):
    bl_idname = "object.scanrig_setup"
    bl_label = "Setup The Scene"
    bl_description = "Create cameras and lights to reproduce a ScanRig model"
    bl_options = {'REGISTER', 'UNDO'}

    camDistance: bpy.props.FloatProperty(name="Camera Distance", description="Distance (in meters) from the center of the world", default=0.5, min=0.1, max=1) # In meters
    flashDistance: bpy.props.FloatProperty(name="Flash Distance", description="Distance (in meters) from the center of the world", default=1, min=0.1, max=2) # In meters
    ledDistance: bpy.props.FloatProperty(name="Led Distance", description="Distance (in meters) from the center of the world", default=1, min=0.1, max=2) # In meters
    ledAngle: bpy.props.FloatProperty(name="Led Angle", description="Angle (in degrees) around the center of the world", default=37.5, min=0, max=45) # In degrees
    
    nbCamera: bpy.props.IntProperty(name="Number of Cameras", description="Number of cameras on one slice", default=3, min=1, max=25, step=1)
    startAngle: bpy.props.FloatProperty(name="Starting Angle", description="Angle of start for the column of cameras", default=-30, min=-80, max=80)
    stopAngle: bpy.props.FloatProperty(name="Stopping Angle", description="Stopping angle for the column of cameras", default=30, min=-80, max=80)

    # - Icosahedron
    nbSubdiv: bpy.props.IntProperty(name="Number of Subdivisions", description="Number of dome shape's subdivisions", default=1, min=1, max=3, step=1)

    # - UV Sphere
    nbSegment: bpy.props.IntProperty(name="Number of segments", description="Number of sphere's rings", default=16, min=3, max=32, step=1)
    nbRing: bpy.props.IntProperty(name="Number of rings", description="Number of sphere's rings", default=8, min=3, max=16, step=1)

    # - Dome distance (original value at 1)
    domeDistance: bpy.props.FloatProperty(name="Dome Distance", description="Distance (in meters) from the center of the world", default=1, min=0, max=10) # In meters

    def execute(self, context):
        # Create our collection if needed
        if bpy.data.collections.get("ScanRigCollection") is None:
            ScanRigCollection = bpy.data.collections.new("ScanRigCollection")
            context.scene.collection.children.link(ScanRigCollection)

        # Delete objects in our collection
        for o in bpy.data.collections.get("ScanRigCollection").objects:
            bpy.data.objects.remove(o, do_unlink=True)

        # Creating cameras collection
        cameras = bpy.data.objects.new('Cameras', None) # None for empty object
        cameras.location = (0,0,0)
        cameras.empty_display_type = 'PLAIN_AXES'
        self.linkToScanRigCollection(cameras)

        domeShape = context.scene.RenderPropertyGroup.domeShape

        if domeShape == "I" :
            # Create icosahedron
            nbCameras = scanRigAddon_icoCreation.create(context, self, cameras)
            context.scene.RenderPropertyGroup.nbCam = nbCameras 

        elif domeShape == "U" :
            # Create UV sphere
            nbCameras = scanRigAddon_uvCreation.create(context, self, cameras)
            context.scene.RenderPropertyGroup.nbCam = nbCameras 

        elif domeShape == "S" :
            # Create slice within sphere
            scanRigAddon_sphereCreation.create(context, self, cameras)
            context.scene.RenderPropertyGroup.nbCam = self.nbCamera

        context.scene.RenderPropertyGroup.renderReady = True # Set rendering Ready

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        if context.object is not None:

            domeShape = context.scene.RenderPropertyGroup.domeShape

            col1 = layout.column()
            col1.label(text="Setup Management")

            row = col1.row()
            row.prop(self, "flashDistance")
            row = col1.row()
            row.prop(self, "ledDistance")
            row = col1.row()
            row.prop(self, "ledAngle")

            if domeShape == "S" :
                
                col2 = layout.column()
                col2.label(text="Slice Camera Management")

                row = col2.row()
                row.prop(self, "nbCamera")
                row = col2.row()
                row.prop(self, "camDistance")
                row = col2.row()
                row.prop(self, "startAngle")
                row = col2.row()
                row.prop(self, "stopAngle")

            if domeShape == "I" :
                col2 = layout.column()
                col2.label(text="Subdivision Management")

                row = col2.row()
                row.prop(self, "nbSubdiv")

            if domeShape == "U" :
                col2 = layout.column()
                col2.label(text="Segments and Rings Management")

                row = col2.row()
                row.prop(self, "nbSegment")
                row = col2.row()
                row.prop(self, "nbRing")

            col3 = layout.column()
            col3.label(text="Dome Management")

            row = col3.row()
            row.prop(self, "domeDistance")

    def linkToScanRigCollection(self, obj):
        bpy.data.collections['ScanRigCollection'].objects.link(obj) # Link to our collection

    def createCam(self, name, fov):
        cam = bpy.data.cameras.new(name)
        cam.lens_unit = 'FOV'
        cam.angle = math.radians(fov)
        return cam

    def createCameraObj(self, context, name, cam, loc = (0.0, 0.0, 0.0), rot = (0.0, 0.0, 0.0)):
        radiansRot = tuple([math.radians(a) for a in rot]) # Convert angles to radians
        obj = bpy.data.objects.new(name, cam)
        obj.location = loc
        obj.rotation_euler = radiansRot
        obj.scale = (0.2, 0.2, 0.2) # Nothing changes but it is easier to read in the 3D Viewer like this

        self.linkToScanRigCollection(obj)

        active = context.view_layer.objects.active # Move origin (could be improved)
        context.view_layer.objects.active  = obj
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
        context.view_layer.objects.active = active

        return obj

    def createLight(self, name, type, radius) :
        light = bpy.data.lights.new(name, type)
        light.shadow_soft_size = radius * 0.25

        return light

    def createLightObj(self, context, name, light, loc = (0.0, 0.0, 0.0), rot = (0.0, 0.0, 0.0)) :
        radiansRot = tuple([math.radians(a) for a in rot]) # Convert angles to radians

        obj = bpy.data.objects.new(name, light) # Set object settings
        obj.location = loc
        obj.rotation_euler = radiansRot

        self.linkToScanRigCollection(obj)
        return obj

    def createFlashLight(self, name) :
        return self.createLight(name, 'POINT', 4)

    def createLedLight(self, name) :
        return self.createLight(name, 'AREA', 3)

#---------- Scene Properties ----------#
class RenderPropertyGroup(bpy.types.PropertyGroup):

    renderReady: bpy.props.BoolProperty(name="Toggle Option")
    renderMode: bpy.props.EnumProperty(name='Render mode', description='Choose render mode', 
                                        items={
                                            ('A', 'Ambiant', 'Render with ambiant lights only'),
                                            ('P', 'Photometry', 'Render with Photometry lights only'),
                                            ('AP', 'Ambiant & Photometry', 'Render full light setup')
                                        }, default='A')
    rotAngle: bpy.props.IntProperty(name="Rotation Angle", description="Angle (in degrees) separating the take of two consecutive pictures", default=15, min=15, max=180, step=15) # In degrees
    stepDividerPhotometry: bpy.props.IntProperty(name="Photometry Step Divider", description="If 1, photometry will be done on each rotation step. If 2, it will be done one step out of 2, etc", default=3, min=1, max=12, step=1)
    nbCam: bpy.props.IntProperty()
    exportFolder: bpy.props.StringProperty(name="Export Folder", description="Relative export folder", default="img")
    
    # Render map type management
    bool_albedo: bpy.props.BoolProperty(name="Albedo",
                                        description="Render albedo map",
                                        default = True)
    bool_depth: bpy.props.BoolProperty(name="Depth",
                                        description="Render depth map",
                                        default = True)
    bool_normal: bpy.props.BoolProperty(name="Normal",
                                        description="Render normal map",
                                        default = True)
    bool_id: bpy.props.BoolProperty(name="Id",
                                        description="Render id map",
                                        default = True)
    bool_basic: bpy.props.BoolProperty(name="Basic",
                                        description="Basic render",
                                        default = True)

    # Dome shape management
    domeShape: bpy.props.EnumProperty(name='Camera Dome Shape', description='Choose the shape of the camera dome', 
                                        items={
                                            ('S', 'Sphere', 'Place the cameras along the wall of a sphere'),
                                            ('I', 'Icosahedron', 'Place the cameras along the vertices of an Icosahedron'),
                                            ('U', 'UV Sphere', 'Place the cameras along the vertices of an UV Sphere')
                                        }, default='S')

class RenderOperator(bpy.types.Operator):
    bl_idname = "object.scanrig_render"
    bl_label = "Start Render"
    bl_description = "Start render with the set parameters. Please, open the console to be able to follow the rendering. When a camera has done its work, it will ask you if you want to continue or not"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.RenderPropertyGroup.renderReady == True

    def execute(self, context):

        # Get the img folder path
        filePath = bpy.data.filepath
        curDir = os.path.dirname(filePath)
        imgDir = os.path.join(curDir, context.scene.RenderPropertyGroup.exportFolder)

        # Create the img folder if it does not exist
        os.makedirs(imgDir, exist_ok=True)

        #----------- GET OBJECTS -----------#

        origin = bpy.context.scene.objects['Cameras']
        
        camerasObjs = [context.scene.objects[f'Camera_{nCam}'] for nCam in range(context.scene.RenderPropertyGroup.nbCam)]
        flashLightsObjs = [context.scene.objects['FlashFront'], context.scene.objects['FlashBack'], context.scene.objects['FlashLeft'], context.scene.objects['FlashRight'], context.scene.objects['FlashTop'], context.scene.objects['FlashBottom']]
        ledLightsObjs = [context.scene.objects['LedFront'], context.scene.objects['LedBack'], context.scene.objects['LedLeft'], context.scene.objects['LedRight'], context.scene.objects['LedTop'], context.scene.objects['LedBottom']]

        print("---------- Rendering start ----------")

        #----------- PRE-RENDER -----------#
        origin.rotation_euler[2] = 0

        domeShape = context.scene.RenderPropertyGroup.domeShape

        if domeShape == "S" :
            # Get render settings
            rotAngle = context.scene.RenderPropertyGroup.rotAngle
            renderMode = context.scene.RenderPropertyGroup.renderMode
            stepDividerPhotometry= context.scene.RenderPropertyGroup.stepDividerPhotometry

            # Turn off all lights
            for light in flashLightsObjs:
                light.data.energy = 0
            for light in ledLightsObjs:
                light.data.energy = 0

            for cam in camerasObjs:
                context.scene.camera = cam

                #----------- AMBIANT RENDER -----------#
                if renderMode == 'A' or renderMode == 'AP':
                    for light in ledLightsObjs:
                        light.data.energy = 15

                    for step in range(0, int(360/rotAngle)):
                        origin.rotation_euler[2] = math.radians(step * rotAngle) # Rotate the origin on each step of the process
                        
                        scanRigAddon_render.render(context, imgDir, f"{cam.name}_{int(math.degrees(origin.rotation_euler[2]))}_ambiant")
                   
                    # self.__breakMessage()

                    for light in ledLightsObjs:
                        light.data.energy = 0

                #----------- PHOTOMETRY RENDER -----------#
                if renderMode == 'P' or renderMode == 'AP':

                    for step in range(0, int(360/(rotAngle*stepDividerPhotometry))):
                        origin.rotation_euler[2] = math.radians(step * rotAngle * stepDividerPhotometry) # Rotate the origin on each step of the process
                        for light in flashLightsObjs:
                            light.data.energy = 100

                            scanRigAddon_render.render(context, imgDir, f"{cam.name}_{int(math.degrees(origin.rotation_euler[2]))}_{light.name}")
                            
                            light.data.energy = 0
                    # self.__breakMessage()

        else :
            for cam in camerasObjs:
                context.scene.camera = cam

                scanRigAddon_render.render(context, imgDir, f"{cam.name}")

                # self.__breakMessage()

        return {'FINISHED'}

    #def __startRender(self, imgDir, imgName):
    #        bpy.context.scene.render.filepath = os.path.join(imgDir, imgName)
    #        bpy.ops.render.render(write_still=True)

    # def __breakMessage(self):
    #         doContinue = int(input("Do you want to continue to render with the other cameras? YES = 1 / NO = 0\n"))
    #         if doContinue == 0:
    #             raise Exception()

classes = [ScanRigPanel, CleanSceneOperator, SettingsOperator, SetupOperator, RenderPropertyGroup, RenderOperator]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.RenderPropertyGroup = bpy.props.PointerProperty(type = RenderPropertyGroup)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.RenderPropertyGroup

if __name__ == "__main__":
    register()
