from discord.ext import commands
import inspect
from subprocess import run
from utils.moduleloader import get_module_loader

# to expose to the eval command
import datetime
from collections import Counter
import utils.iniparser as iniparser


class Admin(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot: commands.Bot, config):
        self.bot = bot
        self.config = config
        self.module_loader = get_module_loader(bot)
        self.trusted_users = [
            408192607760416768,
            103111970751799296,
            101649687995486208,
        ]

    async def cog_check(self, ctx):
        user_authorized = (
            ctx.author.id in self.trusted_users or ctx.author.id == self.bot.owner_id
        )
        if not user_authorized:
            await ctx.send("User not verified")
        return ctx.author.id in self.trusted_users or ctx.author.id == self.bot.owner_id

    @commands.command(hidden=True)
    async def update_config(self, ctx, section="", item="", value=""):
        success, message = iniparser.setConfigValue(section, item, value)
        await ctx.send(message)

    @commands.command(hidden=True)
    async def log(self, ctx, limit: int = 10):
        git_output = run(
            ["journalctl", "--unit=discordbot.service", "-n", f"{limit}", "--no-pager"],
            capture_output=True,
        )
        git_output = git_output.stdout.decode("utf-8")
        await ctx.send(git_output)

    @commands.command(hidden=True)
    async def restart(self, ctx):
        run(["sudo", "systemctl", "restart", "discordbot.service"])
        await ctx.send("Service Restarted")

    @commands.command(hidden=True)
    async def pull(self, ctx):
        await ctx.send("pulling dat shit")
        git_output = run(["git", "pull"], capture_output=True)
        git_output = git_output.stdout.decode("utf-8")
        await ctx.send(git_output)

        if "Already up to date" in git_output:
            await ctx.send("No changes")
        else:
            # run(["sudo", "systemctl", "restart", "discordbot.service"])
            msg = await self.module_loader.sync_changed_files()
            await ctx.send(
                "Restarting modules, use restart if you changed a file not in BotModules \n"
                + msg
            )


    @commands.command(hidden=True)
    async def listcogs(self, ctx, *, module_name: str = ""):
        await ctx.send(self.module_loader.list_cogs(module_name))
        
        
    @commands.command(hidden=True)
    async def load(self, ctx, *, module_name: str):
        """Loads a module."""
        msg = ""
        try:
            msg = await self.module_loader.load_cog(module_name)
        except Exception as e:
            msg = "{}: {}".format(type(e).__name__, e)
        await ctx.send(msg)

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module_name: str):
        """Unloads a module."""
        msg = ""
        try:
            msg = self.module_loader.unload_cog(module_name)
        except Exception as e:
            msg = "{}: {}".format(type(e).__name__, e)
        await ctx.send(msg)

    @commands.command(name="reload", hidden=True)
    async def _reload(self, ctx, *, module_name: str):
        """Reloads a module."""
        msg = ""
        try:
            msg = await self.module_loader.reload_cog(module_name)
        except Exception as e:
            msg = "{}: {}".format(type(e).__name__, e)
        await ctx.send(msg)

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def debug(self, ctx, *, code: str):
        """Evaluates code."""
        code = code.strip("` ")
        python = "```py\n{}\n```"
        result = None

        env = {
            "bot": self.bot,
            "ctx": ctx,
            "message": ctx.message,
            #'server': ctx.message,
            "channel": ctx.channel,
            "author": ctx.author,
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send(python.format(type(e).__name__ + ": " + str(e)))
            return

        await ctx.send(python.format(result))
