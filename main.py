import discord
import os
import requests
import json
import random

# Bot from youtube tutorial
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote

# basic bot example
client = discord.Client()

sad_words = ["sad", "depressed"]
starter_encouragements = ["Cheer up!"]

# events for the bot to work
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))   # 0 becomes client and user is how you get the username

@client.event
async def on_message(message):
    msg = message.content
    if message.author == client.user:
        return

    if msg.startswith("!inspire"):
        quote=get_quote()
        await message.channel.send(quote)

    if any(word in msg for word in sad_words):
        await message.channel.send(random.choice(starter_encouragements))

client.run(os.getenv("TOKEN"))