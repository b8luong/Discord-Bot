from dotenv import load_dotenv
from flask import Flask
import discord
from discord.ext import tasks, commands
import logging
import os
import requests
import json
import mysql.connector
import time
from datetime import datetime
from threading import Timer
import dateutil.parser
import asyncio

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
    database=sqlDatabase,
    autocommit=True
)


# mycursor.execute("CREATE DATABASE reminders")
# mycursor.execute("CREATE TABLE reminders (id INT AUTO_INCREMENT PRIMARY KEY, date VARCHAR(255), who VARCHAR(255), what VARCHAR(255), remind VARCHAR(255))")

# basic bot example
client = discord.Client()

# getting current time and date
now = datetime.now()
formatNow = now.strftime("%m/%d/%Y %H:%M")
print(formatNow)

# events for the bot to work
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))   # 0 becomes client and user is how you get the username
    check_time.start()

@client.event
async def on_message(message):
    msg = message.content

    if msg.startswith("!setdate"):
        # split the message on the command word
        content = msg.split("!setdate",1)[1]
        print(content)
        list = content.split("\n")
        print(list)

        # variable for the time and date
        when_str = list[1].split("When: ",1)[1]
        date_obj = dateutil.parser.parse(when_str)
        date_obj = date_obj.strftime("%m/%d/%Y %H:%M")
        print(date_obj)


        # variable to store the people to mention for the reminder
        who = list[2].split("Who: ",1)[1]
        print(who)
        # variable to store the message to remind
        what = list[3].split("What: ",1)[1]
        print(what)
        # variable store how often to remind
        remind = list[4].split("Remind: ",1)[1]
        print(remind)
        # cursor for database
        mycursor = db.cursor()
        # store into table for the future
        mycursor.execute("INSERT INTO reminders VALUES(NULL, %s, %s, %s, %s)",(str(date_obj),who,what,remind))
        db.commit()

        # test code for querying for table data
        mycursor.execute("SELECT * FROM reminders")
        table = mycursor.fetchall()
        for rows in table:
            print(rows)
        mycursor.execute("SELECT date FROM reminders WHERE id")
        all_dates = mycursor.fetchall()

        # grab the user id for who set the reminder
        user = message.author.id
        # await message.channel.send(f"<@{user}> Reminder has been set. \n{content} ")
        await message.channel.send(f"<@{user}>\nWhen: {when_str}\nWho: {who}\nWhat: {what}\n")

@tasks.loop(minutes=1)
async def check_time():
    channel = client.get_channel(839197220431331349)
    await channel.send("hello")
    # channel = "<#839197220431331349>"
    # await

# print.start()

client.run(os.getenv("TOKEN"))
# start app
if __name__ == "__main__":
    app.run(debug=True)