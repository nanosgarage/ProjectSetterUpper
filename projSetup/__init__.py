import os
import bpy

class PROJECTSETUP_OT_setup_project(bpy.types.Operator):
    bl_idname = "projectsetup.setup_project"
    bl_label = "Setup Project"
    directory: bpy.props.StringProperty(name = "Setup Project In...", subtype="DIR_PATH")
    project_name: bpy.props.StringProperty(name="Project Name", default="NewProject")
    make_output_folder: bpy.props.BoolProperty(name= "Make output directory?", default=True)
    output_folder_name: bpy.props.StringProperty(name = "Output Folder Name", default= "output")
    make_textures_folder: bpy.props.BoolProperty(name = "Make textures directory?", default=True)
    camera_resolution: bpy.props.IntVectorProperty(name = "Camera Resolution", min=4, size=2, default=(1920, 1080))
    framerate: bpy.props.IntProperty(name = "Framerate", min=1, default=24)

    def try_make_folder(self, root_path, new_folder_name):
        try:
            new_folder_path = os.path.join(root_path, new_folder_name)
            os.makedirs(new_folder_path, exist_ok=False)
        except FileExistsError as e:
            self.report({'ERROR'}, f"Folder already exists: {e}")
            return None
        except PermissionError as e:
            self.report({'ERROR'}, f"Not allowed to create folder due to permissions: {e}")
            return None
        except Exception as e:
            self.report({'ERROR'}, f"Unknown error occured: {e}")
            return None
        
        return new_folder_path


    def execute(self, context):
        if not self.directory or not self.project_name:
            self.report({'ERROR'}, "Please choose directory and/or a project name.")
            return {'CANCELLED'}

        bpy.path.clean_name(self.project_name)

        root_folder = bpy.path.abspath(self.directory)
        project_folder = self.try_make_folder(root_folder, self.project_name)
        if project_folder is None:
            return {'CANCELLED'}
        
        if self.make_output_folder:
            output_folder = self.try_make_folder(project_folder, self.output_folder_name)
            if output_folder is None:
                return {'CANCELLED'}
            context.scene.render.filepath = bpy.path.relpath(os.path.join(output_folder, ""))

        if self.make_textures_folder:
            textures_folder = self.try_make_folder(project_folder, "Textures")
            if textures_folder is None:
                return {'CANCELLED'}

        context.scene.render.resolution_x = self.camera_resolution[0]
        context.scene.render.resolution_y = self.camera_resolution[1]

        context.scene.render.fps = self.framerate
        context.scene.render.fps_base = 1.0

        blend_path = os.path.join(project_folder, f"{self.project_name}.blend")
        try:
            bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        except RuntimeError as e:
            self.report({'ERROR'}, f"Couldn't save file: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, title="Setup Blender Project Directory", confirm_text="Setup Project")


def menu_func(self, context):
    self.layout.operator("projectsetup.setup_project")

def register():
    bpy.utils.register_class(PROJECTSETUP_OT_setup_project)
    bpy.types.TOPBAR_MT_file.append(menu_func)

def unregister():
    bpy.types.TOPBAR_MT_file.remove(menu_func)
    bpy.utils.unregister_class(PROJECTSETUP_OT_setup_project)