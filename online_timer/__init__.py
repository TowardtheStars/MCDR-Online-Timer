
from online_timer.command import build_commands
from online_timer.db import load_data, OnlineTimeDB
from online_timer.config import config
from online_timer.util import psi

from mcdreforged.plugin.server_interface import PluginServerInterface
from mcdreforged.info_reactor.info import Info


"""默认插件加载事件"""
def on_load(server:PluginServerInterface, prev):
    build_commands(server)
    load_data(prev)
    
"""默认玩家加入事件"""
def on_player_joined(server:PluginServerInterface, player:str, info:Info):
    OnlineTimeDB().join(player)

"""默认玩家离线事件"""
def on_player_left(server:PluginServerInterface, player:str):
    OnlineTimeDB().leave(player)

"""默认服务器停止事件"""
def on_server_stop(server: PluginServerInterface, server_return_code: int):
    OnlineTimeDB().stop_server()
