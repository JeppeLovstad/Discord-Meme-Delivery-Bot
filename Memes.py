import discord
import os
import GetMeme
from io import BytesIO
import base64

client = discord.Client()
scraper = GetMeme.MemeScraper()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    initial_command = message.content.split()[0]

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    if initial_command == '$memelist':
        message_to_send = 'index: Meme name\n'
        message_to_send += '\n'.join([f"{k} : {v}" for k,
                                      v in scraper.meme_index_dict.items()])
        await message.channel.send(message_to_send)
    if initial_command == '$meme':
        incoming_message = message.content.split()
        send = ""
        if len(incoming_message) > 1 and incoming_message[1].isdigit():
            send = scraper.updateImage(int(incoming_message[1]))
        else:
            send = scraper.updateImage()
        await message.channel.send(send)
    if "69" in message.content:
        await message.channel.send('lmao')
    if "96" in message.content:
        await message.channel.send('oaml')
    if "rm -rf" in message.content:
        await message.channel.send('get rekt kiddo')

# print(os.getenv('DISCORD_TOKEN'))
client.run({REDACTED}})
