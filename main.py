import discord
import discord.ext.commands as commands
from profanity_police import checker
from check_swear import SwearingCheck
import random
import datetime

from GuildsSQL import GuildsDB, USER_ID, MESSAGES_COUNT, WARNS_COUNT, LAST_MUTE_AT
from keys import BOT_KEY
from minesweeper_generator import generate_field

RUS_CENSOR = SwearingCheck()
EUR_CENSOR = checker.Checker()
EUR_CENSOR_LANGS = ['en', 'fr', 'es', 'ko', 'pt', 'it', 'hi']
PUNTIONS = [0, 0, 5, 35, 70, 140]
NOTE_FOR_MEMBERS = '{}, здесь не принято ругаться! Вы получили {}-е предупреждение'
NOTE_FOR_MEMBERS2 = ['.\nНа 3-й раз вы будете наказаны и временно не сможете здесь общаться!', ' и были наказаны!']
NOTE_FOR_ADMIN = '{}, не ругайтесь! Я не могу наказать администратора, отнеситесь к этому с пониманием.'
ABOUT_COMS = 'Ошибка. Введите !help_beaver для справки о командах'


class BEAVER(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guilds_db = GuildsDB()

        @self.command('help_beaver')
        async def help(ctx: commands.Context):
            await ctx.channel.send(f'Команды бота БОБР:\n'
                                   f'!minesweeper <число мин от 5 до 50> - создаёт поле с минами размером 9*9\n'
                                   f'!mute <упоминание пользователя> <время наказания в минутах> - '
                                   f'блокирует пользователю общение на указанное время\n'
                                   f'!clear_warns <поминание пользователя> - обнуляет '
                                   f'счётчик предупреждений пользователя\n'
                                   f'!unmute <упоминание пользователя> - снимает с пользователя наказание')

        @self.command('mute')
        @commands.has_permissions(administrator=True)
        async def mute(ctx: commands.Context, user_mention, minutes: int):
            try:
                user = ctx.guild.get_member(int(user_mention[2:-1]))
                await user.timeout(datetime.timedelta(minutes=minutes), reason='Наказан админом сервера')
                await ctx.channel.send(f'Пользователь {user.mention} наказан.')
            except Exception:
                await ctx.channel.send(ABOUT_COMS)

        @self.command('minesweeper')
        async def minesweeper(ctx: commands.Context, mines='12'):
            try:
                mines = int(mines)
                if not 5 <= mines <= 50:
                    raise Exception
                generated = generate_field(9, mines)
                await ctx.channel.send(f"Сапёр создан!\n"
                                       f"Количество мин: {mines}\n"
                                       f"Создать ещё сапёр: {self.user.mention}\n"
                                       f"{generated}")
            except Exception:
                await ctx.send(ABOUT_COMS)

        @self.command('clear_warns')
        @commands.has_permissions(administrator=True)
        async def clear_warns(ctx: commands.Context, user_mention):
            try:
                user = ctx.guild.get_member(int(user_mention[2:-1]))
                self.guilds_db.set_value(user, WARNS_COUNT, 0)
                await ctx.channel.send(f'Предупреждения для {user.mention} обнулены.')
            except Exception:
                await ctx.channel.send(ABOUT_COMS)

        @self.command('unmute')
        @commands.has_permissions(administrator=True)
        async def unmute(ctx: commands.Context, user_mention):
            try:
                user = ctx.guild.get_member(int(user_mention[2:-1]))
                await user.timeout(datetime.timedelta(seconds=1), reason='Наказание снято')
                await ctx.channel.send(f'С {user.mention} снято наказание.')
            except Exception:
                await ctx.channel.send(ABOUT_COMS)

        @self.event
        async def on_message_edit(before: discord.Message, after: discord.Message):
            if before.content != after.content:
                if self.check_profanity(after.content):
                    await after.delete()
                    await after.channel.send(f'{after.author.mention}, здесь не принято ругаться!')

        @self.event
        async def on_ready():
            self.guilds_db.initialize_giulds(self.guilds)

    async def on_message(self, message: discord.Message):
        if self.user != message.author:
            if self.check_profanity(message.content):
                raw = self.guilds_db.get_value(message.author, LAST_MUTE_AT)
                if raw != 0:
                    last_mute_time = datetime.datetime(*self.decode_time(raw))
                else:
                    last_mute_time = datetime.datetime.now()
                if datetime.datetime.now() - last_mute_time >= datetime.timedelta(seconds=300):
                    self.guilds_db.set_value(message.author, WARNS_COUNT, 0)
                warn_count = self.guilds_db.get_value(message.author, WARNS_COUNT) + 1
                self.guilds_db.set_value(message.author, WARNS_COUNT, warn_count)
                await message.delete()
                if message.author.guild_permissions.administrator:
                    await message.channel.send(NOTE_FOR_ADMIN.format(message.author.mention))
                else:
                    msg = NOTE_FOR_MEMBERS.format(message.author.mention, warn_count)
                    if warn_count < 3:
                        msg += NOTE_FOR_MEMBERS2[0]
                    else:
                        msg += NOTE_FOR_MEMBERS2[1]
                        await message.author.timeout(
                            datetime.timedelta(seconds=PUNTIONS[min(warn_count - 1, len(PUNTIONS) - 1)]))
                    await message.channel.send(msg)
                self.guilds_db.set_value(message.author, LAST_MUTE_AT, datetime.datetime.now())
            else:
                self.guilds_db.set_value(message.author, MESSAGES_COUNT,
                                         self.guilds_db.get_value(message.author, MESSAGES_COUNT) + 1)
                await self.process_commands(message)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content != after.content:
            if self.check_profanity(after.content):
                await after.delete()

    def check_profanity(self, text):
        return (any([EUR_CENSOR.check_swear_word([{'text': text}], i) for i in EUR_CENSOR_LANGS])
                or RUS_CENSOR.predict(text)[0])

    def decode_time(self, strtime: str):
        return list(map(int, strtime.replace('-', ' ').replace(':', ' ').replace('.', ' ').split()))


def main():
    intents = discord.Intents.default()
    intents.members = True
    intents.messages = True
    intents.message_content = True
    intents.guild_messages = True

    bot = BEAVER(command_prefix='!', intents=intents)
    bot.run(token=BOT_KEY)


if __name__ == '__main__':
    main()
