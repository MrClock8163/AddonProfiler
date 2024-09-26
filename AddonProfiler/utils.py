from os.path import abspath
import cProfile
import types
from sys import prefix
from datetime import datetime

import bpy

from . import __package__ as addon_name


addon_prefs = bpy.context.preferences.addons[addon_name].preferences


class Profiler:
    def __init__(self):
        self.cprof = cProfile.Profile()
        self.running = False
        self.callstack = {}
        self.settings = None
    
    def is_running(self):
        return self.running
    
    def enable(self):
        self.running = True
        self.cprof.enable()
    
    def disable(self):
        self.cprof.disable()
        self.running = False
    
    def logger_names(self, f_code):
        file = abspath(f_code.co_filename)
        name = f_code.co_name
        return file, name, "%s:%s" % (file, name)

    def logger_call(self, frame: types.FrameType, arg):
        file, name, key = self.logger_names(frame.f_code)
        
        if file.startswith(prefix) and self.settings.filter_builtin:
            return
    
        if "<listcomp>" in name and self.settings.filter_comp:
            return
        
        if self.settings.filter_module != "" and not file.startswith(self.settings.filter_module):
            return
        
        for item in self.settings.filter_file:
            if (item.name in file) == (self.settings.filter_file_type == 'BLACKLIST'):
                return
        
        for item in self.settings.filter_func:
            if (item.name == name) == (self.settings.filter_func_type == 'BLACKLIST'):
                return
        
        self.callstack[key] = datetime.now()

    def logger_return(self, frame, arg):
        file, name, key = self.logger_names(frame.f_code)

        start = self.callstack.pop(key, None)
        if start is None:
            return
        
        log = ""
        duration = (datetime.now() - start).total_seconds()
        if duration <= self.settings.filter_time_threshold and self.settings.filter_time_enable:
            return
        
        if 'NAME' in self.settings.logger_details:
            log += name
        
        if 'FILE' in self.settings.logger_details:
            log += " from %s" % file
        
        if 'DATE' in self.settings.logger_details:
            log += " at %s" % start

        if 'TIME' in self.settings.logger_details:
            log += " in %0.9fs" % duration

        print(log)

    def logger(self, frame, event, arg):
        if event == "call":
            self.logger_call(frame, arg)
        elif event == "return":
            self.logger_return(frame, arg)
