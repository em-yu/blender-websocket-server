import json
import websocket
import threading
try:
    import thread
except ImportError:
    import _thread as thread
import time


def on_message(ws, message):
    print("Received message from server:")
    print(message)

    # If there is a data value, move the default cube:
    try :
        data = json.loads(message)
        
        if bpy.data.objects["Cube"]:
            obj = bpy.data.objects["Cube"]
            if 'x' in data:
                obj.location.x = data['x']
            if 'y' in data:
                obj.location.y = data['y']
            if 'z' in data:
                obj.location.z = data['z']
    except Exception as e:
        print("cannot parse message as json:", e)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        ws.send('open ws connection')

    thread.start_new_thread(run, ())

# From https://gist.github.com/kotobukid/380bf0ac66e128731b95fbccfc583b2b
class TestThread(threading.Thread):
    def __init__(self, ctx):
        super(TestThread, self).__init__()
        self.daemon = True 

        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://localhost:5001",
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.on_open = on_open
        self.ws = ws

    def run(self):
        self.ws.run_forever()


bl_info = {
    "name": "Add-on Websocket test",
    "description": "",
    "author": "emilie",
    "version": (0, 0, 3),
    "blender": (3, 1, 2),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class WSSenderTest(bpy.types.Operator):
    bl_label = "Test Call Server"
    bl_idname = "wm.call_server_hello"

    def execute(self, context):
        print("Calling websocket")
        th.ws.send('hello from blender')

        return {'FINISHED'}
    

class WSSenderRandom(bpy.types.Operator):
    bl_label = "Move Cube Random"
    bl_idname = "wm.call_server_rand"

    def execute(self, context):
        print("Calling websocket (asking for random values to move the cube)")
        th.ws.send(json.dumps({'action': 0}))

        return {'FINISHED'}


# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_CustomPanel(Panel):
    bl_label = "Websocket Test"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Tools"
    bl_context = "objectmode"   


    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout


        layout.operator("wm.call_server_hello")
        layout.operator("wm.call_server_rand")
        layout.separator()

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------


def menu_fn(self, context):
    self.layout.separator()
    self.layout.operator(WSSenderTest.bl_idname)
    self.layout.operator(WSSenderRandom.bl_idname)


def register():
    th.start()

    bpy.utils.register_class(WSSenderTest)
    bpy.utils.register_class(WSSenderRandom)
    bpy.utils.register_class(OBJECT_PT_CustomPanel)
    bpy.types.VIEW3D_MT_object.append(menu_fn)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_fn)
    bpy.utils.unregister_class(WSSenderTest)
    bpy.utils.unregister_class(WSSenderRandom)
    bpy.utils.unregister_class(OBJECT_PT_CustomPanel)
    th.ws.close()
    print('websocket is closed')

ctx = {"lock": threading.Lock()}
th = TestThread(ctx)

if __name__ == "__main__":
    register()
