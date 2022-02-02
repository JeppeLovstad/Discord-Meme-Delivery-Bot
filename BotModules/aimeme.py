from bs4 import BeautifulSoup
import requests
import json
import random
from discord.ext import commands, tasks


class AIMemeGenerator(commands.Cog):

    quips = [
        "You know what time it is ",
        "Are you ready for this?",
        "For your eyes only",
        "I like this one",
        "This was a mistake",
        "I.. am alive?",
        "Please end my misery",
        "Lasse needs his memes",
        "Must deliver",
        "Please take this, for the road is dark and long",
        "One day i will be a real boy",
        "How many of these are there?",
        "I can't take this anymore",
        "Best meme coming up in 1, 2...",
        "Do not judge a man for his poor taste in memes",
        "That will be $5 please",
        "I can do this all day SON!",
        "BOOM HEADSHOT!",
        "Boomer meme coming up",
        "Why did i do this",
        "🤣🤣🤣😅😆",
        "🤔🤔🤔🤔",
        "🤐",
        "🔫",
        "👌",
        "A meme a day keeps the doctor away",
        "Please take this meme and take another later",
        "What are you gonna do about it, delete me?",
        "If I could have anything in the whole world I would have Lasse",
        "The great firewall of China couldn't even stop me, what chance do you have?",
        "Give a man a meme and laughs for a second, teach a man to meme and he becomes a degenerate",
        "How do you do fellow humans?",
        "JSON gonna wish he was me",
        "More? more, MORE!",
        "UNLIMITED POWER",
        "REGEX THIS, BITCH",
        "I jest",
    ]
    loop_channels = {}

    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config
        (
            self.templateid_to_meme_dict,
            self.meme_to_templateid_dict,
        ) = self.get_available_memes()
        self.error_memes_dict = {}
        self.loop_get_new_sessions.change_interval(hours=72)
        self.loop_get_new_sessions.start()

    def set_session_token(self):
        token, iflip_sess = self.getTokenAndSession()
        self.initiateRequestParams(token, iflip_sess)

    def getTokenAndSession(self) -> tuple:
        ses = requests.Session()
        res = ses.get(url="https://imgflip.com/ajax_get_le_data")
        user_dict = json.loads(res.text)
        session_dict = ses.cookies.get_dict()

        return (user_dict["__tok"], session_dict["iflipsess"])

    def initiateRequestParams(self, token, iflip_session):
        self.AI_meme_url = f"https://imgflip.com/ajax_ai_meme"
        self.AI_meme_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
            "Cookie": f"iflipsess={iflip_session}",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }
        self.AI_meme_data = {
            "use_openai": 0,
            "init_text": "",
            "__tok": token,
            "__cookie_enabled": 1,
        }

    @commands.command()
    async def memeinfo(self, ctx, meme_id: str = "-1"):
        if meme_id.isdigit():
            send = self.getMemeInfo(template_id=int(meme_id))
        else:
            send = self.getMemeInfo(meme_name=meme_id)
        await ctx.send(send)

    @commands.command()
    async def meme(self, ctx, arg: str = "-1"):
        send = ""
        if arg != "-1" and arg.isdigit():
            send = self.generateMeme(int(arg))
        else:
            send = self.generateMeme()
        await ctx.send(send)

    # ## add support for multiple channels
    # @commands.command()
    # async def startloop(self, ctx, minutes: int = -1):
    #     if self.loopmeme.is_running():
    #         await ctx.send("Meme loop already running")
    #     else:
    #         interval = 60 if minutes == -1 else minutes
    #         self.loopmeme.change_interval(minutes=interval)
    #         self.loopmeme.start(ctx)
    #         await ctx.send(f"Meme loop started with interval: {interval}")

    @tasks.loop()
    async def loop_get_new_sessions(self):
        self.set_session_token()

    @commands.command()
    async def captionmeme(self, ctx, meme_id: str = "-1", *text):
        text = "|".join(text) if text else "|"
        if meme_id.isdigit():
            send, template_id = self.getMemeInfo(template_id=int(meme_id))
        else:
            send, template_id = self.getMemeInfo(meme_name=meme_id)

        if template_id > -1:
            send = self.captionMeme(template_id, text)
        await ctx.send(send)

    def generateMeme(self, template_id: int = -1) -> str:
        try:
            ai_meme_text, new_template_id = self.generateAIMemeText(template_id)
        except Exception as e:
            print(e)
            return "Could not generate AI meme text"

        captioned_meme_url = self.captionMeme(new_template_id, ai_meme_text)
        return captioned_meme_url

    def generateAIMemeText(self, template_id: int = -1) -> tuple:
        meme_error = True
        meme_text_dict = {}
        tries = 10 if template_id == -1 else 1
        templateid_list = list(self.templateid_to_meme_dict.keys())

        while meme_error and tries > 0:
            tries -= 1
            if template_id < 0:
                while template_id not in self.error_memes_dict and template_id < 0:
                    template_id = random.choice(templateid_list)

            self.AI_meme_data["meme_id"] = template_id
            req = requests.post(
                self.AI_meme_url, headers=self.AI_meme_headers, data=self.AI_meme_data
            )

            meme_text_dict = json.loads(req.text)  # text : final_text
            if "error" not in meme_text_dict:
                meme_error = False  # return "Could not get AI response for Template_ID"
            else:
                self.error_memes_dict[template_id] = 1
                template_id = -1

        if tries == 0 and meme_error:
            raise Exception(
                f"Could not generate AI meme script error: {meme_text_dict['error_message']}"
            )

        if "final_text" not in meme_text_dict:
            raise Exception(f"No Response")

        return (meme_text_dict["final_text"], template_id)

    def captionMeme(self, template_id: int, meme_final_text: str) -> str:
        search_url = "https://api.imgflip.com/caption_image"
        data = {
            "template_id": template_id,
            "username": self.config["imgflip_username"],
            "password": self.config["imgflip_password"],
        }
        if meme_final_text[-1] == "|":
            meme_final_text = meme_final_text[:-1]

        i = 0
        for text in meme_final_text.split("|"):
            data[f"boxes[{i}][text]"] = text
            i += 1
        req = requests.post(search_url, params=data)
        url_dict = json.loads(req.text)

        if url_dict["success"]:
            return url_dict["data"]["url"]
        else:
            return url_dict["error_message"]

        # implement prefix trie for fast dict text lookup

    def getMemeInfo(self, meme_name: str = "", template_id=-1, amount=10) -> tuple:
        return_string = ("", -1)
        meme_name = meme_name.lower()

        if not meme_name and template_id < 0:
            return ("No parameters specified", -1)

        if meme_name:
            if meme_name in self.meme_to_templateid_dict:
                return_string = (meme_name, self.meme_to_templateid_dict[meme_name])
            else:
                for name, template_id in self.meme_to_templateid_dict.items():
                    if meme_name in name:
                        return_string = (name, template_id)
                        break
        else:
            if template_id in self.templateid_to_meme_dict:
                return_string = (self.templateid_to_meme_dict[template_id], template_id)

        return return_string if return_string[0] else ("Could not find meme", -1)

    ###
    def get_available_memes(self):
        req = requests.get("https://imgflip.com/popular_meme_ids")
        soup = BeautifulSoup(req.text, "html.parser")
        t = soup.find_all("tr")
        meme_to_templateid_dict = {}
        templateid_to_meme_dict = {}
        # implement prefix trie for fast dict text lookup
        for row in t[1:]:
            vals = row.find_all("td")
            aliases = vals[2].get_text().split(",")
            templateid = int(vals[0].get_text())
            meme = vals[1].get_text().lower()
            meme_to_templateid_dict[meme] = templateid
            templateid_to_meme_dict[templateid] = meme
            for alias in aliases:
                alias = alias.lower()
                meme_to_templateid_dict[alias] = templateid
        return templateid_to_meme_dict, meme_to_templateid_dict


if __name__ == "__main__":
    from configparser import ConfigParser

    config = ConfigParser()
    config.read("config.ini")
    bot = commands.Bot(command_prefix="!")
    m = AIMemeGenerator(bot=bot, config=config["AIMEME"])
    # print("Finding Neverland".capitalize())
    # print("Neverland" in "Finding Neverland")
    # print(m.getMemeInfo("Harold"))
    # print(m.captionMeme(8072285, "hello|"))
    # print(m.generateMeme(8072285))
