from random import choice
from discord.ext import commands
if __name__ != "__main__": 
    from .GenericScrapers.RedditScrape import RedditScrape

class Reddit(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config

       

    @commands.command()
    async def reddit(self, ctx,arg1: str, arg2: int = 25):
        reddit_img = self.get_reddit(arg1,arg2)
        await ctx.send(reddit_img)

    def get_reddit(self,arg1,arg2 = 25):
        #return choice(self.reddit_imgs)       
        self.scrape = RedditScrape(sub_reddit=arg1,load_amount=arg2)
        return self.scrape.get_random_post()

if __name__ == "__main__":
    from GenericScrapers.RedditScrape import RedditScrape
    from configparser import ConfigParser

    config = ConfigParser()
    config.read("config.ini")
    bot = commands.Bot(command_prefix="!")
    m = reddit(bot=bot, config=config["REDDIT"])
    #m = Reddit(0,0)
    print(m.get_reddit("programmerhumor"))
