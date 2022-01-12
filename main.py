from memebot import MemeBot
from discord.ext import commands
import discord
import iniparser

    
if __name__ == "__main__":
    config = iniparser.getConfigAsDict()
    if config:
        intents = discord.Intents.all()
        command_prefix = config["DISCORD"]["bot_command_prefix"]
        bot = commands.Bot(command_prefix=command_prefix, intents=intents)
        meme_bot = MemeBot(config,bot)
    else:
        print("Config is missing, quitting...")