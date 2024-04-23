import discord
import discord.ext.commands as commands
from better_profanity import profanity

from keys import BOT_KEY
from minesweeper_generator import generate_field

profanity.load_censor_words()
profanity.add_censor_words(open('swear_words18+.txt', encoding='UTF-8').read().split())


class BEAVER(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        @self.command('mute')
        async def mute(ctx: commands.Context):
            await ctx.channel.send('OK!')

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
                await ctx.send('Неверно введена команда. Команда: !minesweeper <число мин от 5 до 50>')

    async def on_message(self, message: discord.Message):
        if self.user != message.author:
            if profanity.contains_profanity(message.content):
                await message.delete()
                await message.channel.send(f'{message.author.mention}, здесь не принято ругаться!')
            else:

                await self.process_commands(message)


def main():
    intents = discord.Intents.default()
    intents.members = True
    intents.messages = True
    intents.message_content = True

    bot = BEAVER(command_prefix='!', intents=intents)
    bot.run(token=BOT_KEY)


if __name__ == '__main__':
    main()
