import discord
import os
import GetMeme
from CustomCommandHandler import CustomCommandHandler
from io import BytesIO
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
scraper = GetMeme.MemeScraper()
ccHandler = CustomCommandHandler()


try:
    with open(".env", "r") as file:
        TOKEN = file.readline()
except:
    print("no token, shutting down")
    exit()


@bot.command()
async def addcommand(ctx, arg1: str, *args):
    added = ccHandler.addCommand(
        arg1, " ".join(args))
    if added:
        await ctx.send("command added")
    else:
        await ctx.send("adding command failed")


@bot.command()
async def deletecommand(ctx, arg1: str):
    deleted = ccHandler.deleteCommand(arg1)
    if deleted:
        await ctx.send("command deleted")
    else:
        await ctx.send("deleting command failed")


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
        send = scraper.updateImage(int(arg))
    else:
        send = scraper.updateImage()
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
    if message.author.name == 'Lasse Morgen':
        await message.add_reaction(":LasseWut:912650302589648907")

    ccResponse = ccHandler.getResponseToMessage(message.content)
    if ccResponse:
        await message.channel.send(ccResponse)


bot.run(TOKEN)
