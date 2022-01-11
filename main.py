from memebot import MemeBot
from discord.ext import commands
import iniparser

    
if __name__ == "__main__":
    config = iniparser.getConfigAsDict()
    if config:
        command_prefix = config["DISCORD"]["bot_command_prefix"]
        bot = commands.Bot(command_prefix=command_prefix)
        meme_bot = MemeBot(config,bot)
    else:
        print("Config is missing, quitting...")