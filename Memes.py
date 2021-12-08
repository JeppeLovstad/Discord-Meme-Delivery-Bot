import discord
import os
import GetMeme
from CustomCommandHandler import CustomCommandHandler
from io import BytesIO
import base64

client = discord.Client()
scraper = GetMeme.MemeScraper()
ccHandler = CustomCommandHandler()
command_dict = {}


@client.event
async def on_ready():
    client.get_all_channels()
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    command_list = message.content.split()
    num_of_parameters = len(command_list)
    initial_command = command_list[0]

    if initial_command.startswith("$"):
        if initial_command == '$addcommand' and num_of_parameters >= 3:
            added = ccHandler.addCommand(
                command_list[1], " ".join(command_list[2:]))
            if added:
                await message.channel.send("command added")
            else:
                await message.channel.send("adding command failed")

        if initial_command == '$deletecommand' and num_of_parameters == 2:
            deleted = ccHandler.deleteCommand(command_list[1])
            if deleted:
                await message.channel.send("command deleted")
            else:
                await message.channel.send("deleting command failed")

        if initial_command in ['$addcommand', '$deletecommand']:
            ccHandler.updateFile()

        if initial_command == '$memelist' and num_of_parameters == 1:
            message_to_send = 'index: Meme name\n'
            message_to_send += '\n'.join([f"{k} : {v}" for k,
                                          v in scraper.meme_index_dict.items()])
            await message.channel.send(message_to_send)

        if initial_command == '$meme' and num_of_parameters <= 2:
            incoming_message = message.content.split()
            send = ""
            if num_of_parameters == 2 and incoming_message[1].isdigit():
                send = scraper.updateImage(int(incoming_message[1]))
            else:
                send = scraper.updateImage()
            await message.channel.send(send)

    else:
        ccResponse = ccHandler.getResponseToMessage(message.content)
        if ccResponse:
            await message.channel.send(ccResponse)

# print(os.getenv('DISCORD_TOKEN'))
client.run(REDACTED)
