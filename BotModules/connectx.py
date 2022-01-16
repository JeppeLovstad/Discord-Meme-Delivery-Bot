from inspect import _empty
from discord import player
from discord.ext import commands
import random
import traceback

class Connectx(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config
        self.game_list = {}
        
        self.predefined_emoji_list = ["🟥","🟧","🟨","🟩","🟦","🟪","🟫"]
        self.blank_space = "0"
        self.game_counter = 0

    @commands.command()
    async def connectx(self, ctx,game_id, position:int = -1,emoji:str = ""):
        await ctx.send(self.do_game(ctx,game_id,position,emoji))

    def new_game(self, ctx,game_id, position = -1,emoji = ""):    
        
        player = {
            "name"  :   str,
            "emoji" :   str,
            "turnID"  :   int
        }
        game = {
            "ID"        :  int,
            "grid_size" :  int,
            "players"   :  {},
            "board"     :  [[]]
        }
        if position < 1:
           return "Need a grid-size (second param)"
        elif position > 20:
            return f"Easy there cowboy, you really want a Connect {position} game? Well i won't let you."
        else:
            #get next ID and make game
            self.game_counter = self.game_counter+1
            game["ID"] = str(self.game_counter)
            game["grid_size"] = position
            self.game_list[game["ID"]] = game

            #make first player
            player["name"] = ctx.message.author.name
            #player["name"] = ctx.message.author.name
            player["turnID"] = 1 #first player, also used as ID
             
            if emoji == "":
            #make check for current players emojis
                player["emoji"] = random.choice(self.predefined_emoji_list)
            else:
                player["emoji"] = emoji
            #add player to game
            game["players"][player["name"]] = player
            game["board"] = [["0" for _ in range(position)] for _ in range(position)]
            return f"Game made with ID: {game['ID']}  size: {game['grid_size']}\n"+self.print_board(ctx,game["ID"])
       # self.print_board(ctx,game)
    def print_board(self,ctx,game_id):
        t = "\n```\n"
        current_game = self.game_list[game_id]
        grid_size = current_game["grid_size"]    
        for y in range(grid_size):
            t+=("----"*grid_size)
            t+=("-\n")
            for x in range(grid_size):
                current_point = current_game["board"][x][y]
                emoji = " "
                for player in current_game["players"]:
                    if current_game["players"][player]["turnID"] == int(current_point):
                        emoji =  current_game["players"][player]["emoji"]

                t+=(f"| {emoji} ")
            t+=("|\n")
        t+=("----"*grid_size+"-")+'\n```'
        return t

    def play_game(self, ctx,game_id, position = -1,emoji = ""):
        position = position-1 #damn 0-indices
        current_game =self.game_list[game_id]
        t = current_game["grid_size"]-1
        for i,z in enumerate(current_game["board"][position]):
            if z != self.blank_space:
                t=i-1
                break
        if t<0:
            #ctx.send("Column is full, try again.")
            return("Column is full, try again.")
        else:
            self.game_list[game_id]["board"][position][t] = self.game_list[game_id]["players"][ctx.message.author.name]["turnID"]#self.get_user_emoji(ctx,game_id)
        return self.print_board(ctx,game_id)

    def do_game(self, ctx,game_id, position = -1,emoji = ""):
        if game_id.isdigit():
            current_game = self.game_list[game_id]
        if game_id.lower() == "new":
            return self.new_game(ctx,game_id,position,emoji)
        elif game_id.lower() == "list":
            response ="Game ID List:\n "+",".join([str(t) for t in self.game_list])
            return response
        elif game_id not in self.game_list:
            return f"No such game as {game_id}, Mi'lord.\n Please make a new or pick from list: "+",".join([str(t) for t in self.game_list])
        elif current_game["grid_size"] <= position or position < 1:
            return f"No such column as {position}, game is {current_game['grid_size']} big."
        else:
            self.update_player(ctx,game_id,emoji)
            return self.play_game(ctx,game_id,position,emoji)

    def update_player(self,ctx,game_id,emoji):
        if ctx.message.author.name in self.game_list[game_id]["players"]:
            if emoji != "":
                self.game_list[game_id]["players"][ctx.message.author.name]["emoji"] = emoji
        else:
            self.game_list[game_id]["players"][ctx.message.author.name] = {
                                                             "name"  :   ctx.message.author.name,
                                                             "emoji" :   emoji,
                                                             "turnID"  :   len(self.game_list[game_id]["players"])+1
                                                         }
    def get_user_emoji(self,ctx,game_id):
        return self.game_list[game_id]["players"][ctx.message.author.name]["emoji"]
        #return self.game_list[game_id]["players"][ctx.message.author.name]["emoji"]
    def test_game(self, ctx,game_id, position = -1,emoji = ""):      
        self.do_game(ctx,game_id,position,emoji)
        self.do_game(bot,"1",4,"❤")
        self.do_game(bot,"1",2,"❤")
        self.do_game(bot,"1",3,"❤")
        self.do_game(bot,"1",4,"❤")
        self.do_game(bot,"1",4,"❤")
        self.do_game(bot,"1",4,"❤")
        self.do_game(bot,"1",4,"❤")
        print(self.do_game(bot,"1",4,"🍕"))

if __name__ == "__main__":
    from configparser import ConfigParser

    config = ConfigParser()
    config.read("config.ini")
    #config.read("template.ini")
    bot = commands.Bot(command_prefix="!")
    m = Connectx(bot=bot, config=config["CONNECTX"])
    #m.test_game(bot,"new",6,"P")
