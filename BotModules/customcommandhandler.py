from io import FileIO
import json
from itertools import combinations
import random
from discord.ext import commands
import discord
#from functools import wraps

class CustomCommandHandler(commands.Cog):
    
    add_command = ""
    remove_command = ""
    
    def __init__(self, config, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = config
        self.remove_command = self.config["remove_command"]
        self.remove_command = self.config["add_command"]
        self.command_prefix = self.config["command_prefix"]
        self.get_single_response = config["get_single_response"] == "True" if "get_single_response" in config else False
        self.file_name = config["json_file_location"] if "json_file_location" in config else ""
        self.command_dict = {}
        self.initiateFile()
        #self.add_bot_command(bot)
        
        
    #def add_bot_command(self,bot: commands.Bot):
     #   bot.add_command
    
    def initiateFile(self):
        try:
            with open(self.file_name, "r") as infile:
                # cast lists to sets
                self.command_dict = {k: set(v)
                                     for k, v in json.load(infile).items()}
        except FileNotFoundError:
            print("no command file")
            pass
        # file broken continue with new file
        except Exception as e:
            print(e)
            print("command file load failed")
            pass

    @commands.Cog.listener(name="on_message")
    async def CustomCommandResponder(self, message:discord.Message):
        if message.author == self.bot.user:
            return
        if message.content == "":
            return
        
        if not message.content.startswith(self.command_prefix):
            ccResponse = self.getResponseToMessage(message.content)
            if ccResponse:
                await message.reply(ccResponse)

    @commands.command()
    async def addcommand(self, ctx, arg1: str, *args):
        response = " ".join(args)
        if response == "":
            await ctx.send("Cannot add empty response")
            return

        added = self.addCommand(arg1, response)

        if added:
            await ctx.send("command added")
        else:
            await ctx.send("adding command failed")


    @commands.command()
    async def deletecommand(self, ctx, arg1: str):
        if arg1 == "":
            await ctx.send("Cannot delete empty command")
            return
        deleted = self.deleteCommand(arg1)
        if deleted:
            await ctx.send("command deleted")
        else:
            await ctx.send("deleting command failed")

    def addCommand(self, command: str, response: str) -> bool:
        try:
            # use set for no duplicates
            self.command_dict.setdefault(command, set()).add(response)
            self.updateFile()
            return True
        except Exception as e:
            print(e)
            return False

    def deleteCommand(self, command: str) -> bool:
        try:
            if command in self.command_dict:
                self.command_dict.pop(command)
                self.updateFile()
                return True
            return False
        except:
            return False

    def getResponseToMessage(self, message: str) -> str:
        commands = message.split()
        commands_expanded = []

        single_response = self.get_single_response

        # Get all possible slices
        for i, j in combinations(range(len(commands) + 1), 2):
            commands_expanded.append(" ".join(commands[i:j]))
        # Get responses to commands, filter away None
        valid_commands = list(filter(lambda x: x != "", map(
            self.getResponseToCommand, commands_expanded)))
        
        
        if valid_commands and not single_response:
            return '\n'.join(valid_commands)
        elif valid_commands and single_response:
            return random.choice(valid_commands)
        else:
            return ""

    def getResponseToCommand(self, command: str) -> str:

        try:
            if command in self.command_dict:
                commands = list(self.command_dict[command])
            else:
                return ""
        except:
            return ""
        return random.choice(commands)  # '\n'.join([f"{v}" for v in commands])

    def updateFile(self) -> bool:
        try:
            # Cast to list, since set cant be json dumped
            intermediateDict = {k: list(v)
                                for k, v in self.command_dict.items()}
            with open(self.file_name, "w") as outfile:
                json.dump(intermediateDict, outfile)
            return True
        except Exception as e:
            print(e)
            return False

    

    # Cannot call open in del
    # def __exit__(self):
    #     print("saving file")
    #     with open(self.file_name, "w") as outfile:
    #         json.dump(self.command_dict, outfile)


#c = CustomCommandHandler()
# print(c.addCommand("test", "wow much so"))
# print(c.addCommand("test", "wow much too"))
# print(c.deleteCommand("test"))
# print(c.addCommand("i am", "wow much too"))
# print(c.addCommand("i am", "wow much too test"))
# print(c.getResponseToMessage("i am test this"))
# print(c.updateFile())
