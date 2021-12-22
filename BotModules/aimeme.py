from bs4 import BeautifulSoup
import requests
import json
import random
from discord.ext import commands

class AIMemeGenerator(commands.Cog):

    def __init__(self,config, bot: commands.Bot):
        self.bot = bot
        self.config = config
        self.meme_dict = self.get_available_memes()
        self.error_memes_dict = {}
    
    
    @commands.command()
    async def memelist(self, ctx):
        message_to_send = 'Meme name: Id\n'
        memes = self.listAvailableMemes()
        print(memes)
        message_to_send += '\n'.join([f"{k} : {v}" for k,
                                    v in memes.items()])
        print(message_to_send)
        await ctx.send(message_to_send[:1999])


    @commands.command()
    async def meme(self, ctx, arg: str = "-1"):
        send = ""
        if arg != "-1" and arg.isdigit():
            send = self.generateMeme(int(arg))
        else:
            send = self.generateMeme()
        await ctx.send(send)
    
    
    def generateMeme(self, template_id: int = -1) -> list[str]:
        
        #print(self.meme_dict)
        meme_error = True
        command_dict = {}
        while meme_error:
            if template_id < 0:
                while template_id not in self.error_memes_dict and template_id < 0:
                    template_id = int(random.choice(list(self.meme_dict.values())))
                    
            cookie_iflipsess = self.config["imgflip_cookie_iflipsess"]
            cookie_email = self.config["imgflip_email"]
            cookie_rootkey = self.config["imgflip_cookie_rootkey"]
            token = self.config["imgflip_token"]
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
                "Cookie":	f"rootkey={cookie_rootkey}; rootemail={cookie_email}; iflipsess={cookie_iflipsess}",
                "Content-Type":	"application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With":	"XMLHttpRequest",
                "Accept":	"application/json, text/javascript, */*; q=0.01"
                }
            search_url = f"https://imgflip.com/ajax_ai_meme"
            data = f'use_openai=0&meme_id={template_id}&init_text=&__tok={token}&__cookie_enabled=1'
            #print(data)
            req = requests.post(search_url, headers=headers, data=data)
            #print(template_id, req.text)
            command_dict = json.loads(req.text)
            
            if "error" not in command_dict:
                meme_error = False#return "Could not get AI response for Template_ID" 
            else:
                self.error_memes_dict[template_id] = 1
                template_id = -1
            
        headers = {
            "Content-Type":	"application/x-www-form-urlencoded; charset=UTF-8",
            }
        search_url = "https://api.imgflip.com/caption_image"
        data = {"template_id":template_id,
                "username":self.config["imgflip_username"],
                "password":self.config["imgflip_password"]
                }
        
        #print(command_dict)
        i = 0
        for text in command_dict["final_text"].split('|')[:-1]:
            data[f"boxes[{i}][text]"] = text
            i+=1
            
        req = requests.post(search_url,  params=data)
        url_dict = json.loads(req.text)
        return url_dict["data"]["url"]

    def listAvailableMemes(self) -> dict:
        return self.meme_dict

    def get_available_memes(self):
        req = requests.get("https://imgflip.com/popular_meme_ids")
        soup = BeautifulSoup(req.text, "html.parser")
        t = soup.find_all("tr")
        meme_dict = {}
        for row in t[1:]:
            vals = row.find_all("td")
            meme_dict[vals[1].get_text()] = vals[0].get_text()
        return meme_dict

if __name__ == "__main__":
    pass
    #m = AIMemeGenerator(None, None)
    #print(m.generateMeme())
    #print("|||".split("|"))



#iflipsess=ireei3b9g8plnco7jhe4jk59cd; claim_key=9MhDZO32A8XanOfLMTDmBc8DI5q9RW0C