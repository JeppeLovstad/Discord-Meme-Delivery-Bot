import json
from itertools import combinations
import random
from discord.ext import commands
import discord
import emoji
import re

class CustomCommandHandler(commands.Cog):
    def __init__(self, config, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = config
        self.updateCommandNames(config)
        self.get_single_response = (
            config["get_single_response"] == "True"
            if "get_single_response" in config
            else False
        )
        file_name = (
            config["json_file_location"] if "json_file_location" in config else ""
        )
        self.command_dict = {}
        self.reply_type = config["reply_type"]
        self.initiateFile(file_name)
        # self.add_bot_command(bot)

    def updateCommandNames(self, config):
        commands = super().get_commands()
        for command in commands:
            if command.name == "addcommand" and "add_command" in config:
                command.name = config["add_command"]
            if command.name == "deletecommand" and "delete_command" in config:
                command.name = config["delete_command"]

    def initiateFile(self, file_name="command.json"):
        try:
            with open(file_name, "r") as infile:
                # cast lists to sets
                self.command_dict = {k: set(v) for k, v in json.load(infile).items()}
        except FileNotFoundError:
            print("no command file")
            pass
        # file broken continue with new file
        except Exception as e:
            print(e)
            print("command file load failed")
            pass

    @commands.Cog.listener(name="on_message")
    async def CustomCommandResponder(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if message.content == "":
            return

        if not message.content.startswith(self.bot.command_prefix):
            ccResponse = self.getResponseToMessage(message.content)
            if ccResponse:
                if self.reply_type == "message":
                    await message.reply(ccResponse)
                if self.reply_type == "reaction":
                    await message.add_reaction(ccResponse)

    @commands.command()
    async def addcommand(self, ctx, arg1: str, *args):
        response = " ".join(args)
        if response == "":
            await ctx.send("Cannot add empty response")
            return

        added = self.addCommand(arg1, response)

        if self.reply_type == "reaction":
            if not self.emojiIdentifier(response):
                await ctx.send("non valid emoji")
                return

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

    def emojiIdentifier(self, text_with_emoji):
        custom_emoji = re.match(r"<:\w*:\d*>", text_with_emoji)
        default_emoji = (
            emoji.emoji_lis(text_with_emoji)[0]["emoji"]
            if emoji.emoji_count(text_with_emoji) == 1
            else None
        )
        print(text_with_emoji, custom_emoji, default_emoji)
        return custom_emoji or default_emoji

    def getResponseToMessage(self, message: str) -> str:
        commands = message.split()
        commands_expanded = []

        single_response = self.get_single_response

        # Get all possible slices
        for i, j in combinations(range(len(commands) + 1), 2):
            commands_expanded.append(" ".join(commands[i:j]))
        # Get responses to commands, filter away None
        valid_commands = list(
            filter(lambda x: x != "", map(self.getResponseToCommand, commands_expanded))
        )

        if valid_commands and not single_response:
            return "\n".join(valid_commands)
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
            intermediateDict = {k: list(v) for k, v in self.command_dict.items()}
            with open(self.config["json_file_location"], "w") as outfile:
                json.dump(intermediateDict, outfile)
            return True
        except Exception as e:
            print(e)
            return False



