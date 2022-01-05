from random import choice
from discord.ext import commands
if __name__ != "__main__": 
    from .GenericScrapers.RedditScrape import RedditScrape

class Greentext(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config

        self.scrape = RedditScrape(sub_reddit="greentext",load_amount=100)
        #self.image = 
        #reddit_greentext_url = "https://www.reddit.com/r/greentext/"
        #reddit_greentext_html = requests.get(reddit_greentext_url).content
        #soup = BeautifulSoup(reddit_greentext_html, "html.parser")
#
        ## reddit_greentext_url = 'https://the-greentext-guy.tumblr.com/archive'
        ## reddit_greentext_html = requests.get(reddit_greentext_url).content
        ## soup = BeautifulSoup(reddit_greentext_html, 'html.parser')
#
        #img_tag = soup.find_all(attrs={"alt": "Post image"})
        ## print(img_tag)
        #self.greentext_imgs = [img["src"] for img in img_tag]

    @commands.command()
    async def greentext(self, ctx):
        greentext_img = self.get_greentext()
        await ctx.send(greentext_img)

    def get_greentext(self):
        #return choice(self.greentext_imgs)       
        return self.scrape.get_random_post()

if __name__ == "__main__":
    from GenericScrapers.RedditScrape import RedditScrape
    from configparser import ConfigParser

    config = ConfigParser()
    config.read("config.ini")
    bot = commands.Bot(command_prefix="!")
    m = Greentext(bot=bot, config=config["GREENTEXT"])
    #m = Greentext(0,0)
    print(m.get_greentext())
