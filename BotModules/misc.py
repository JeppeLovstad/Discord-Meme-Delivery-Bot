from discord.ext import commands
from typing import Optional


class Misc(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config

    def sass_text(self, text_to_sass: str) -> str:
        return "".join(
            [
                c.upper() if idx % 2 == 0 else c.lower()
                for idx, c in enumerate(list(text_to_sass))
            ]
        )

    @commands.command(aliases=["s"])
    async def sass(
        self, ctx, Messages_to_go_back: Optional[int] = 1, *, text_to_sass=""
    ):

        if Messages_to_go_back is None or Messages_to_go_back < 1:
            Messages_to_go_back = 1

        if text_to_sass == "":
            text_to_sass = await ctx.channel.history(
                limit=1 + Messages_to_go_back
            ).flatten()
            sassed_text = self.sass_text(text_to_sass[-1].content)
            await ctx.send(sassed_text)
        else:
            sassed_text = self.sass_text(text_to_sass)
            webhook = await ctx.channel.create_webhook(name=ctx.author.name)
            await webhook.send(
                str(sassed_text),
                username=ctx.author.nick,
                avatar_url=ctx.author.avatar_url,
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
