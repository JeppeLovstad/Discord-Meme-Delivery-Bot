import openai
from discord.ext import commands
from typing import Optional


class GPT3Bot(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config
        openai.api_key = config["token"]
    
    def get_ai_response(self, prompt: str) -> str:
        response = openai.Completion.create(
            model="text-davinci-002",
            max_tokens=64,
            prompt=prompt,
            temperature=0.6,
        )
        return response.choices[0].text

    @commands.command(aliases=["c"])
    async def chat(
        self,
        ctx,
        #Messages_to_go_back: Optional[int] = 1,
        #format: Optional[str] = "sass",
        *,
        prompt=""
    ):
        if prompt is None or prompt == "":
            await ctx.send("Input invalid try again,")
        else:
            await ctx.send(self.get_ai_response(prompt))

if __name__ == "__main__":

    from configparser import ConfigParser
    config = ConfigParser()
    config.read("config.ini")
    
    openai.api_key = config["GPT3BOT"]["token"]

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=generate_prompt("blablado"),
        temperature=0.6,
    )

    print(response.choices[0].text)
    
    
#     print(
#         "".join(
#             [
#                 c.upper() if idx % 2 == 0 else c.lower()
#                 for idx, c in enumerate(list("msg"))
#             ]
#         )
#     )
