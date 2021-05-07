from dotenv import load_dotenv
from flask import Flask
import discord
import logging
import os
import requests
import json
import mysql.connector
import time
from datetime import datetime

# error logging
logging.basicConfig(level=logging.INFO)

# .env file
load_dotenv()

# initializing variables from env file
TOKEN = os.getenv("TOKEN")
app_id = os.getenv("APP_ID")
public_key = os.getenv("PUBLIC_KEY")
# mySql credentials
sqlHost = os.getenv("host")
sqlUser = os.getenv("user")
sqlPasswd = os.getenv("passwd")
sqlDatabase = os.getenv("database")
# Creating flask app.
app = Flask(__name__)

# initializing mysql db
db = mysql.connector.connect(
    host=sqlHost,
    user=sqlUser,
    passwd=sqlPasswd,
    database=sqlDatabase
)

mycursor = db.cursor()
# mycursor.execute("CREATE DATABASE reminders")
# mycursor.execute("CREATE TABLE reminders (id INT AUTO_INCREMENT PRIMARY KEY, date VARCHAR(255), who VARCHAR(255), what VARCHAR(255), remind VARCHAR(255))")


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

    # if any(word in msg for word in sad_words):
    #     await message.channel.send(random.choice(starter_encouragements))

    # example to do split
    '''
    if msg.startswith("$new"):
        encouraging_message = msg.split("$new ",1)[1]
        update_encouragements(encouraging_message)
        await message.channel.send("New encouraging message added.")
    '''

    if msg.startswith("!setdate"):
        # split the message on the command word
        content = msg.split("!setdate",1)[1]
        print(content)
        list = content.split("\n")
        print(list)

        # store the time of the event
        when_str = list[1].split("When: ",1)[1]
        date_obj = datetime.strptime(when_str, "%m/%d/%y %H:%M:%S")
        print(date_obj)
        # store the people to mention for the reminder
        who = list[2].split("Who: ",1)[1]
        print(who)
        # store the message to remind
        what = list[3].split("What: ",1)[1]
        print(what)
        # store into table for the future
        mycursor.execute("INSERT INTO reminders VALUES(NULL, %s, %s, %s, 'fill')",(when_str,who,what))

        # grab the user id for who set the reminder
        user = message.author.id
        # await message.channel.send(f"<@{user}> Reminder has been set. \n{content} ")
        await message.channel.send(f"<@{user}>\nWhen: {when_str}\nWho: {who}\nWhat: {what}\n")
client.run(os.getenv("TOKEN"))

# start app
if __name__ == "__main__":
    app.run(debug=True)