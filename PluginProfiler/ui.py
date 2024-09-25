import pstats
from io import StringIO
from sys import setprofile, getprofile

import bpy
from bpy_extras.io_utils import ExportHelper


from . import utils


prof = utils.Profiler()


class PPROF_OT_logging_filter_add(bpy.types.Operator):
    """Add new filter item"""

    bl_idname = "pprof.logging_filter_add"
    bl_label = "Add"
    bl_options = {'REGISTER', 'UNDO'}

    prop: bpy.props.StringProperty(
        name="Property Name",
        description="Filter collection propety to add item to"
    )

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        getattr(context.window_manager.pprof_logging, self.prop).add()

        return {'FINISHED'}


class PPROF_OT_logging_filter_remove(bpy.types.Operator):
    """Remove selected filter item"""

    bl_idname = "pprof.logging_filter_remove"
    bl_label = "Remove"
    bl_options = {'REGISTER', 'UNDO'}

    prop: bpy.props.StringProperty(
        name="Property Name",
        description="Filter collection propety to remove item from"
    )

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        props = context.window_manager.pprof_logging
        idx = getattr(props, "%s_index" % self.prop)
        filters = getattr(props, self.prop)
        if not (0 <= idx < len(filters)):
            return {'FINISHED'}

        filters.remove(idx)
        setattr(props, "%s_index" % self.prop, max(0, idx - 1))

        return {'FINISHED'}


class PPROF_OT_logging_start(bpy.types.Operator):
    """Start execution logging"""

    bl_idname = "pprof.logging_start"
    bl_label = "Start"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return getprofile() is None
    
    def execute(self, context):
        profiler = utils.Profiler()
        profiler.settings = context.window_manager.pprof_logging
        setprofile(profiler.logger)
        return {'FINISHED'}


class PPROF_OT_logging_stop(bpy.types.Operator):
    """Stop execution logging"""

    bl_idname = "pprof.logging_stop"
    bl_label = "Stop"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return getprofile() is not None and not prof.is_running()
    
    def execute(self, context):
        setprofile(None)
        return {'FINISHED'}


class PPROF_OT_profiling_start(bpy.types.Operator):
    """Start profiling"""

    bl_idname = "pprof.profiling_start"
    bl_label = "Start"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return not prof.is_running()
    
    def execute(self, context):
        prof.enable()
        return {'FINISHED'}


class PPROF_OT_profiling_pause(bpy.types.Operator):
    """Pause profiling"""

    bl_idname = "pprof.profiling_pause"
    bl_label = "Pause"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return prof.is_running()
    
    def execute(self, context):
        prof.disable()
        return {'FINISHED'}


class PPROF_OT_profiling_save(bpy.types.Operator, ExportHelper):
    """Save collected profiling data"""

    bl_idname = "pprof.profiling_save"
    bl_label = "Save"
    bl_options = {'REGISTER'}
    filename_ext = ".prof"

    filter_glob: bpy.props.StringProperty(
        default="*.prof",
        options={'HIDDEN'}
    )

    @classmethod
    def poll(cls, context):
        return not prof.is_running() and prof.cprof.getstats()

    def execute(self, context):
        stats = pstats.Stats(prof.cprof).sort_stats(pstats.SortKey.CUMULATIVE)
        stats.dump_stats(self.filepath)
        return {'FINISHED'}


class PPROF_OT_profiling_print(bpy.types.Operator):
    """Print collected profiling data to the system console"""

    bl_idname = "pprof.profiling_print"
    bl_label = "Print"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return not prof.is_running() and prof.cprof.getstats()
    
    def execute(self, context):
        stream = StringIO()
        stats = pstats.Stats(prof.cprof, stream=stream).sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats()
        print(stream.getvalue())
        return {'FINISHED'}


class PPROF_OT_profiling_clear(bpy.types.Operator):
    """Clear collected profiling data"""

    bl_idname = "pprof.profiling_clear"
    bl_label = "Clear"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return not prof.is_running() and prof.cprof.getstats()
    
    def execute(self, context):
        prof.cprof.clear()
        return {'FINISHED'}


class PPROF_UL_filter(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon='FILTER') 


class PPROF_PT_logging(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Plugin Profiler"
    bl_label = "Call Logging"

    @classmethod
    def poll(cls, context):
        return True
    
    def draw_header(self, context):
        pass

    def draw(self, context):
        layout = self.layout

        layout.operator(PPROF_OT_logging_start.bl_idname, icon='PLAY')
        layout.operator(PPROF_OT_logging_stop.bl_idname, icon='PAUSE')


class PPROF_PT_logging_settings(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Plugin Profiler"
    bl_label = "Settings"
    bl_parent_id = "PPROF_PT_logging"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True
    
    def draw_header(self, context):
        pass

    def draw(self, context):
        layout = self.layout

        props = context.window_manager.pprof_logging
        row = layout.row(align=True)
        row.prop(props, "logger_details", expand=True)
        layout.prop(props, "filter_module")

        layout.label(text="Exclude:")
        row_filters = layout.row(align=True)
        row_filters.prop(props, "filter_comp", text="Comprehension", toggle=True)
        row_filters.prop(props, "filter_builtin", text="Built-in", toggle=True)

        layout.label(text="Filter Files:")
        row_file = layout.row()
        col_list_file = row_file.column()
        col_list_file.template_list("PPROF_UL_filter", "PPROF_filter_file", props, "filter_file", props, "filter_file_index")
        col_list_file.prop(props, "filter_file_exclude", text="Exclude", toggle=True)
        col_op_file = row_file.column(align=True)
        op_add_file = col_op_file.operator("pprof.logging_filter_add", text="", icon='ADD')
        op_add_file.prop = "filter_file"
        op_rem_file = col_op_file.operator("pprof.logging_filter_remove", text="", icon='REMOVE')
        op_rem_file.prop = "filter_file"

        layout.label(text="Filter Functions:")
        row_func = layout.row()
        col_list_func = row_func.column()
        col_list_func.template_list("PPROF_UL_filter", "PPROF_filter_func", props, "filter_func", props, "filter_func_index")
        col_list_func.prop(props, "filter_func_exclude", text="Exclude", toggle=True)
        col_op_func = row_func.column(align=True)
        op_add_func = col_op_func.operator("pprof.logging_filter_add", text="", icon='ADD')
        op_add_func.prop = "filter_func"
        op_rem_func = col_op_func.operator("pprof.logging_filter_remove", text="", icon='REMOVE')
        op_rem_func.prop = "filter_func"


class PPROF_PT_profiler(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Plugin Profiler"
    bl_label = "Profiling"

    @classmethod
    def poll(cls, context):
        return True
    
    def draw_header(self, context):
        pass

    def draw(self, context):
        layout = self.layout

        name = "Resume" if not prof.is_running() and prof.cprof.getstats() else "Start"
        layout.operator(PPROF_OT_profiling_start.bl_idname, text=name, icon='PLAY')
        layout.operator(PPROF_OT_profiling_pause.bl_idname, icon='PAUSE')
        layout.operator(PPROF_OT_profiling_save.bl_idname, icon='FILE_TICK')
        layout.operator(PPROF_OT_profiling_print.bl_idname, icon='CONSOLE')
        layout.operator(PPROF_OT_profiling_clear.bl_idname, icon='TRASH')


classes = (
    PPROF_OT_logging_filter_add,
    PPROF_OT_logging_filter_remove,
    PPROF_OT_logging_start,
    PPROF_OT_logging_stop,
    PPROF_OT_profiling_start,
    PPROF_OT_profiling_pause,
    PPROF_OT_profiling_save,
    PPROF_OT_profiling_print,
    PPROF_OT_profiling_clear,
    PPROF_UL_filter,
    PPROF_PT_logging,
    PPROF_PT_logging_settings,
    PPROF_PT_profiler
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
