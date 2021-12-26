#from MemeScraper.MemeScraper import MemeScraper
#import BotModules.aimeme
#from BotModules.CustomCommandHandler import CustomCommandHandler
#import json
#import re
import discord
#import BotModules.Googler
#import emoji
import sys
#import BotModules.CodInGame
#from BotModules import * 
from discord.ext import commands
import importlib
#from BotModules.Aimeme import AIMemeGenerator


class MemeBot:
    bot: commands.Bot 
    command_prefix:str 
    
    def __init__(self, config:dict, bot: commands.Bot ):
        self.command_prefix = config["DISCORD"]["command_prefix"]
        self.initiateBotModules(config, bot)
        self.registerDefaultFunctions(bot)
        self.bot = bot
        bot.run(config["DISCORD"]["bot_token"])
        
    def initiateBotModules(self, config, bot):
        for module,enabled in config["BOT_MODULES"].items():
            if enabled == "True":
                
                main_classname = config["BOT_MODULES"][f"{module}_main"] if f"{module}_main" in config["BOT_MODULES"] else module.capitalize()
                module_path = config["BOT_MODULES"][f"{module}_path"] if f"{module}_path" in config["BOT_MODULES"] else f"BotModules.{module}"
                try:
                    imported_class = self.import_bot_module(module_path,main_classname)
                    module_config = config[module.upper()] if module.upper() in config else {}
                    initiated_class = imported_class(bot=bot, config=module_config)
                    initiated_class.__cog_name__ = module.capitalize()
                except ModuleNotFoundError:
                    print(f"no module found in {module_path}")
                    continue
                except AttributeError:
                    print(f"no class '{main_classname}', found in module {module_path}")
                    continue
                
                bot.add_cog(initiated_class)
                
    def import_bot_module(self, module, name):
        module = __import__(module, fromlist=[name])
        return getattr(module, name)

    def registerDefaultFunctions(self, bot: commands.Bot):
        bot.event(self.on_ready)
        bot.event(self.on_command_error)
        bot.add_listener(self.CustomCommandResponder, name="on_message")

    async def on_ready(self):
        self.bot.get_all_channels()
        print('We have logged in as {0.user}'.format(self.bot))
        
    async def on_command_error(self, ctx, error):
        print(ctx,error)
        if isinstance(error, commands.CommandNotFound):
            if ctx.message.author.name == 'Lasse Morgen':
                await ctx.message.reply("you fool. you absolute buffoon. you think you can challenge me in my own realm? you think you can rebel against my authority? you dare come into my house and upturn my dining chairs and spill coffee grounds in my Keurig? you thought you were safe in your chain mail armor behind that screen of yours. I will take these laminate wood floor boards and destroy you. I didn’t want war. but i didn’t start it.")
        else:
            raise error

    async def CustomCommandResponder(self, message:discord.Message):
        if message.author == self.bot.user:
            return
        if message.content == "":
            return
        # legacy code do not delete
        # if message.author.name == 'Lasse Morgen':
        #    await message.add_reaction("<:LasseWut:912650302589648907>")


        if not message.content.startswith(self.command_prefix):
            pass
            # ccResponse = ccHandler.getResponseToMessage(message.content)
            # if ccResponse:
            #     await message.reply(ccResponse)

            # reactionResponse = reactionHandler.getResponseToMessage(
            #     message.content,
            #     single_response=True)

            # if reactionResponse:
            #     await message.add_reaction(reactionResponse)



    # @bot.command()
    # async def addreaction(ctx, arg1: str, arg2):
    #     response = arg2
    #     if response == "":
    #         await ctx.send("Cannot add empty reaction")
    #         return

    #     custom_emoji = re.match(r'<:\w*:\d*>', response)
    #     default_emoji = emoji.emoji_lis(
    #         arg2)[0]["emoji"] if emoji.emoji_count(arg2) == 1 else None
    #     #print(arg2, default_emoji)

    #     if not (custom_emoji or default_emoji):
    #         print(arg2, custom_emoji, default_emoji)
    #         await ctx.send("Non valid reaction emoji")
    #         return

    #     added = reactionHandler.addCommand(arg1, arg2)

    #     if added:
    #         await ctx.send("reaction added")
    #     else:
    #         await ctx.send("adding reaction failed")
  

    # @bot.command()
    # async def deletereaction(ctx, arg1: str):
    #     if arg1 == "":
    #         await ctx.send("Cannot delete empty reaction")
    #         return
    #     deleted = reactionHandler.deleteCommand(arg1)
    #     if deleted:
    #         await ctx.send("reaction deleted")
    #     else:
    #         await ctx.send("deleting reaction failed")





    # @bot.command()
    # async def customcommandslist(ctx):
    #     message_to_send = '\n'.join(
    #         [f"{v}" for v in ccHandler.command_dict.keys() if v != ""])
    #     await ctx.send(message_to_send)








