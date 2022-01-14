from discord.ext import commands
#from BotModules.utils import checks
import inspect
from subprocess import run
# to expose to the eval command
import datetime
from collections import Counter
import iniparser

class Admin(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot:commands.Bot,config):
        self.bot = bot
        self.config = config
        self.trusted_users = []
        
    
    async def check_cog(self, ctx):
        user_authorized = ctx.author.id in self.trusted_users or ctx.author.id == self.bot.owner_id
        if not user_authorized:
            await ctx.send('User not verified')
        return ctx.author.id in self.trusted_users or ctx.author.id == self.bot.owner_id

    @commands.command(hidden=True)
    async def update_config(self,ctx, section = "", item = "", value=""):
        iniparser.setConfigValue(section,item,value)
        
    @commands.command(hidden=True)
    async def log(self, ctx, limit:int=10):
        git_output = run(["journalctl", "--unit=discordbot.service", "-n",  f"{limit}", "--no-pager"], capture_output=True)
        git_output = git_output.stdout.decode("utf-8")
        await ctx.send(git_output)
        
    @commands.command(hidden=True)
    async def restart(self, ctx):
        run(["sudo", "systemctl", "restart", "discordbot.service"])
        await ctx.send('Service Restarted')

    @commands.command(hidden=True)
    async def pull(self, ctx):
        await ctx.send('pulling dat shit')
        git_output = run(["git", "pull"], capture_output=True)
        git_output = git_output.stdout.decode("utf-8")
        await ctx.send(git_output)
        
        if "Already up to date" in git_output:
            await ctx.send('No changes')
        else:
            run(["sudo", "systemctl", "restart", "discordbot.service"])
            await ctx.send('Service Restarted')
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
    async def debug(self, ctx, *, code : str):
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
