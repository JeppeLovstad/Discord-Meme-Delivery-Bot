from random import choice
from discord.ext import commands
if __name__ != "__main__": 
    from .GenericScrapers.RedditScrape import RedditScrape

class Reddit(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config
        self.subreddit_collection = {}
       

    @commands.command()
    async def reddit(self, ctx,arg1: str, arg2: int = 100, arg3: str = 'all'):
        reddit_img = self.get_reddit(arg1,arg2,arg3)
        await ctx.send(reddit_img)

    def get_reddit(self,arg1,arg2 = 100,arg3 = 'all'):
        #return choice(self.reddit_imgs)       
        if arg1 not in self.subreddit_collection:
            self.subreddit_collection[arg1] = RedditScrape(sub_reddit=arg1,load_amount=arg2,post_type=arg3)
        #self.scrape = RedditScrape(sub_reddit=arg1,load_amount=arg2,)
        post = self.subreddit_collection[arg1].get_random_post()
        return f"{post['title']} \n {post['url']}"
      #  print(self.scrape.get_random_post()[0])
      #  return self.scrape.get_random_post()

if __name__ == "__main__":
    from GenericScrapers.RedditScrape import RedditScrape
    from configparser import ConfigParser

    config = ConfigParser()
    config.read("config.ini")
    bot = commands.Bot(command_prefix="!")
    m = reddit(bot=bot, config=config["REDDIT"])
    #m = Reddit(0,0)
    print(m.get_reddit("programmerhumor"))
