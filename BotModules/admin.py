from discord.ext import commands
#from BotModules.utils import checks
import inspect
from subprocess import run
# to expose to the eval command
import datetime
from collections import Counter

class Admin(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot:commands.Bot,config):
        self.bot = bot
        self.config = config

    @commands.command()
    @commands.is_owner()
    async def pull(self, ctx):
        await ctx.send('pulling dat shit')
        run(["git", "pull"])
        run(["sudo", "systemctl", "restart", "discordbot.service"])

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self,ctx, *, module : str):
        """Loads a module."""
        try:
            self.bot.add_cog(module)
        except Exception as e:
            await ctx.send('\N{PISTOL}')
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self,ctx, *, module : str):
        """Unloads a module."""
        try:
            self.bot.remove_cog(module)
        except Exception as e:
            await ctx.send('\N{PISTOL}')
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self,ctx, *, module : str):
        """Reloads a module."""
        try:
            cog = None
            for cog in self.bot.cogs:
                if cog.__name__ == module:
                    cog = cog
            
            self.bot.remove_cog(module)
            self.bot.add_cog(cog)
        except Exception as e:
            await ctx.send('\N{PISTOL}')
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def debug(self, ctx:commands.Context, *, code : str):
        """Evaluates code."""
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            #'server': ctx.message,
            'channel': ctx.channel,
            'author': ctx.author
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send(python.format(type(e).__name__ + ': ' + str(e)))
            return

        await ctx.send(python.format(result))