bl_info = {
    "name": "Brush Pressure Simulator",
    "author": "OscarVezz",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > N",
    "description": "Simulates pen pressure in Texture Paint",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import bpy
from bpy.props import *
 
 


class BrushStepProperties(bpy.types.PropertyGroup):
    
    brush_size : IntProperty(
        name = "Brush Size", 
        description = "The size of the Brush",
        default = 30,
        soft_min = 0, 
        soft_max = 300
    )
    
    brush_strength : FloatProperty(
        name = "Brush Strength",
        description = "The strength of the Brush",
        default = 1, 
        soft_min = 0, 
        soft_max = 1
    )
    
    brush_time : FloatProperty(
        name = "Timing",
        description = "The time it takes to reach this Brush",
        default = 1, 
        soft_min = 0.05, 
        soft_max = 10
    )
    
    brush_easing : EnumProperty(
        name = "Easing",
        description = "The easing curve of the Brush",
        items = [('Linear', "Linear", ""),
                 ('InCubic', "In_Cubic", ""),
                 ('OutCubic', "Out_Cubic", ""),
                 ('InExpo', "In_Expo", ""),
                 ('OutExpo', "Out_Expo", "")
        ]
    )




class ToolStates(bpy.types.PropertyGroup):
    
    showDebug : BoolProperty(name = "Show Debug Options")
    
    isRunning : BoolProperty(name = "Testing")
    stopTool : BoolProperty(name = "Stop")
    
    isFirstShift : BoolProperty(name = "FirstShift", default = True)
    prevShift : BoolProperty(name = "PrevShift")
    
    isFirstCtrl : BoolProperty(name = "FirstCtrl", default = True)
    prevCtrl : BoolProperty(name = "PrevCtrl")
    
    isFirstAlt : BoolProperty(name = "FirstAlt", default = True)
    prevAlt : BoolProperty(name = "PrevAlt")
    
    mousePress : BoolProperty(name = "Mouse Press")
    detectMouse : BoolProperty(name = "Mouse Move")




class BPS_PT_main_panel(bpy.types.Panel):
    bl_label = "Brush Pressure Simulator"
    bl_idname = "BPS_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Brush Tool"
    
    
    
    def draw(self, context):
        layout = self.layout
        brushSteps = context.scene.brush_steps
        brushStepSize = len(brushSteps)
        
        mytest = context.scene.tool_states
        
        
        
        if brushStepSize > 0:
            row = layout.row()
            row.label(text = "Default")     #row.label(text="Hello world!", icon='WORLD_DATA')
            
            row = layout.row()
            self.drawBrushHeader(row)
            
            row = layout.row()
            self.drawBrushStep(row, brushSteps[0], "/")
        
            row = layout.row()
            row.operator("bps.set_default_operator")
        
        
        
        signs = ["/","Shift","Ctrl","Alt"]
        if brushStepSize > 1:
            row = layout.row()
            row.label(text = " ")
            
            row = layout.row()
            row.label(text = "Brush Steps")
            
            row = layout.row()
            self.drawBrushHeader(row)
            for step in range(1, brushStepSize):
                row = layout.row()
                self.drawBrushStep(row, brushSteps[step], signs[step])
        
        row = layout.row()
        row.operator("bps.add_brush_operator")
        row.operator("bps.remove_brush_operator")
        
        
        
        row = layout.row()
        row.label(text = " ")
        
        row = layout.row()
        row.operator("bps.start_read")
        row = layout.row()
        row.operator("bps.stop_read")
        
        
        row = layout.row()
        row.prop(mytest, "showDebug")
        if mytest.showDebug:
            row = layout.row()
            row.prop(mytest, "isRunning")
            row.prop(mytest, "stopTool")
            #row.prop(mytest, "isFirstShift")


    
    def drawBrushStep(self, row, step, string):
        row = row.split(factor = 0.10)
        row.label(text = string)
        row = row.split(factor = 0.21)
        row.prop(step, "brush_size", icon_only = True)
        row = row.split(factor = 0.35)
        row.prop(step, "brush_strength", icon_only = True)
        row = row.split(factor = 0.52)
        row.prop(step, "brush_time", icon_only = True)
        row = row.split(factor = 1)
        row.prop(step, "brush_easing", text = "")



    def drawBrushHeader(self, row):
        row = row.split(factor = 0.15)
        row.label(text = "Key")
        row = row.split(factor = 0.17)
        row.label(text = "Size")
        row = row.split(factor = 0.42)
        row.label(text = "Strength")
        row.label(text = "Time")
        row.label(text = "Easing")





class BPS_OT_add_brush(bpy.types.Operator):
    bl_label = "Add Step"
    bl_idname = "bps.add_brush_operator"
    
    max_steps = 4
    
    def execute(self, context):
        
        size = len(bpy.context.scene.brush_steps)
        if size < self.max_steps:
            bpy.context.scene.brush_steps.add()
        return {'FINISHED'}




class BPS_OT_remove_brush(bpy.types.Operator):
    bl_label = "Remove Step"
    bl_idname = "bps.remove_brush_operator"
    
    min_steps = 0
    
    def execute(self, context):
        
        size = len(bpy.context.scene.brush_steps)
        if size > self.min_steps:
            bpy.context.scene.brush_steps.remove(len(bpy.context.scene.brush_steps) - 1)
        return {'FINISHED'}




class BPS_OT_set_default(bpy.types.Operator):
    bl_label = "Set Brush to Default"
    bl_idname = "bps.set_default_operator"
    
    def execute(self, context):
        
        bpy.context.scene.tool_settings.unified_paint_settings.size = bpy.context.scene.brush_steps[0].brush_size
        bpy.data.brushes["TexDraw"].strength = bpy.context.scene.brush_steps[0].brush_strength
        return {'FINISHED'}




class BPS_OT_start_read(bpy.types.Operator):
    bl_label = "Start Tool"
    bl_idname = "bps.start_read"
    
    
    _timer = None
    
    _calls_per_second = 20
    
    currentStep = 2
    maxSteps = 1
    type = 0
    
    Zfrom = 0
    Zto = 1
    
    Tfrom = 0
    Tto = 1
    
    
    def modal(self, context, event):
        if bpy.context.scene.tool_states.stopTool == True:
            self.cancel(context)
            bpy.context.scene.tool_states.isRunning = False
            bpy.context.scene.tool_states.stopTool = False
            return {'CANCELLED'}
        
        if event.type in {'ESC'}:
            bpy.context.scene.tool_states.stopTool = True
        
        
        
        if event.type in {'LEFTMOUSE'}:   #, 'MOUSEMOVE'}:# and event.value == 'PRESS': #Does not work???
            bpy.context.scene.tool_states.mousePress = True
            bpy.context.scene.tool_states.detectMouse = True
        if bpy.context.scene.tool_states.detectMouse:
            if event.type in {'MOUSEMOVE'}:
                bpy.context.scene.tool_states.mousePress = False
                bpy.context.scene.tool_states.detectMouse = False
            
        
        
        #if event.type in {'RIGHT_SHIFT', 'LEFT_SHIFT'}:
            #self.event.type = 'A'
            #return {'RUNNING_MODAL'}
        
        
        
        if event.alt and len(bpy.context.scene.brush_steps) > 3:
            if bpy.context.scene.tool_states.isFirstAlt == True:
                self.setInformation(3)
                bpy.context.scene.tool_states.isFirstAlt = False
            bpy.context.scene.tool_states.prevAlt = True
        #else:
        elif bpy.context.scene.tool_states.prevAlt:
            state = 0
            if event.shift:
                state = 1
            if event.ctrl:
                state = 2
            
            self.setInformation(state)
            bpy.context.scene.tool_states.isFirstAlt = True
            bpy.context.scene.tool_states.prevAlt = False
        
        
        
        
        elif event.ctrl and len(bpy.context.scene.brush_steps) > 2 and bpy.context.scene.tool_states.mousePress:
            if bpy.context.scene.tool_states.isFirstCtrl == True:
                self.setInformation(2)
                bpy.context.scene.tool_states.isFirstCtrl = False
            bpy.context.scene.tool_states.prevCtrl = True
        #else:
        elif bpy.context.scene.tool_states.prevCtrl:
            state = 0
            if event.shift:
                state = 1
            
            self.setInformation(state)
            bpy.context.scene.tool_states.isFirstCtrl = True
            bpy.context.scene.tool_states.prevCtrl = False
        
        
        
        
        elif event.shift and len(bpy.context.scene.brush_steps) > 1:
            if bpy.context.scene.tool_states.isFirstShift == True:
                self.setInformation(1)
                bpy.context.scene.tool_states.isFirstShift = False
            bpy.context.scene.tool_states.prevShift = True
        else:
            if bpy.context.scene.tool_states.prevShift:
                self.setInformation(0)
                bpy.context.scene.tool_states.isFirstShift = True
                bpy.context.scene.tool_states.prevShift = False
         
        
        
        
        if event.type == 'TIMER':
            if self.currentStep <= self.maxSteps:
                
                normal = self.currentStep / self.maxSteps
                y = self.evaluate(normal, self.type)
                
                
                ySize = self.Zfrom + ((self.Zto - self.Zfrom) * y)
                bpy.context.scene.tool_settings.unified_paint_settings.size = round(ySize)
                
                
                yStrength = self.Tfrom + ((self.Tto - self.Tfrom) * y)
                bpy.data.brushes["TexDraw"].strength = yStrength
                bpy.data.brushes["SculptDraw"].strength = yStrength
                
                
                print(self.currentStep)
                self.currentStep += 1
                
        
        return {'PASS_THROUGH'}
    
    
    
    
    
    
    
    def setInformation(self, id):
        
        self.maxSteps = bpy.context.scene.brush_steps[id].brush_time / (1 / self._calls_per_second)
        self.currentStep = 1
        self.type = bpy.context.scene.brush_steps[id].brush_easing
        
        
        
        self.Zfrom = bpy.context.scene.tool_settings.unified_paint_settings.size
        self.Zto = bpy.context.scene.brush_steps[id].brush_size
        
        self.Tfrom = bpy.data.brushes["TexDraw"].strength
        self.Tto = bpy.context.scene.brush_steps[id].brush_strength
    
    
    
    
    def evaluate(self, x, type):
        if type == 'Linear':
            return x
        elif type == 'InCubic':
            return x * x * x
        elif type == 'OutCubic':
            return 1 - ((1-x)**3)
        elif type == 'InExpo':
            return 2**((10 * x) - 10)
        elif type == 'OutExpo':
            return 1 - (2**(-10 * x))
        else:
            return 1
    
    
    
    
    def execute(self, context):
        isActive = context.scene.tool_states.isRunning
        
        if isActive == False:
            wm = context.window_manager
            self._timer = wm.event_timer_add(1/self._calls_per_second, window=context.window)
            wm.modal_handler_add(self)
            
            # Fatal Crash
            #self.Zcumulative = bpy.context.scene.brush_steps[0].brush_size
            #bpy.data.brushes["TexDraw"].strength = bpy.context.scene.brush_steps[0].brush_strength
            
            bpy.context.scene.tool_states.isRunning = True
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}
    
    
    
    
    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)








class BPS_OT_stop_read(bpy.types.Operator):
    bl_label = "Stop Tool"
    bl_idname = "bps.stop_read"
    
    def execute(self, context):
        isActive = context.scene.tool_states.isRunning
        
        if isActive == True:
            bpy.context.scene.tool_states.stopTool = True
            return {'FINISHED'}
        else:
            return {'FINISHED'}


 
classes = [BrushStepProperties, ToolStates, BPS_PT_main_panel, BPS_OT_set_default, BPS_OT_add_brush, BPS_OT_remove_brush, BPS_OT_start_read, BPS_OT_stop_read]
#addon_keymaps = []



def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.brush_steps = bpy.props.CollectionProperty(type = BrushStepProperties)
    bpy.types.Scene.tool_states = bpy.props.PointerProperty(type = ToolStates)
    
    """
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
        #km = wm.keyconfigs.addon.keymaps.new(name ='Image', space_type ='IMAGE_EDITOR')
        
        kmi = km.keymap_items.new("bps.start_read", type = 'LEFTMOUSE', value = 'PRESS', shift = True)
        addon_keymaps.append((km, kmi))
    """



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.brush_steps
    del bpy.types.Scene.tool_states
    
    """
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    """



if __name__ == "__main__":
    register()