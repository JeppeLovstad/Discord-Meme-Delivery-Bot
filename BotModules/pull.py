import os
from discord.ext import commands

class Pepe(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config

    @commands.command()
    async def pull(self, ctx):
        os.system("git pull")
        os.system("sudo systemctl restart discordbot.service)")