
import datetime, parse, os, gzip
from typing import Optional, Tuple, Union
import zipfile
from os.path import join as pathjoin, abspath
from dataclasses import dataclass
from mcdreforged.api.all import *
from online_timer.util import psi
import json

logger = psi.psi.logger
logger.setLevel('DEBUG')

@dataclass(unsafe_hash=True)
class JoinEntry:
    name: str
    timestamp: datetime.datetime
    type:str = 'join'

@dataclass(unsafe_hash=True)
class LeaveEntry:
    name: str
    timestamp: datetime.datetime
    type:str = 'leave'



class PlayTimeHistoryInfoManager(dict):
    def add_entry(self, entry: Union[JoinEntry, LeaveEntry]):
        if entry.name not in self.keys():
            self[entry.name] = set()
        
        self[entry.name].add(entry)
        
    def get_playtime(self, name) -> datetime.timedelta:
        playtime_record:list[Union[JoinEntry, LeaveEntry]] = list(self[name])
        playtime_record.sort(key=lambda x: x.timestamp)
        
        if isinstance(playtime_record[-1], JoinEntry):
            logger.info('%s\'s last entry is join, might be a player online', name)
            playtime_record = playtime_record[:-1]
        if name == 'FVortex':
            for l in playtime_record:
                logger.info(l)
        result = datetime.timedelta()
        last_is = None
        for entry in playtime_record:
            if last_is != entry.type:
                result = entry.timestamp - result
            last_is = entry.type
        return result
    
    def get_list(self, name):
        playtime_record:list = list(self[name])
        playtime_record.sort(key=lambda x: x.timestamp)
        return playtime_record
    
    def get_all(self) -> dict[str, Tuple[datetime.timedelta, Optional[datetime.datetime]]]:
        return {
            k: (
                self.get_playtime(k), 
                (self.get_list(k)[-1].timestamp if isinstance(self.get_list(k)[-1], JoinEntry) else None)
            ) for k, v in self.items()
        }
    
playtime_history = PlayTimeHistoryInfoManager()


def parse_vanilla_logfile(file, date, decode=True):
    
    line = file.readline()
    global playtime_history
    join = None
    logger.info("Loading history log file: %s", file.name)
    while line:
        if decode:
            line = line.decode('utf-8').strip()
        else:
            line = line.strip()
        join_result = parse.parse('[{time:tt}] [{}]: {name} joined the game', line)
        
        if join_result is not None:
            join = JoinEntry(join_result['name'], datetime.datetime.combine(date, join_result['time']))
            playtime_history.add_entry(join)
        
        leave_result = parse.parse('[{time:tt}] [{}]: {name} left the game', line)
        if leave_result is not None:
            leave = LeaveEntry(leave_result['name'], datetime.datetime.combine(date, leave_result['time']))
            playtime_history.add_entry(leave)
            
        server_stop = parse.parse('[{time:tt}] [{}]: Stopping server', line)
        if server_stop is not None:
            for k in playtime_history.keys():
                if playtime_history.get_list(k)[-1].type == 'join':
                    leave = LeaveEntry(k, datetime.datetime.combine(date, server_stop['time']))
                    playtime_history.add_entry(leave)
        
        line = file.readline()
    

def server_close_info():    #cannot parse anything now
    global playtime_history
    fmt = '[MCDR] [{dt:s}] [MainThread/INFO]: ' + psi.psi.tr('mcdr_server.on_server_stop.show_return_code', '{}')
    def parse_mcdr_logfile(logfile):
        global playtime_history
        line = logfile.readline()
        
        while line:
            line = line.decode('utf8').strip()
            
            stop_msg = parse.parse(fmt, line)

            if stop_msg:
                logger.info(f"MCDR stopped at {stop_msg['dt']}")
                for k in playtime_history.keys():
                    # if playtime_history.get_list(k)[-1].type == 'join':
                    dt = datetime.datetime.strptime(stop_msg['dt'], '%Y-%m-%D %H:%M:%S')
                    leave = LeaveEntry(k, dt)
                    playtime_history.add_entry(leave)
            line = logfile.readline()
        pass
    
    for zip_log in os.listdir('logs'):
        if zip_log.endswith('.zip'):
            with zipfile.ZipFile(pathjoin('logs', zip_log)) as file:
                with file.open('MCDR.log') as logfile:
                    logger.info(f'Loading history log file %s', file.filename)
                    line = logfile.readline()
                    
                    while line:
                        line = line.decode('utf8').strip()
                        stop_msg = parse.parse(fmt, line)

                        if stop_msg:
                            logger.info(f"MCDR stopped at {stop_msg['dt']}")
                            for k in playtime_history.keys():
                                # if playtime_history.get_list(k)[-1].type == 'join':
                                dt = datetime.datetime.strptime(stop_msg['dt'], '%Y-%m-%D %H:%M:%S')
                                leave = LeaveEntry(k, dt)
                                playtime_history.add_entry(leave)
                        line = logfile.readline()
                        pass
        
        pass
    with open(pathjoin('logs','MCDR.log'), 'rb') as logfile:
        logger.info(f'Loading history log file %s', logfile.name)
        parse_mcdr_logfile(logfile)

def load_history(server:PluginServerInterface):
    log_folder = pathjoin(abspath(server.get_mcdr_config().get('working_directory')), 'logs')
    for gzip_name in os.listdir(log_folder):
        if gzip_name.endswith('.log.gz'):
            path = os.path.join(log_folder, gzip_name)
            with gzip.open(path, 'r') as file:
                date = (os.path.splitext(os.path.split(file.name)[-1])[0]).split('-')[0:-1]
                date = [int(p) for p in date]
                date = datetime.date(*date)
                parse_vanilla_logfile(file, date)
                pass
            pass
        pass
    
    latest_log = pathjoin(log_folder, 'latest.log')
    with open(latest_log, 'r', encoding='utf8') as file:
        parse_vanilla_logfile(file, datetime.date.today(), decode=False)
        pass
    
    server_close_info()
    
    result = playtime_history.get_all()
    show = {k: str(v) for k , v in result.items()}
    logger.info(json.dumps(show, indent=2))
    return result

