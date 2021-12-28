from bs4 import BeautifulSoup
import requests
from random import choice
from discord.ext import commands

class greentext(commands.Cog):
    def __init__(self,config, bot: commands.Bot):
        self.bot = bot
        self.config = config
        
        reddit_greentext_url = 'https://www.reddit.com/r/greentext/'
        reddit_greentext_html = requests.get(reddit_greentext_url).content
        soup = BeautifulSoup(reddit_greentext_html, 'html.parser')

        #reddit_greentext_url = 'https://the-greentext-guy.tumblr.com/archive'
        #reddit_greentext_html = requests.get(reddit_greentext_url).content
        #soup = BeautifulSoup(reddit_greentext_html, 'html.parser')


        img_tag = soup.find_all('a', class_='_13svhQIUZqD9PVzFcLwOKT styled-outbound-link')
        print(img_tag)
        self.greentext_imgs = [img['href'] for img in img_tag]
    
        
    @commands.command()
    async def greentext(self, ctx):
        greentext_img = self.get_greentext()
        await ctx.send(greentext_img)
    
    def get_greentext(self):
        return choice(self.greentext_imgs)
    