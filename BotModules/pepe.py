from bs4 import BeautifulSoup
import requests
from random import choice
from discord.ext import commands


class Pepe(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config

        pepe_url = "https://rare-pepe.com/"
        pepe_html = requests.get(pepe_url).content
        soup = BeautifulSoup(pepe_html, "html.parser")
        img_tag = soup.find_all("img", class_="attachment-thumbnail size-thumbnail")
        self.pepe_imgs = [img["src"] for img in img_tag]

    @commands.command()
    async def pepe(self, ctx):
        pepe_img = self.get_pepe()
        await ctx.send(pepe_img)

    def get_pepe(self):
        if self.pepe_imgs:
            pepe_url = choice(self.pepe_imgs)
            return pepe_url.replace('-150x150.','.')
        else:
            return "No Pepes :("

if __name__ == "__main__":
    from configparser import ConfigParser

    config = ConfigParser()
    config.read("config.ini")
    #bot = commands.Bot(command_prefix="!")
    #m = Pepe(bot=bot, config=config["PEPE"])
    #print(m.get_pepe())
