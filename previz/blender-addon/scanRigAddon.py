#---------- Informations concernant le plugin ----------#
bl_info = {
    "name" : "ScanRig Addon", 
    "author" : "Julien Haudegond & Enguerrand De Smet",\
    "description" : "Script used to test the capture of the ScanRig device",
    "blender" : (2, 80, 0),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

#---------- Imports ----------#
import os
import bpy
import math
import mathutils

class ScanRigPanel(bpy.types.Panel):
    bl_idname = 'SCANRIG_PT_ScanRig'
    bl_label = 'ScanRig Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ScanRig"

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator('object.scanrig_settings')
        row = layout.row()
        row.operator('object.scanrig_clean')
        row = layout.row()
        row.operator('object.scanrig_setup')

        if context.scene.RenderPropertyGroup.renderReady:
            row = layout.row()        
            row.prop(context.scene.RenderPropertyGroup, "rotAngle")
            row = layout.row()        
            row.prop(context.scene.RenderPropertyGroup, "stepDividerPhotometry")
            row = layout.row()        
            row.prop(context.scene.RenderPropertyGroup, "renderMode")
            row = layout.row()        
            row.prop(context.scene.RenderPropertyGroup, "exportFolder")
            row = layout.row()
            row.operator('object.scanrig_render')
        else:
            row = layout.row()
            row.label(text = "Render not ready")

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
    
    def execute(self, context):
        self.nbCam = self.nbCamera
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

        # Computing the angle between cams
        deltaAngle = (self.stopAngle - self.startAngle)/(self.nbCamera -1)

        #---------- Create cam ----------#
        cam = self.__createCam("Camera", 56)
        for i in range(self.nbCamera):
            camName = f"Camera_{i}"
            camAngle = self.startAngle + i*deltaAngle
            current_cam = self.__createCameraObj(context, camName, cam, (self.camDistance, 0, 0), (90, 0, 90))
            current_cam.parent = cameras
            cameras.rotation_euler[1] = math.radians(camAngle)
            current_cam.select_set(True)
            context.view_layer.objects.active  = current_cam # (could be improved)
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        cameras.rotation_euler[1] = math.radians(0)
        for i in range(self.nbCamera):
            camName = f"Camera_{i}"
            current_cam = context.scene.objects[camName]
            current_cam.parent = cameras

        #---------- Create flash Light ----------#
        flashLight = self.__createFlashLight("FlashLight")
        FlashFront = self.__createLightObj(context, "FlashFront", flashLight, (0, -self.flashDistance, 0))
        FlashBack = self.__createLightObj(context, "FlashBack", flashLight, (0, self.flashDistance, 0))
        FlashLeft = self.__createLightObj(context, "FlashLeft", flashLight, (self.flashDistance, 0, 0))
        FlashRight = self.__createLightObj(context, "FlashRight", flashLight, (-self.flashDistance, 0, 0))
        FlashTop = self.__createLightObj(context, "FlashTop", flashLight, (0, 0, self.flashDistance))
        FlashBottom = self.__createLightObj(context, "FlashBottom", flashLight, (0, 0, -self.flashDistance))

        #---------- Create Flash Light Collection ----------#
        flashLights = bpy.data.objects.new('FlashLights', None) # None for empty object
        flashLights.location = (0,0,0)
        flashLights.empty_display_type = 'PLAIN_AXES'

        self.linkToScanRigCollection(flashLights)
        # Relinking
        FlashFront.parent = FlashBack.parent = FlashLeft.parent = FlashRight.parent = FlashTop.parent = FlashBottom.parent = flashLights

        #---------- Create Led light ----------#
        ledlight = self.__createLedLight("Ledlight")
        LedFront = self.__createLightObj(context, "LedFront", ledlight, (0, -self.ledDistance, 0), (90, 0, 0))
        LedBack = self.__createLightObj(context, "LedBack", ledlight, (0, self.ledDistance, 0), (-90, 0, 0))
        LedLeft = self.__createLightObj(context, "LedLeft", ledlight, (self.ledDistance, 0, 0), (0, 90, 0))
        LedRight = self.__createLightObj(context, "LedRight", ledlight, (-self.ledDistance, 0, 0), (0, -90, 0))
        LedTop = self.__createLightObj(context, "LedTop", ledlight, (0, 0, self.ledDistance), (0, 0, 0))
        LedBottom = self.__createLightObj(context, "LedBottom", ledlight, (0, 0, -self.ledDistance), (180, 0, 0))

        #---------- Rotate Led light by 37.5 degrees ----------#
        ledLights = bpy.data.objects.new('LedLights', None) # None for empty object
        ledLights.location = (0,0,0)
        ledLights.empty_display_type = 'PLAIN_AXES'

        self.linkToScanRigCollection(ledLights)
        # Relinking
        LedFront.parent = LedBack.parent = LedLeft.parent = LedRight.parent = LedTop.parent = LedBottom.parent = ledLights
        ledLights.rotation_euler[2] = math.radians(self.ledAngle)

        context.scene.RenderPropertyGroup.nbCam = self.nbCamera
        context.scene.RenderPropertyGroup.renderReady = True # Set rendering Ready

        return {'FINISHED'}

    def linkToScanRigCollection(self, obj):
        bpy.data.collections['ScanRigCollection'].objects.link(obj) # Link to our collection

    def __createCam(self, name, fov):
        cam = bpy.data.cameras.new(name)
        cam.lens_unit = 'FOV'
        cam.angle = math.radians(fov)
        return cam

    def __createCameraObj(self, context, name, cam, loc = (0.0, 0.0, 0.0), rot = (0.0, 0.0, 0.0)):
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

    def __createLight(self, name, type, radius) :
        light = bpy.data.lights.new(name, type)
        light.shadow_soft_size = radius * 0.25

        return light

    def __createLightObj(self, context, name, light, loc = (0.0, 0.0, 0.0), rot = (0.0, 0.0, 0.0)) :
        radiansRot = tuple([math.radians(a) for a in rot]) # Convert angles to radians

        obj = bpy.data.objects.new(name, light) # Set object settings
        obj.location = loc
        obj.rotation_euler = radiansRot

        self.linkToScanRigCollection(obj)
        return obj

    def __createFlashLight(self, name) :
        return self.__createLight(name, 'POINT', 4)

    def __createLedLight(self, name) :
        return self.__createLight(name, 'AREA', 3)

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
    exportFolder: bpy.props.StringProperty(name="Export Folder", description="RElative export folder", default="img")

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
                    self.__startRender(imgDir, f"{cam.name}_{int(math.degrees(origin.rotation_euler[2]))}_ambiant")
                # self.__breakMessage()

                for light in ledLightsObjs:
                    light.data.energy = 0

            #----------- PHOTOMETRY RENDER -----------#
            if renderMode == 'P' or renderMode == 'AP':

                for step in range(0, int(360/(rotAngle*stepDividerPhotometry))):
                    origin.rotation_euler[2] = math.radians(step * rotAngle * stepDividerPhotometry) # Rotate the origin on each step of the process
                    for light in flashLightsObjs:
                        light.data.energy = 100
                        self.__startRender(imgDir, f"{cam.name}_{int(math.degrees(origin.rotation_euler[2]))}_{light.name}")
                        light.data.energy = 0
                # self.__breakMessage()

        return {'FINISHED'}

    def __startRender(self, imgDir, imgName):
            bpy.context.scene.render.filepath = os.path.join(imgDir, imgName)
            bpy.ops.render.render(write_still=True)

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