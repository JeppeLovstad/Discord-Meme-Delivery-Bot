import configparser
from MemeBot import MemeBot
import os.path
from discord.ext import commands


def getConfigValues() -> dict:
    config = configparser.ConfigParser()
    if os.path.isfile("config.ini"):
        config.read("config.ini")
    else:
        config.read("template.ini")
        
    config = {s:dict(config.items(s)) for s in config.sections()}
    return config
    
if __name__ == "__main__":
    config = getConfigValues()
    command_prefix = config["DISCORD"]["command_prefix"]
    bot = commands.Bot(command_prefix=command_prefix)
    meme_bot = MemeBot(config,bot)