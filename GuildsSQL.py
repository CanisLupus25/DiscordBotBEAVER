import sqlite3
import typing
import datetime

import discord

CREATE_GUILD_TABLE = '''
CREATE TABLE IF NOT EXISTS {}
(User_ID INTEGER PRIMARY KEY UNIQUE,
Messages_count INTEGER DEFAULT 0,
Warns_count INTEGER DEFAULT 0,
Last_mute_at DATETIME DEFAULT 0)'''

ADD_USER = '''
INSERT OR IGNORE INTO {} VALUES ({}, {}, {}, {})'''

USER_ID = 'User_ID'
MESSAGES_COUNT = 'Messages_count'
WARNS_COUNT = 'Warns_count'
LAST_MUTE_AT = 'Last_mute_at'


class GuildsDB:
    def __init__(self):
        self.database = sqlite3.connect('data/guilds.db')

    def initialize_giulds(self, guids: typing.Sequence[discord.Guild]):
        for i in guids:
            self.database.execute(CREATE_GUILD_TABLE.format(f"guild_{i.id}"))
            self.add_members(i)
        self.database.commit()

    def add_members(self, guild: discord.Guild):
        for user in guild.members:
            self.database.execute(ADD_USER.format(f"guild_{guild.id}", user.id, 0, 0, 0))

    def set_value(self, user: discord.member.Member, variable: str, value):
        self.database.execute(
            'UPDATE {} SET {} = ? WHERE User_ID = {}'.format(f"guild_{user.guild.id}", variable, user.id),
            (value,))
        self.database.commit()

    def get_value(self, user: discord.member.Member, variable: str):
        return self.database.execute(
            'SELECT {} FROM {} WHERE User_ID = {}'.format(variable, f"guild_{user.guild.id}", user.id)).fetchone()[0]
