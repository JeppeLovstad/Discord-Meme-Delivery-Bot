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

def generate_prompt(animal):
    return """Suggest three names for an animal that is a superhero.
            Animal: Cat
            Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
            Animal: Dog
            Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
            Animal: {}
            Names:""".format(animal.capitalize())
        
    

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
