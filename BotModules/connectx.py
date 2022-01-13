from inspect import _empty
from discord.ext import commands
import random
import traceback

class Connectx(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config
        self.game_list = {}
        
        self.predefined_emoji_list = ["🟥","🟧","🟨","🟩","🟦","🟪","🟫"]
        self.game_counter = 0

    @commands.command()
    async def connectx(self, ctx,game, position = -1,emoji = ""):
        msg = self.do_game(ctx,game,position,emoji)

    def new_game(self, ctx,game, position = -1,emoji = ""):    
        
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
            game["ID"] = self.game_counter
            game["grid_size"] = position
            self.game_list[self.game_counter] = game

            #make first player
            player["name"] = "papa"#temp #ctx.author
            player["turnID"] = 1 #first player, also used as ID
             
            if emoji == "":
            #make check for current players emojis
                player["emoji"] = random.choice(self.predefined_emoji_list)
            else:
                player["emoji"] = emoji
            #add player to game
            game["players"][player["name"]] = player
            game["board"] = [["0" for _ in range(position)] for _ in range(position)]
       # self.print_board(ctx,game)
    def print_board(self,ctx,game):
        t = ""
        current_game = self.game_list[int(game)]
        grid_size = current_game["grid_size"]
        emoji = " "
        for y in range(grid_size):
            t+=("----"*grid_size)
            t+=("-\n")
            for x in range(grid_size):
                emoji = current_game["board"][x][y]        
                t+=(f"| {emoji} ")
            t+=("|\n")
        t+=("----"*grid_size+"-")
        return t
    def play_game(self, ctx,game, position = -1,emoji = ""):
        return self.print_board(ctx,game)

    def do_game(self, ctx,game, position = -1,emoji = ""):
        if game.lower() == "new":
         return self.new_game(ctx,game,position,emoji)
      #  elif game not in self.game_list:
       #     return f"No such game as {game}, Mi'lord"
        else:
            self.new_game(ctx,game,position,emoji)
            return self.play_game(ctx,game,position,emoji)
if __name__ == "__main__":
    from configparser import ConfigParser

    config = ConfigParser()
    config.read("config.ini")
    bot = commands.Bot(command_prefix="!")
    m = Connectx(bot=bot, config=config["CONNECTX"])
    #m = Connectx(0,0)
    print(m.do_game(0,"1",5))
