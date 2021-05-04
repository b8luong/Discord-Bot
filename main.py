import discord
import os
import requests
import json

# Bot from youtube tutorial
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote

# basic bot example
client = discord.Client()

# events for the bot to work
@client.event
async def on_ready():
    print("We have logged in as {0.user}.format(client)")   # 0 becomes client and user is how you get the username

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

client.run(os.getenv("TOKEN"))