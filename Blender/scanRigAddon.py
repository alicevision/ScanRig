#---------- Informations concernant le plugin ----------#
bl_info = {
    "name" : "scanRig addon", 
    "author" : "Julien Haudegond & Enguerrand De smet",\
    "description" : "script permettant de tester la capture du dispositif scanRig",
    "blender" : (2, 80, 0),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

#---------- Imports ----------#
import os
import bpy
import math
from mathutils import Matrix

class ScanRigPanel(bpy.types.Panel):
    bl_idname = 'SCANRIG_PT_ScanRig'
    bl_label = 'scan rig panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ScanRig"
    # enum in [‘WINDOW’, ‘HEADER’, ‘CHANNELS’, ‘TEMPORARY’, ‘UI’, ‘TOOLS’, ‘TOOL_PROPS’, ‘PREVIEW’, ‘HUD’, ‘NAVIGATION_BAR’, ‘EXECUTE’, ‘FOOTER’, ‘TOOL_HEADER’], default ‘WINDOW’num in [‘WINDOW’, ‘HEADER’, ‘CHANNELS’, ‘TEMPORARY’, ‘UI’, ‘TOOLS’, ‘TOOL_PROPS’, ‘PREVIEW’, ‘HUD’, ‘NAVIGATION_BAR’, ‘EXECUTE’, ‘FOOTER’, ‘TOOL_HEADER’], default ‘WINDOW’

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
            # select objs in our collection
            for obj in bpy.data.collections["ScanRigCollection"].objects :
                bpy.data.objects.remove(obj, do_unlink=True)

        context.scene.RenderPropertyGroup.renderReady = False
            
        return {'FINISHED'}

class SettingsOperator(bpy.types.Operator):
    bl_idname = "object.scanrig_settings"
    bl_label = "set project setting"
    bl_options = {'REGISTER', 'UNDO'}

    tileSize: bpy.props.IntProperty(name="tiles size", default=256, min=64, max=1024, step=32) #in meters
    renderSamplesNumber: bpy.props.IntProperty(name="number of sample for rendering", default=128, min=16, max=1024, step=16) #in meters

    def execute(self, context):

        #useful variables
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

        #world setting
        context.scene.world.use_nodes = False
        context.scene.world.color = (0, 0, 0)

        return {'FINISHED'}

class SetupOperator(bpy.types.Operator):
    bl_idname = "object.scanrig_setup"
    bl_label = "setup the scene"
    bl_options = {'REGISTER', 'UNDO'}

    camDistance: bpy.props.FloatProperty(name="camDistance", default=0.5, min=0.1, max=1) #in meters
    flashDistance: bpy.props.FloatProperty(name="flashDistance", default=1, min=0.1, max=2) #in meters
    ledDistance: bpy.props.FloatProperty(name="ledDistance", default=1, min=0.1, max=2) #in meters
    ledAngle: bpy.props.FloatProperty(name="ledDistance", default=37.5, min=0, max=45) #in degrees

    def execute(self, context):

        # delete objects in other collection exept ScanRigCollection
        for c in bpy.data.collections:
            if c.name != 'ScanRigProtectedCollection':
                for obj in c.objects:
                    bpy.data.objects.remove(obj, do_unlink=True)
                bpy.data.collections.remove(c, do_unlink=True)

        # create our collection if needed
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
        bpy.data.collections['ScanRigCollection'].objects.link(cameras) # link to our collection

        # Bottom cam
        camBottom.parent = cameras
        cameras.rotation_euler[1] = math.radians(30)
        camBottom.select_set(True)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        # Top cam
        camTop.parent = cameras
        cameras.rotation_euler[1] = math.radians(-30)
        camTop.select_set(True)
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
        bpy.data.collections['ScanRigCollection'].objects.link(ledLights) # link to our collection

        # Relinking
        LedFront.parent = LedBack.parent = LedLeft.parent = LedRight.parent = ledLights
        ledLights.rotation_euler[2] = math.radians(self.ledAngle)

        context.scene.RenderPropertyGroup.renderReady = True #set renderring Ready

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
    renderMode: bpy.props.EnumProperty( name='render mode', description='choose render mode', 
                                        items={
                                            ('A', 'Ambiant', 'render with ambiant lights only'),
                                            ('P', 'Photometry', 'render with Photometry lights only'),
                                            ('AP', 'Ambiant & Photometry', 'render full light setup')
                                        }, default='A')
    rotAngle: bpy.props.IntProperty(name="angle of rotation", default=15, min=15, max=180, step=15) #in meters
    stepDividerPhotometry: bpy.props.IntProperty(name="step Divider for photometry render", default=3, min=1, max=12, step=1) #in meters

class RenderOperator(bpy.types.Operator):
    bl_idname = "object.scanrig_render"
    bl_label = "start Ambiant render"
    bl_options = {'REGISTER', 'UNDO'}

    rotAngle: bpy.props.IntProperty(name="angle of rotation", default=15, min=15, max=180, step=15) #in meters

    @classmethod
    def poll(cls, context):
        return context.scene.RenderPropertyGroup.renderReady == True

    def execute(self, context):

        #----------- PREPARATION -----------#

        # Get the img folder path
        filePath = bpy.data.filepath
        curDir = os.path.dirname(filePath)
        imgDir = os.path.join(curDir, "img")

        # Create the img folder if it doesn't exist
        os.makedirs(imgDir, exist_ok=True)

        #----------- GET OBJECTS -----------#


        origin = bpy.context.scene.objects['cameras']

        # link bras to origin if exist in ScanRigProtectedCollection
        bras = bpy.data.collections['ScanRigProtectedCollection'].objects['BRAS'] 
        brasParent = None
        if bras != None :
            brasParent = bras.parent
            bras.parent = origin
        else :
            print("object BRAS not found")

        camerasObjs = [context.scene.objects['camTop'], context.scene.objects['camMiddle'], context.scene.objects['camBottom']]
        flashLightsObjs = [context.scene.objects['flashFront'], context.scene.objects['flashBack'], context.scene.objects['flashLeft'], context.scene.objects['flashRight'], context.scene.objects['flashTop'], context.scene.objects['flashBottom']]
        ledLightsObjs = [context.scene.objects['LedFront'], context.scene.objects['LedBack'], context.scene.objects['LedLeft']]

        print("---------- rendering start ----------")

        #----------- PRE-RENDER -----------#
        origin.rotation_euler[2] = 0

        # get render settings
        rotAngle = context.scene.RenderPropertyGroup.rotAngle
        renderMode = context.scene.RenderPropertyGroup.renderMode
        stepDividerPhotometry= context.scene.RenderPropertyGroup.stepDividerPhotometry

        # turn all flash
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


        # unlink bras if needed
        if bras != None :
            bras.parent = brasParent

        return {'FINISHED'}

    def __startRender(self, imgDir, imgName):
            bpy.context.scene.render.filepath = os.path.join(imgDir, imgName)
            bpy.ops.render.render(write_still=True)

    def __breakMessage(self):
            # MESSAGE DE CONFIRMATION
            stop = int(input("Arreter ? OUI = 1 / NON = 0\n"))
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