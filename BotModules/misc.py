from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config

    @commands.command()
    async def sass(self, ctx):
        sassed_text = "".join(
            [
                c.upper() if idx % 2 == 0 else c.lower()
                for idx, c in enumerate(list(ctx.message))
            ]
        )
        await ctx.send(sassed_text)


# if __name__ == "__main__":

#     print(
#         "".join(
#             [
#                 c.upper() if idx % 2 == 0 else c.lower()
#                 for idx, c in enumerate(list("msg"))
#             ]
#         )
#     )
