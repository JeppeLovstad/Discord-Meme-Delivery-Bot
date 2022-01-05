from configparser import Error
import discord
import sys
from discord.ext import commands


class MemeBot:
    bot: commands.Bot
    command_prefix: str

    def __init__(self, config: dict, bot: commands.Bot):
        self.bot = bot
        enabledCogs = self.getCogInfoFromConfig(config)
        for cogInfo in enabledCogs:
            cog = self.instantiateCog(cogInfo)
            if cog:
                bot.add_cog(cog)
                
        self.registerDefaultFunctions(bot)
        bot.run(config["DISCORD"]["bot_token"])

    def getCogInfoFromConfig(self, config):
        cogs = []
        for module, enabled in config["BOT_MODULES"].items():
            if enabled == "True":

                main_classname = (
                    config["BOT_MODULES"][f"{module}_main"]
                    if f"{module}_main" in config["BOT_MODULES"]
                    else module.capitalize()
                )
                module_path = (
                    config["BOT_MODULES"][f"{module}_path"]
                    if f"{module}_path" in config["BOT_MODULES"]
                    else f"BotModules.{module}"
                )
                module_config = (
                        config[module.upper()] if module.upper() in config else {}
                    )
                cog={"module":module, "main_classname":main_classname, "module_path":module_path, "module_config":module_config}
                cogs.append(cog)
        return cogs

    def instantiateCog(self, cog):
        error_message = initiated_class = None
        module,main_classname,module_path,module_config = cog["module"],cog["main_classname"],cog["module_path"],cog["module_config"]
        try:
            #get class from folder
            imported_class = self.import_bot_module(module_path, main_classname)
            #check if module specific config exists

            try:
                #initate class
                initiated_class = imported_class(bot=self.bot, config=module_config)
                #update class name
                initiated_class.__cog_name__ = module.capitalize()
            except Error as e:
                print(f"Could not instantiate {module} skipping..., \n Error: {e.message}")
                error_message = e
        except ModuleNotFoundError as e:
            print(f"no module found in {module_path}")
            error_message = e
        except AttributeError as e:
            print(f"no class '{main_classname}', found in module {module_path}")
            error_message = e
            
        if not error_message:
            return initiated_class
        else:
            print(error_message)

    def import_bot_module(self, module, name):
        module = __import__(module, fromlist=[name])
        return getattr(module, name)

    def registerDefaultFunctions(self, bot: commands.Bot):
        bot.event(self.on_ready)
        bot.event(self.on_command_error)
        bot.add_listener(self.CustomCommandResponder, name="on_message")

    async def on_ready(self):
        self.bot.get_all_channels()
        print("We have logged in as {0.user}".format(self.bot))

    async def on_command_error(self, ctx, error):
        print(ctx, error)
        if isinstance(error, commands.CommandNotFound):
            if ctx.message.author.name == "Lasse Morgen":
                await ctx.message.reply(
                    "you fool. you absolute buffoon. you think you can challenge me in my own realm? you think you can rebel against my authority? you dare come into my house and upturn my dining chairs and spill coffee grounds in my Keurig? you thought you were safe in your chain mail armor behind that screen of yours. I will take these laminate wood floor boards and destroy you. I didn’t want war. but i didn’t start it."
                )
        else:
            raise error

    async def CustomCommandResponder(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if message.content == "":
            return
        # legacy code do not delete
        # if message.author.name == 'Lasse Morgen':
        #    await message.add_reaction("<:LasseWut:912650302589648907>")

