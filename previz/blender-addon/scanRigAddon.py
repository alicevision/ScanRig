#---------- Informations concernant le plugin ----------#
bl_info = {
    "name" : "ScanRig Addon", 
    "author" : "Julien Haudegond & Enguerrand De smet",\
    "description" : "Script used to test the capture of the scanRig device",
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
    bl_label = 'scan rig panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ScanRig"

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator('object.scanrig_settings')
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
            row.operator('object.scanrig_render')
        else:
            row = layout.row()
            row.label(text = "Render not ready")

class CleanSceneOperator(bpy.types.Operator):
    bl_idname = "object.scanrig_clean"
    bl_label = "clean the Scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')

        if bpy.data.collections.get("ScanRigCollection") is None:
            print("the ScanRigCollection does not exist ")
        else :
            # Select objects in our collection
            for obj in bpy.data.collections["ScanRigCollection"].objects :
                bpy.data.objects.remove(obj, do_unlink=True)

        context.scene.RenderPropertyGroup.renderReady = False
            
        return {'FINISHED'}

class SettingsOperator(bpy.types.Operator):
    bl_idname = "object.scanrig_settings"
    bl_label = "set project setting"
    bl_options = {'REGISTER', 'UNDO'}

    tileSize: bpy.props.IntProperty(name="tiles size", default=256, min=64, max=1024, step=32)
    renderSamplesNumber: bpy.props.IntProperty(name="number of sample for rendering", default=128, min=16, max=1024, step=16)

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
    bl_label = "setup the scene"
    bl_options = {'REGISTER', 'UNDO'}

    camDistance: bpy.props.FloatProperty(name="camDistance", default=0.5, min=0.1, max=1) # In meters
    flashDistance: bpy.props.FloatProperty(name="flashDistance", default=1, min=0.1, max=2) # In meters
    ledDistance: bpy.props.FloatProperty(name="ledDistance", default=1, min=0.1, max=2) # In meters
    ledAngle: bpy.props.FloatProperty(name="ledDistance", default=37.5, min=0, max=45) # In degrees

    def execute(self, context):

        # Delete objects in other collection except ScanRigCollection
        for c in bpy.data.collections:
            if c.name != 'ScanRigProtectedCollection':
                for obj in c.objects:
                    bpy.data.objects.remove(obj, do_unlink=True)
                bpy.data.collections.remove(c, do_unlink=True)

        # Create our collections if needed
        if bpy.data.collections.get("ScanRigCollection") is None:
            ScanRigCollection = bpy.data.collections.new("ScanRigCollection")
            context.scene.collection.children.link(ScanRigCollection)
        if bpy.data.collections.get("ScanRigProtectedCollection") is None:
            ScanRigProtectedCollection = bpy.data.collections.new("ScanRigProtectedCollection")
            context.scene.collection.children.link(ScanRigProtectedCollection)

        #---------- Create cam ----------#
        camMiddle = self.__createCam(context, "camMiddle", (self.camDistance,0,0), (90, 0, 90), 56)
        camTop = self.__createCam(context, "camTop", (self.camDistance,0,0), (90, 0, 90), 56)
        camBottom = self.__createCam(context, "camBottom", (self.camDistance,0,0), (90, 0, 90), 56)

        #---------- Make the 30 degrees angle ----------#
        cameras = bpy.data.objects.new('cameras', None) # None for empty object
        cameras.location = (0,0,0)
        cameras.empty_display_type = 'PLAIN_AXES'
        bpy.data.collections['ScanRigCollection'].objects.link(cameras) # Link to our collection

        # Top cam
        camTop.parent = cameras
        cameras.rotation_euler[1] = math.radians(-30)
        camTop.select_set(True)

        context.view_layer.objects.active  = camTop # (could be improved)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        # Bottom cam
        camBottom.parent = cameras
        cameras.rotation_euler[1] = math.radians(30)
        camBottom.select_set(True)

        context.view_layer.objects.active  = camBottom # (could be improved)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        # Relinking
        cameras.rotation_euler[1] = math.radians(0)
        camBottom.parent = camMiddle.parent = camTop.parent = cameras

        #---------- Create flash Light ----------#
        self.__createFlashLight(context, "flashFront", (0, -self.flashDistance, 0))
        self.__createFlashLight(context, "flashBack", (0, self.flashDistance, 0))
        self.__createFlashLight(context, "flashLeft", (self.flashDistance, 0, 0))
        self.__createFlashLight(context, "flashRight", (-self.flashDistance, 0, 0))
        self.__createFlashLight(context, "flashTop", (0, 0, self.flashDistance))
        self.__createFlashLight(context, "flashBottom", (0, 0, -self.flashDistance))

        #---------- Create Led light ----------#
        LedFront = self.__createLedLight(context, "LedFront", (0, -self.ledDistance, 0), (90, 0, 0))
        LedBack = self.__createLedLight(context, "LedBack", (0, self.ledDistance, 0), (-90, 0, 0))
        LedLeft = self.__createLedLight(context, "LedLeft", (self.ledDistance, 0, 0), (0, 90, 0))
        LedRight = self.__createLedLight(context, "LedRight", (-self.ledDistance, 0, 0), (0, -90, 0))

        #---------- Rotate Led light by 37.5 degrees ----------#
        ledLights = bpy.data.objects.new('ledLights', None) # None for empty object
        ledLights.location = (0,0,0)
        ledLights.empty_display_type = 'PLAIN_AXES'
        bpy.data.collections['ScanRigCollection'].objects.link(ledLights) # Link to our collection

        # Relinking
        LedFront.parent = LedBack.parent = LedLeft.parent = LedRight.parent = ledLights
        ledLights.rotation_euler[2] = math.radians(self.ledAngle)

        context.scene.RenderPropertyGroup.renderReady = True # Set renderring Ready

        return {'FINISHED'}

    def __createCam(self, context, name, loc, rot, angle):      # private method
        radiansRot = tuple([math.radians(a) for a in rot]) #convert angles in radians
        # bpy.ops.object.camera_add(location=loc, rotation=radiansRot)
        
        cam = bpy.data.cameras.new(name) # set cam setting
        cam.lens_unit = 'FOV'
        cam.angle = math.radians(angle)

        obj = bpy.data.objects.new(name, cam) #set object setting 
        obj.location = loc
        obj.rotation_euler=radiansRot
        bpy.data.collections['ScanRigCollection'].objects.link(obj) # link to our collection

        active = context.view_layer.objects.active # changer origin (could be improved)
        context.view_layer.objects.active  = obj
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
        context.view_layer.objects.active = active

        return obj

    def __createLight(self, context, name, type, radius, loc = (0, 0, 0), rot = (0, 0, 0)) :
        radiansRot = tuple([math.radians(a) for a in rot]) #convert angles in radians
        light = bpy.data.lights.new(name, type)
        light.shadow_soft_size = radius * 0.25

        obj = bpy.data.objects.new(name, light) #set object setting 
        obj.location = loc
        obj.rotation_euler=radiansRot

        bpy.data.collections['ScanRigCollection'].objects.link(obj) # link to our collection
        return obj

    def __createFlashLight(self, context, name, loc) :
        return self.__createLight(context, name, 'POINT', 4, loc)

    def __createLedLight(self, context, name, loc, rot) :
        return self.__createLight(context, name, 'AREA', 3, loc, rot)

class RenderPropertyGroup(bpy.types.PropertyGroup):

    renderReady: bpy.props.BoolProperty(name="Toggle Option")
    renderMode: bpy.props.EnumProperty(name='Render mode', description='Choose render mode', 
                                        items={
                                            ('A', 'Ambiant', 'Render with ambiant lights only'),
                                            ('P', 'Photometry', 'Render with Photometry lights only'),
                                            ('AP', 'Ambiant & Photometry', 'Render full light setup')
                                        }, default='A')
    rotAngle: bpy.props.IntProperty(name="Angle of rotation", default=15, min=15, max=180, step=15) #in degrees
    stepDividerPhotometry: bpy.props.IntProperty(name="Step Divider for photometry render", default=3, min=1, max=12, step=1)

class RenderOperator(bpy.types.Operator):
    bl_idname = "object.scanrig_render"
    bl_label = "Start Ambiant render"
    bl_options = {'REGISTER', 'UNDO'}

    rotAngle: bpy.props.IntProperty(name="angle of rotation", default=15, min=15, max=180, step=15) #in degrees

    @classmethod
    def poll(cls, context):
        return context.scene.RenderPropertyGroup.renderReady == True

    def execute(self, context):

        # Get the img folder path
        filePath = bpy.data.filepath
        curDir = os.path.dirname(filePath)
        imgDir = os.path.join(curDir, "img")

        # Create the img folder if it doesn't exist
        os.makedirs(imgDir, exist_ok=True)

        #----------- GET OBJECTS -----------#

        origin = bpy.context.scene.objects['cameras']

        # link arm to origin if exist in ScanRigProtectedCollection
        if bpy.data.collections['ScanRigProtectedCollection'].objects.get('arm') is not None:
            arm = bpy.data.collections['ScanRigProtectedCollection'].objects['arm'] 
        else:
            arm = None

        armParent = None
        if arm != None :
            armParent = arm.parent
            arm.parent = origin
        else :
            print("object arm not found")

        camerasObjs = [context.scene.objects['camTop'], context.scene.objects['camMiddle'], context.scene.objects['camBottom']]
        flashLightsObjs = [context.scene.objects['flashFront'], context.scene.objects['flashBack'], context.scene.objects['flashLeft'], context.scene.objects['flashRight'], context.scene.objects['flashTop'], context.scene.objects['flashBottom']]
        ledLightsObjs = [context.scene.objects['LedFront'], context.scene.objects['LedBack'], context.scene.objects['LedLeft']]

        print("---------- Rendering start ----------")

        #----------- PRE-RENDER -----------#
        origin.rotation_euler[2] = 0

        # Get render settings
        rotAngle = context.scene.RenderPropertyGroup.rotAngle
        renderMode = context.scene.RenderPropertyGroup.renderMode
        stepDividerPhotometry= context.scene.RenderPropertyGroup.stepDividerPhotometry

        # Turn all flash lights
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
                self.__breakMessage()

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
                self.__breakMessage()


        # Unlink arm if needed
        if arm != None :
            arm.parent = armParent

        return {'FINISHED'}

    def __startRender(self, imgDir, imgName):
            bpy.context.scene.render.filepath = os.path.join(imgDir, imgName)
            bpy.ops.render.render(write_still=True)

    def __breakMessage(self):
            stop = int(input("Stop ? YES = 1 / NO = 0\n"))
            if stop == 1:
                raise Exception()

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