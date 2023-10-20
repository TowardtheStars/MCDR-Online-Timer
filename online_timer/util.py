
from datetime import timedelta
from mcdreforged.api.all import *
from typing import *
from os.path import join as pathjoin


class PluginRef:
    psi = ServerInterface.get_instance().as_plugin_server_interface()
    
    def __init__(self) -> None:
        # self.new_thread.__doc__ = new_thread.__doc__
        pass
        
    def rtr(self, translation_key:str, *args, **kwargs):
        if not translation_key.startswith(self.metadata.id):
            translation_key = self.metadata.id + '.' + translation_key
        return self.psi.rtr(translation_key, *args, **kwargs)
    
    def tr(self, translation_key:str, *args, **kwargs):
        if not translation_key.startswith(self.metadata.id):
            translation_key = self.metadata.id + '.' + translation_key
        return self.psi.tr(translation_key, *args, **kwargs)
        
    @property
    def metadata(self):
        return self.psi.get_self_metadata()
    
    def new_thread(self, name: str):
        return new_thread(self.metadata.name + '_' + name)
    
    def data_file(self, *path:str):
        return pathjoin(self.psi.get_data_folder(), *path)
    
    

psi = PluginRef()

def format_timedelta(td:timedelta, force_day:bool=False) -> RTextBase:
    mm, ss = divmod(td.seconds, 60)
    hh, mm = divmod(mm, 60)
    
    def consider_plural(key, value):
        return psi.rtr(key + ('.text' if value == 0 or value == 1 else '.plural'), value)
    
    s:Union[RTextBase, list] = [consider_plural('time_format.day', td.days)] if td.days > 0 or force_day else list()
    s.append(consider_plural('time_format.hour', hh))
    s.append(consider_plural('time_format.minute', mm))
    s.append(consider_plural('time_format.second', mm))
    
    return RTextBase.join(' ', s)
