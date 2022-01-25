from discord.ext import commands
from utils.moduleloader import get_module_loader


class MemeBot:
    bot: commands.Bot
    command_prefix: str

    def __init__(self, config: dict, bot: commands.Bot):
        self.bot = bot
        self.moduleLoader = get_module_loader(bot)
        print(self.moduleLoader.reload_all_cogs())

        self.registerDefaultFunctions(bot)
        bot.run(config["DISCORD"]["bot_token"])

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

    async def CustomCommandResponder(self, message):
        if message.author == self.bot.user:
            return
        if message.content == "":
            return
        # legacy code do not delete
        # if message.author.name == 'Lasse Morgen':
        #    await message.add_reaction("<:LasseWut:912650302589648907>")
