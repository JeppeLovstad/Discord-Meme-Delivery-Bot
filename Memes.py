import discord
import os
import GetMeme
from io import BytesIO
import base64

client = discord.Client()
m = GetMeme.MemeScraper()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    if message.content.startswith('$boi'):
        m.updateImage()
        #file = discord.File(BytesIO(base64.b64decode(m.Image)))
        await message.channel.send(m.ImageLink)
    if "69" in message.content:
        await message.channel.send('lmao')
    if "96" in message.content:
        await message.channel.send('oaml')
    if "rm -rf" in message.content:
        await message.channel.send('get rekt kiddo')

# print(os.getenv('DISCORD_TOKEN'))
client.run({REDACTED})
