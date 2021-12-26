from bs4 import BeautifulSoup
import requests
import urllib.parse
import json
from discord.ext import commands

class CodInGame(commands.Cog):
    def __init__(self,config, bot: commands.Bot):
        self.bot = bot
        self.config = config
        
    @commands.command()
    async def gofish(self, ctx):
        url = self.CodInGame()
        await ctx.send(url)
        
    def CodInGame(self) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
            "Cookie": f"rememberMe={self.config['codingame_cookie']}"
            
            }
        search_url = f"https://www.codingame.com/services/ClashOfCode/createPrivateClash"
        data = '[4187058,["Python3"],["FASTEST","SHORTEST","REVERSE"]]'
        req = requests.post(search_url, headers=headers, data=data)

        print(req.text)
        command_dict = json.loads(req.text.replace("false", '"False"'))
        handle = command_dict['publicHandle']
        #https://www.codingame.com/clashofcode/clash/
        return f"https://www.codingame.com/clashofcode/clash/{handle}"


if __name__ == "__main__":
    pass
    #print(CodInGame())
