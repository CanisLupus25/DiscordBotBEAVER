import discord
import discord.ext.commands as commands
from better_profanity import profanity

from badwords18plus import badwords
from bot_token import TOKEN

profanity.load_censor_words(badwords)


class BEAVER(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_command(mute)

    async def on_message(self, message: discord.Message):
        if self.user != message.author:
            if profanity.contains_profanity(message.content):
                await message.delete()
                await message.channel.send(f'{message.author.mention}, здесь не принято ругаться!')
            else:
                await self.process_commands(message)


@commands.command('mute')
async def mute(ctx: commands.Context):
    await ctx.channel.send('OK!')


def main():
    intents = discord.Intents.default()
    intents.members = True
    intents.messages = True
    intents.message_content = True

    bot = BEAVER(command_prefix='!', intents=intents)
    bot.run(token=TOKEN)


if __name__ == '__main__':
    main()
