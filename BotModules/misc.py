from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config

    @commands.command(aliases=["s"])
    async def sass(self, ctx, *text_to_sass):
        text_to_sass = " ".join(text_to_sass)
        sassed_text = "".join(
            [
                c.upper() if idx % 2 == 0 else c.lower()
                for idx, c in enumerate(list(text_to_sass))
            ]
        )
        # await ctx.send(sassed_text)

        webhook = await ctx.channel.create_webhook(name=ctx.member.name)
        await webhook.send(
            str(sassed_text), username=ctx.member.name, avatar_url=ctx.member.avatar_url
        )

        webhooks = await ctx.channel.webhooks()
        for webhook in webhooks:
            await webhook.delete()

        await ctx.message.delete()


# if __name__ == "__main__":

#     print(
#         "".join(
#             [
#                 c.upper() if idx % 2 == 0 else c.lower()
#                 for idx, c in enumerate(list("msg"))
#             ]
#         )
#     )
