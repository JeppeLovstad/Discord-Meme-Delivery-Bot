import discord
import os
import GetMeme
from CustomCommandHandler import CustomCommandHandler
from io import BytesIO
from discord.ext import commands
import json
import re

command_prefix = "!"
bot = commands.Bot(command_prefix=command_prefix)
scraper = GetMeme.MemeScraper()
ccHandler = CustomCommandHandler(file_name="commands.json")
reactionHandler = CustomCommandHandler(file_name="reactions.json")

try:
    with open("emoji_map.json", "r") as infile:
        # cast lists to sets
        emoji_dict = {k: v
                      for k, v in json.load(infile).items()}
except FileNotFoundError:
    print("no command file")
    pass

try:
    with open(".env", "r") as file:
        TOKEN = file.readline()
except:
    print("no token, shutting down")
    exit()


@bot.command()
async def addreaction(ctx, arg1: str, arg2):
    response = arg2
    if response == "":
        await ctx.send("Cannot add empty reaction")
        return

    custom_emoji = re.match(r'<:\w*:\d*>', response)
    default_emoji = emoji_dict.get(arg2)
    #print(arg2, default_emoji)

    if not (custom_emoji or default_emoji):
        print(arg2, custom_emoji, default_emoji)
        await ctx.send("Non valid reaction emoji")
        return

    added = reactionHandler.addCommand(arg1, arg2)

    if added:
        await ctx.send("reaction added")
    else:
        await ctx.send("adding reaction failed")


@bot.command()
async def deletereaction(ctx, arg1: str):
    if arg1 == "":
        await ctx.send("Cannot delete empty reaction")
        return
    deleted = reactionHandler.deleteCommand(arg1)
    if deleted:
        await ctx.send("reaction deleted")
    else:
        await ctx.send("deleting reaction failed")


@bot.command()
async def addcommand(ctx, arg1: str, *args):
    response = " ".join(args)
    if response == "":
        await ctx.send("Cannot add empty response")
        return

    added = ccHandler.addCommand(arg1, response)

    if added:
        await ctx.send("command added")
    else:
        await ctx.send("adding command failed")


@bot.command()
async def deletecommand(ctx, arg1: str):
    if arg1 == "":
        await ctx.send("Cannot delete empty command")
        return
    deleted = ccHandler.deleteCommand(arg1)
    if deleted:
        await ctx.send("command deleted")
    else:
        await ctx.send("deleting command failed")


@bot.command()
async def customcommandslist(ctx):
    message_to_send = '\n'.join(
        [f"{v}" for v in ccHandler.command_dict.keys() if v != ""])
    await ctx.send(message_to_send)


@bot.command()
async def memelist(ctx):
    message_to_send = 'index: Meme name\n'
    message_to_send += '\n'.join([f"{k} : {v}" for k,
                                  v in scraper.meme_index_dict.items()])
    await ctx.send(message_to_send)


@bot.command()
async def meme(ctx, arg: str = "-1"):
    send = ""
    if arg != "-1" and arg.isdigit():
        send = await scraper.getMeme(int(arg))
    else:
        send = await scraper.getMeme()
    await ctx.send(send)


@bot.event
async def on_ready():
    bot.get_all_channels()
    print('We have logged in as {0.user}'.format(bot))


@bot.listen('on_message')
async def CustomCommandResponder(message):
    if message.author == bot.user:
        return
    if message.content == "":
        return
    # legacy code do not delete
    # if message.author.name == 'Lasse Morgen':
    #    await message.add_reaction("<:LasseWut:912650302589648907>")

    if not message.content.startswith(command_prefix):
        ccResponse = ccHandler.getResponseToMessage(message.content)
        if ccResponse:
            await message.channel.send(ccResponse)

        reactionResponse = reactionHandler.getResponseToMessage(
            message.content,
            single_response=True)

        if reactionResponse:
            await message.add_reaction(reactionResponse)


bot.run(TOKEN)
