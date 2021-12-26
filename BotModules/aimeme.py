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
        token, iflip_sess = self.getTokenAndSession()
        self.initiateRequestParams(token, iflip_sess)
        
    def getTokenAndSession(self) -> tuple:
        ses = requests.Session()
        res = ses.get(url='https://imgflip.com/ajax_get_le_data')
        user_dict = json.loads(res.text)
        session_dict = ses.cookies.get_dict()
        
        return (user_dict['__tok'], session_dict['iflipsess'])
    
    def initiateRequestParams(self, token, iflip_session):
            self.AI_meme_url = f"https://imgflip.com/ajax_ai_meme"
            self.AI_meme_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
                "Cookie":	f"iflipsess={iflip_session}",
                "Content-Type":	"application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With":	"XMLHttpRequest",
                "Accept":	"application/json, text/javascript, */*; q=0.01"
                }
            self.AI_meme_data = {'use_openai':0,
                                 'init_text':'',
                                 '__tok':token,
                                 '__cookie_enabled':1}
    
    
    @commands.command()
    async def memelist(self, ctx):
        message_to_send = 'Meme name: Id\n'
        memes = self.listAvailableMemes()
        print(memes)
        message_to_send += '\n'.join([f"{k} : {v}" for k,
                                    v in memes.items()])
        await ctx.send(message_to_send[:1999])


    @commands.command()
    async def meme(self, ctx, arg: str = "-1"):
        send = ""
        if arg != "-1" and arg.isdigit():
            send = self.generateMeme(int(arg))
        else:
            send = self.generateMeme()
        await ctx.send(send)
    
    def generateMeme(self, template_id:int = -1) -> str:
        try:
            ai_meme_text,new_template_id = self.generateAIMemeText(template_id)
        except Exception as e:
            print(e)
            return "Could not generate AI meme text"
        
        try:
            captioned_meme_url = self.captionMeme(new_template_id, ai_meme_text)
        except Exception as e:
            print(e)
            return "Could not caption meme"
        
        return captioned_meme_url
    
    def generateAIMemeText(self, template_id: int = -1) -> tuple:
        meme_error = True
        meme_text_dict = {}
        tries = 10 if template_id == -1 else 1
        
        while meme_error and tries > 0:
            tries -= 1
            if template_id < 0:
                while template_id not in self.error_memes_dict and template_id < 0:
                    template_id = int(random.choice(list(self.meme_dict.values())))
                    
            self.AI_meme_data['meme_id'] = template_id
            req = requests.post(self.AI_meme_url, headers=self.AI_meme_headers, data=self.AI_meme_data)
            
            meme_text_dict = json.loads(req.text) # text : final_text
            if "error" not in meme_text_dict:
                meme_error = False#return "Could not get AI response for Template_ID" 
            else:
                self.error_memes_dict[template_id] = 1
                template_id = -1
            
        if tries == 0:
            raise Exception(f"Could not generate AI meme script")
        
        if 'final_text' not in meme_text_dict:
            raise Exception(f"No Response")
        
        return meme_text_dict['final_text'],template_id
            


    def captionMeme(self, template_id:int, meme_final_text:str) -> str:
        search_url = "https://api.imgflip.com/caption_image"
        data = {"template_id":template_id,
                "username":self.config["imgflip_username"],
                "password":self.config["imgflip_password"]
                }
        
        i = 0
        for text in meme_final_text.split('|')[:-1]:
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
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
    #"Cookie":	f"rootkey={cookie_rootkey}; rootemail={cookie_email}; iflipsess={cookie_iflipsess}",
    #"Content-Type":	"application/x-www-form-urlencoded; charset=UTF-8",
    #"X-Requested-With":	"XMLHttpRequest",
    #"Accept":	"application/json, text/javascript, */*; q=0.01"
    }
    session = requests.Session()
    #cookie = session.get(url='https://imgflip.com')
    #print(session.cookies)
    #print(session.cookies.get_dict())
    
    res = session.get(url='https://imgflip.com/ajax_get_le_data')
    print(session.cookies.get_dict())
    print(json.loads(res.text))


