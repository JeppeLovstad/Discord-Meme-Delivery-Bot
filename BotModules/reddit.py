from discord.ext import commands
from BotModules.GenericScrapers.RedditScrape import RedditScrape
from random import choice

class Reddit(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config
        self.subreddit_collection = {}
       
    @commands.command()
    async def reddit(self, ctx,arg1: str, arg2: int = 100, arg3: str = 'all'):
        reddit_img = ""
        if arg1.lower() == "random":
            reddit_img = choice(choice(self.subreddit_collection))
        else:
            reddit_img = self.get_reddit(arg1,arg2,arg3)
        await ctx.send(reddit_img)

    def get_reddit(self,arg1,arg2 = 100,arg3 = 'all'):
        if arg1 not in self.subreddit_collection:
            try:
                self.subreddit_collection[arg1] = RedditScrape(sub_reddit=arg1,load_amount=arg2,post_type=arg3)
            except Exception as e:
                if arg1 in self.subreddit_collection:
                    self.subreddit_collection.pop(arg1)
                return "Could not retrieve subreddit posts"
        post = self.subreddit_collection[arg1].get_random_post()
        return f"{post['title']} \n {post['url']}"

if __name__ == "__main__":
    from configparser import ConfigParser

    config = ConfigParser()
    config.read("config.ini")
    #bot = commands.Bot(command_prefix="!")
    #m = Reddit(bot=bot, config=config["REDDIT"])
    #m = Reddit(0,0)
    #print(m.get_reddit("programmerhumor"))
