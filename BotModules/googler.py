from bs4 import BeautifulSoup
import requests
import urllib.parse
from discord.ext import commands
#import asyncio

class Googler(commands.Cog):
    def __init__(self,config, bot: commands.Bot):
        self.bot = bot
        self.config = config
    
    @commands.command()
    async def google(self, ctx, arg1: str, arg2: int = 1):
        message_to_send = '\n'.join([x for x in self.google_search(arg1, arg2)])
        await ctx.send(message_to_send)
    
    def google_search(self, search_string: str, num_results: int = 1) -> list[str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"}
        search_string = urllib.parse.quote(search_string)
        search_url = f"https://www.google.com/search?q={search_string}+-corona"
        print(search_url)
        req = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(req.text, "html.parser")
        t = soup.find_all("h3")

        result = []
        c = 0
        while len(result) < num_results:
            tag = t[c]
            if "adurl" in tag or tag.get_text() == "Annoncer":
                c += 1
                continue
            link = tag.parent.get("href")
            header = tag.get_text()
            result.append(header + " : " + "<"+link+">" if link else "error")
            c += 1

        return result

if __name__ == "__main__":
    pass
    #print(google("raspberry pi", 3))
