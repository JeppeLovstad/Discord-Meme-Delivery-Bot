import configparser
from MemeBot import MemeBot
import os.path
from os  import walk
from discord.ext import commands

def getConfigValues() -> dict:
    config = configparser.ConfigParser()
    
    (_, _, filenames) = next(walk("."))
    
    # grabs first .ini file in root that has a token and is not template.ini
    for filename in filenames:
        if filename.endswith(".ini") and filename != "template.ini":
            config.read(filename)
            if not validateConfig(config):
                config.clear()
                continue
            break
        
    if len(config) == 1 and os.path.isfile("template.ini"):
        config.clear()
        config.read("template.ini")
        if not validateConfig(config):
            config.clear()

    config = {s:dict(config.items(s)) for s in config.sections()}
    return config
    
def validateConfig(config:configparser.ConfigParser):
    if config["DISCORD"]["bot_token"] == "<BOT_TOKEN>":
        print("Bot token is not set")
        return False
    if not config.has_section("DISCORD"):
        print("DISCORD Section missing in config file")
        return False
    if  not config.has_option("DISCORD","bot_token"):
        print("bot_token value missing in config file")
        return False
    if  not config.has_option("DISCORD","bot_command_prefix"):
        print("bot_command_prefix value missing in config file, using default of !")
        config.set(section="DISCORD", option="bot_command_prefix", value= "!")
        #return False
    return True
    
if __name__ == "__main__":
    config = getConfigValues()
    if config:
        command_prefix = config["DISCORD"]["bot_command_prefix"]
        bot = commands.Bot(command_prefix=command_prefix)
        meme_bot = MemeBot(config,bot)
    else:
        print("Config is missing, quitting...")