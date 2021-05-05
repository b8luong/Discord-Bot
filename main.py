from dotenv import load_dotenv
from flask import Flask
import discord
import os
import requests
import json
import mysql.connector
import random

# .env file from root

load_dotenv()

# initializing variables from env file
TOKEN = os.getenv("TOKEN")
app_id = os.getenv("APP_ID")
public_key = os.getenv("PUBLIC_KEY")
# mySql credentials
sqlHost = os.getenv("host")
sqlUser = os.getenv("user")
sqlPasswd = os.getenv("passwd")

# Creating flask app.
app = Flask(__name__)

# initializing mysql db
db = mysql.connector.connect(
    host=sqlHost,
    user=sqlUser,
    passwd=sqlPasswd
)

mycursor = db.cursor()
mycursor.execute("CREATE DATABASE reminders")

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

    # example to do split
    '''
    if msg.startswith("$new"):
        encouraging_message = msg.split("$new ",1)[1]
        update_encouragements(encouraging_message)
        await message.channel.send("New encouraging message added.")
    '''

    if msg.startswith("!setdate"):
        reminder = msg.split("!setdate ",1)[1]
        await message.channel.send("Reminder has been set")

client.run(os.getenv("TOKEN"))

# start app
if __name__ == "__main__":
    app.run(debug=True)