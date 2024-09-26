import bpy


class PPROF_PG_logging_filteritem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name",
        description="Value to filter"
    )


class PPROF_PG_logging(bpy.types.PropertyGroup):
    logger_details: bpy.props.EnumProperty(
        name="Details",
        description="Call details to log",
        items=(
            ('NAME', "Function", "Name of the executed function"),
            ('FILE', "File", "Path to the source file"),
            ('DATE', "Date", "Date of the end of execution"),
            ('TIME', "Time", "Execution time")
        ),
        default={'NAME', 'FILE', 'TIME'},
        options={'ENUM_FLAG'}
    )
    filter_comp: bpy.props.BoolProperty(
        name="Filter Comprenehsions",
        description="Filter out iterable comprehension operations",
        default=True
    )
    filter_builtin: bpy.props.BoolProperty(
        name="Filter Built-in Operations",
        description="Filter calls to built-in python functions",
        default=True
    )
    filter_module: bpy.props.StringProperty(
        name="Filter Module",
        description="Only show items from this module",
        subtype='DIR_PATH',
        default=bpy.utils.resource_path('USER')
    )
    filter_file: bpy.props.CollectionProperty(
        name="Filter Files",
        description="File paths to filter",
        type=PPROF_PG_logging_filteritem
    )
    filter_file_index: bpy.props.IntProperty(name="Active Filter Index", description="Double click to change name and value")
    filter_file_type: bpy.props.EnumProperty(
        name="Filter Type",
        description="Filter with whitelisting or blacklisting",
        items=(
            ('WHITELIST', "Show Only", "Show items only if they match the filter"),
            ('BLACKLIST', "Hide", "Hide items if they match the filters")
        ),
        default='WHITELIST'
    )
    filter_func: bpy.props.CollectionProperty(
        name="Filter Functions",
        description="Function names to filter",
        type=PPROF_PG_logging_filteritem
    )
    filter_func_index: bpy.props.IntProperty(name="Active Filter Index", description="Double click to change name and value")
    filter_func_type: bpy.props.EnumProperty(
        name="Filter Type",
        description="Filter with whitelisting or blacklisting",
        items=(
            ('WHITELIST', "Show Only", "Show items only if they match the filter"),
            ('BLACKLIST', "Hide", "Hide items if they match the filters")
        ),
        default='WHITELIST'
    )


classes = (
    PPROF_PG_logging_filteritem,
    PPROF_PG_logging
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.WindowManager.pprof_logging = bpy.props.PointerProperty(type=PPROF_PG_logging)


def unregister():
    del bpy.types.WindowManager.pprof_logging

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
