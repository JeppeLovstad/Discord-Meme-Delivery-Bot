from bs4 import BeautifulSoup
import requests
from random import choice
from discord.ext import commands


class Greentext(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config

        reddit_greentext_url = "https://www.reddit.com/r/greentext/"
        reddit_greentext_html = requests.get(reddit_greentext_url).content
        soup = BeautifulSoup(reddit_greentext_html, "html.parser")

        # reddit_greentext_url = 'https://the-greentext-guy.tumblr.com/archive'
        # reddit_greentext_html = requests.get(reddit_greentext_url).content
        # soup = BeautifulSoup(reddit_greentext_html, 'html.parser')

        img_tag = soup.find_all(attrs={"alt": "Post image"})
        print(img_tag[0])
        self.greentext_imgs = [img["src"] for img in img_tag]

    @commands.command()
    async def greentext(self, ctx):
        greentext_img = self.get_greentext()
        await ctx.send(greentext_img)

    def get_greentext(self):
        return choice(self.greentext_imgs)


if __name__ == "__main__":
    from configparser import ConfigParser

    config = ConfigParser()
    config.read("config.ini")
    bot = commands.Bot(command_prefix="!")
    m = Greentext(bot=bot, config=config["GREENTEXT"])
    # print(m.get_greentext())
