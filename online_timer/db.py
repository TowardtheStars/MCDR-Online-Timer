
from copy import deepcopy
from dataclasses import dataclass, field
import json
import os
from os.path import join as pathjoin, abspath
from typing import *
from typing_extensions import Self

from datetime import datetime, timedelta

from mcdreforged.api.all import *
from online_timer.util import format_timedelta, psi
from online_timer.history import load_history

logger = psi.psi.logger
logger.setLevel('DEBUG')

@dataclass()
class PlayTimeInfo:
    name:str
    played_time:timedelta = field(default_factory=timedelta)
    status: Optional[datetime] = None
    
    @property
    def is_online(self):
        return self.status is not None
    
    def get_onlinetime(self):
        result = self.played_time
        if self.is_online:
            result += datetime.now() - self.status
        return result
    
    def online(self, time: datetime):
        self.assert_status(should_already_online=False)
        self.status = time
        
    def offline(self, time: datetime):
        self.assert_status(should_already_online=True)
        self.played_time += time - self.status
        self.status = None
        
    @property
    def formatted_onlinetime(self):
        return format_timedelta(self.get_onlinetime())
        
    def assert_status(self, should_already_online:bool):
        if self.is_online is not should_already_online:
            if should_already_online:
                
                pass
            else:
                pass
        pass
    
    @staticmethod
    def copy_from(obj:Union['PlayTimeInfo', Any]) -> 'PlayTimeInfo':
        return PlayTimeInfo(
            name = obj.name,
            played_time = obj.played_time,
            status = obj.status
        )
    
            

class OnlineTimeDB:
    DB_FILE = psi.data_file('data.json')
    _instance = None
    
    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        if not hasattr(self, 'online_time'):
            logger.info(psi.tr('online_timer.logger.OnlineTimeDB.init'))
            self.online_time: dict[str, PlayTimeInfo] = dict()
    
    def get(self, name) -> timedelta:
        logger.info(psi.tr('online_timer.logger.OnlineTimeDB.get.online_time'), name)
        # logger.info(json.dumps({k:str(v) for k, v in self.online_time.items()}, indent=2))
        info = self.online_time.get(name)
        
        return info.get_onlinetime() if info else None
    
    @psi.new_thread('Reload History')
    def reload_history(self):
        logger.info(psi.tr('online_timer.logger.OnlineTimeDB.history.reload.start'))
        history = load_history(psi.psi)
        for k, v in history.items():
            info = self.online_time.get(k, PlayTimeInfo(name=k))
            info.played_time = v[0]
            info.status = v[1]
            self.online_time[k] = info
        logger.info(psi.tr('online_timer.logger.OnlineTimeDB.history.reload.complete'))
        logger.debug(json.dumps({k:str(v) for k, v in self.online_time.items()}, indent=2))
        self.save_data()
            
    
    def serialize(self) -> dict:
        return {
            v.name: v.played_time.total_seconds()
            for v in self.online_time.values()
        }
    
    @classmethod
    def deserialize(cls: type[Self], data: dict, **kwargs) -> Self:
        logger.info('Deserializing...')
        r = OnlineTimeDB()
        r.online_time = {
            k: PlayTimeInfo(k, timedelta(seconds=v))
            for k, v in data.items()
        }
        return r
    
    def join(self, name):
        info = self.online_time.get(name, PlayTimeInfo(name))
        info.online(datetime.now())
        self.online_time[name] = info
        
    def leave(self, name):
        info = self.online_time.get(name, PlayTimeInfo(name))
        info.offline(datetime.now())
        self.online_time[name] = info
    
    # @psi.new_thread('SaveData')
    def stop_server(self):
        for k, v in self.online_time.items():
            v.offline(datetime.now())
            
        self.save_data()
    
    
    def save_data(self):
        with open(OnlineTimeDB.DB_FILE, 'w') as file:
            json.dump(self.serialize(), file, indent=2)
            
    def oltime_top(self):
        r = list(self.online_time.values())
        logger.info(r)
        r.sort(key=lambda play_time_info: play_time_info.get_onlinetime(), reverse=True)
        return r
    
    def players(self):
        return self.online_time.keys()
    
    @property
    def size(self):
        return len(self.online_time.keys())
    
    @staticmethod
    def copy_from(obj: Union['OnlineTimeDB', Any]) -> 'OnlineTimeDB':
        db = OnlineTimeDB()
        for k, v in obj.online_time.items():
            db.online_time[k] = PlayTimeInfo.copy_from(v)
        return db
            

# @psi.new_thread('LoadData')
def load_data(old):
    if old:
        logger.info(psi.tr('online_timer.logger.load_data.reload_data'))
        # logger.info(json.dumps({k:str(v) for k, v in old.OnlineTimeDB().online_time.items()}, indent=2))
        OnlineTimeDB.copy_from(old.OnlineTimeDB())
    else:
        if os.path.exists(OnlineTimeDB.DB_FILE):
            logger.info(psi.tr('online_timer.logger.load_data.load_json.load'))
            with open(psi.data_file('data.json'), 'r') as file:
                data = json.load(file)
            OnlineTimeDB.deserialize(data)
        else:
            logger.info(psi.tr('online_timer.logger.load_data.load_json.no_json'))
            dbs = OnlineTimeDB()
        

    logger.info(json.dumps({k:str(v) for k, v in OnlineTimeDB().online_time.items()}, indent=2))


def reload_history():
    OnlineTimeDB().reload_history()
    