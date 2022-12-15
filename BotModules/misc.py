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

    def pascal_text(self, text_to_format: str) -> str:
        return "".join([t.capitalize() for t in text_to_format.split(" ")])

    def format_text(self, text_to_format: str, format: str = "sass") -> str:
        if format == "sass":
            return self.sass_text(text_to_format)
        if format == "pascal":
            return self.pascal_text(text_to_format)

        return text_to_format

    async def send_with_webhook(self, ctx, text):
        webhook = await ctx.channel.create_webhook(name=ctx.author.name)
        await webhook.send(
            str(text),
            username=ctx.author.nick,
            avatar_url=ctx.author.avatar_url,
        )

        webhooks = await ctx.channel.webhooks()
        for webhook in webhooks:
            await webhook.delete()

    @commands.command(aliases=["s"])
    async def sass(
        self,
        ctx,
        Messages_to_go_back: Optional[int] = 1,
        format: Optional[str] = "sass",
        *,
        text_to_sass=""
    ):

        if Messages_to_go_back is None or Messages_to_go_back < 1:
            Messages_to_go_back = 1

        if format is None:
            format = "sass"

        if text_to_sass == "":
            text_to_sass = [user async for user in ctx.channel.history(
                limit=1 + Messages_to_go_back
                            )] 
            sassed_text = self.format_text(text_to_sass[-1].content, format)
            await ctx.send(sassed_text)
        else:
            sassed_text = self.format_text(text_to_sass, format)
            await self.send_with_webhook(ctx, sassed_text)

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
