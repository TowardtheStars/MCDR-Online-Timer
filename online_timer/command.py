from datetime import timedelta
import functools
from math import ceil

from mcdreforged.api.all import *

from online_timer.db import reload_history, OnlineTimeDB, PlayTimeInfo
from online_timer.util import format_timedelta, psi
from online_timer.config import config

builder = SimpleCommandBuilder()

root_node_list = set()

def command(command:str):
    global root_node_list
    root_node_list.add(command.split(' ')[0][2:])
    return builder.command(command)

def register_help_messages(server:PluginServerInterface):
    for name in root_node_list:
        server.register_help_message(
            '!!' + name, 
            psi.rtr(name + '.' + 'reg_help_msg', metadata=psi.metadata)
            )

def build_commands(server:PluginServerInterface):
    
    @command('!!oltime reload')
    def reload(source: CommandSource, context: CommandContext):
        if source.has_permission_higher_than(3):
            try:
                reload_history()
                source.reply(psi.rtr('oltime.reload.success'))
            except :
                source.reply(psi.rtr('oltime.reload.error.failed'))
        else:
            source.reply(psi.rtr('oltime.reload.error.no_permission'))

    @command('!!oltime')
    @command('!!oltime help')
    def show_help(source: CommandSource, context: CommandContext):
        msg = [psi.rtr('help_msg', metadata=psi.metadata)]
        if source.has_permission_higher_than(3):
            msg.append(psi.rtr('help_msg_op'))
        source.reply(RTextBase.join('\n', msg))

    builder.arg('player', lambda player: QuotableText(player).suggests(OnlineTimeDB().players))
    @command('!!olt')
    @command('!!olt <player>')
    def oltime_command(source: CommandSource, context: CommandContext):
        if context.get('player'):
            player = context.get('player')
            playinfo: PlayTimeInfo = OnlineTimeDB().online_time.get(player, None)
            if playinfo:
                source.reply(psi.rtr('olt.player.message', playerinfo = playinfo))
            else:
                source.reply(psi.rtr('olt.player.error', player))
        else:
            if source.is_player:
                playinfo: PlayTimeInfo = OnlineTimeDB().get(source.player)
                if playinfo:
                    source.reply(psi.rtr('olt.self.message', playinfo))
                else:
                    source.reply(psi.rtr('olt.self.error.player'))
            else:
                source.reply(psi.rtr('olt.self.error.console'))
        
    
    builder.arg('page', lambda page: Integer(page).at_min(1))
    @command('!!oltop')
    @command('!!oltop <page>')
    def olttop(source: CommandSource, context: CommandContext):
        cnt = config.get('max_oltop')
        page = context.get('page', 1)
        start = cnt * (page - 1)
        total_page = ceil(OnlineTimeDB().size / cnt)
        
        top_data = OnlineTimeDB().oltime_top()[start: cnt * page]
        msg = list()
        msg.append(psi.rtr('oltop.header'))
        
        # detect longest name for aligning
        d = [len(d.name) for d in top_data]
        d.append(0)
        longest_name_len = max(d)
        
        # generate top list
        for i, playtime_info in enumerate(top_data):
            msg.append(
                psi.rtr('oltop.rank', 
                    index = start + i + 1, 
                    name=playtime_info.name.ljust(longest_name_len),
                    time=format_timedelta(playtime_info.get_onlinetime(), force_day=True)
                    )
            )
        msg.append(psi.rtr('oltop.footage', page, total_page))
        source.reply(RTextBase.join('\n', msg))
    
    builder.register(server)
    register_help_messages(server)


