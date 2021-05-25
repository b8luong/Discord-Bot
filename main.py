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

@client.event
async def on_message(message):
    msg = message.content

    if msg.startswith("!setdate"):
        # split the message on the command word
        content = msg.split("!setdate",1)[1]
        print(content)
        list = content.split("\n")
        print(list)

        # store the time of the event
        when_str = list[1].split("When: ",1)[1]
        date_obj = datetime.strptime(when_str, "%m/%d/%y %H:%M")
        print(date_obj)


        # store the people to mention for the reminder
        who = list[2].split("Who: ",1)[1]
        print(who)
        # store the message to remind
        what = list[3].split("What: ",1)[1]
        print(what)
        # store how often to remind
        remind = list[4].split("Remind: ",1)[1]
        print(remind)
        # cursor for database
        mycursor = db.cursor()
        # store into table for the future
        mycursor.execute("INSERT INTO reminders VALUES(NULL, %s, %s, %s, %s)",(when_str,who,what,remind))
        db.commit()

        # test code for querying for table data
        mycursor.execute("SELECT * FROM reminders")
        table = mycursor.fetchall()
        for rows in table:
            print(rows)
        mycursor.execute("SELECT date FROM reminders WHERE id")
        all_dates = mycursor.fetchall()

        print(all_dates[4])
        date_obj = datetime.strptime(when_str, "%m/%d/%y %H:%M")
        print(date_obj)

        # grab the user id for who set the reminder
        user = message.author.id
        # await message.channel.send(f"<@{user}> Reminder has been set. \n{content} ")
        await message.channel.send(f"<@{user}>\nWhen: {when_str}\nWho: {who}\nWhat: {what}\n")

# @tasks.loop(seconds=5)
# async def print():
#     print("Hello")
#     # channel = "<#839197220431331349>"
#     # await channel.send("hello")

print.start()

client.run(os.getenv("TOKEN"))
# start app
if __name__ == "__main__":
    app.run(debug=True)