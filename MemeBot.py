import discord
import sys
from discord.ext import commands


class MemeBot:
    bot: commands.Bot
    command_prefix: str

    def __init__(self, config: dict, bot: commands.Bot):
        self.command_prefix = config["DISCORD"]["command_prefix"]
        self.initiateBotModules(config, bot)
        self.registerDefaultFunctions(bot)
        self.bot = bot
        bot.run(config["DISCORD"]["bot_token"])

    def initiateBotModules(self, config, bot):
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
                try:
                    #get class from folder
                    imported_class = self.import_bot_module(module_path, main_classname)
                    #check if module specific config exists
                    module_config = (
                        config[module.upper()] if module.upper() in config else {}
                    )
                    #iniate class
                    initiated_class = imported_class(bot=bot, config=module_config)
                    #update class name
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

        if not message.content.startswith(self.command_prefix):
            pass
