bl_info = {
    "name" : "Add-on Profiler",
    "author" : "MrClock, bd3d (originally), rubenmesserschmidt (initial fixes)",
    "description" : "Monitor and capture add-on profiling data",
    "blender" : (2, 90, 0),
    "version" : (2, 0, 0),
    "wiki_url" : "",
    "tracker_url" : "https://github.com/MrClock8163/AddonProfiler/issues",
    "category" : "Development",
    "warning": ""
}


if "bpy" in locals():
    from importlib import reload
    if "props" in locals():
        reload(props)
    if "ui" in locals():
        reload(ui)
    if "utils" in locals():
        reload(utils)

import bpy

from . import props
from . import ui
from . import utils


modules = (
    props,
    ui
)


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in reversed(modules):
        mod.unregister()
