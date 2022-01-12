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
        self.trusted_users = [408192607760416768,917706044942217256]
        
    def is_trusted_user(self, user_id):
        return user_id in self.trusted_users or user_id == self.bot.owner_id
        
    @commands.command(hidden=True)
    async def pull(self, ctx):
        if not self.is_trusted_user(ctx.author.id):
            await ctx.send('User not verified')
            return
        
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
        if not self.is_trusted_user(ctx.author.id):
            await ctx.send('User not verified')
            return
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
        if not self.is_trusted_user(ctx.author.id):
            await ctx.send('User not verified')
            return
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
        if not self.is_trusted_user(ctx.author.id):
            await ctx.send('User not verified')
            return
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
        if not self.is_trusted_user(ctx.author.id):
            await ctx.send('User not verified')
            return
        
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