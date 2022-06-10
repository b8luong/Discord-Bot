from discord.ext.commands import bot
from dotenv import load_dotenv
from flask import Flask
import discord
from discord.ext import tasks, commands
from extFunction import OCR, translate2
from webscrapeFunction import redflagsEmbed, redflagsPostings
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

# # basic bot example
# client = discord.Client()

bot = commands.Bot(command_prefix='!')

# events for the bot to work
@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))   # 0 becomes client and user is how you get the username
    # check_time.start()

# function for whenever a message is sent
@bot.event
async def on_message(message):
    # if the message sender is the bot, return nothing
    if message.author == bot.user:
        return
    msg = message.content
    # !ocr command in here since bot commands do not work with images
    if msg.startswith("!ocr"):
        try:
            content = msg.split("!ocr",1)[1].strip()
            print(content)
            imgLink = message.attachments[0]
            language = content
            print(imgLink)
            print(language)
            await message.channel.send(OCR(str(imgLink),str(language)))
        except:
            await message.channel.send("Image not clear")
    try:
        await bot.process_commands(message)
    except:
        return

    # if msg.startswith("!setdate"):
    #     # split the message on the command word
    #     content = msg.split("!setdate",1)[1]
    #     print(content)
    #     list = content.split("\n")
    #     print(list)
    #
    #     # variable for the time and date
    #     when_str = list[1].split("When: ",1)[1]
    #     date_obj = dateutil.parser.parse(when_str)
    #     date_obj = date_obj.strftime("%m/%d/%Y %H:%M")
    #     print(date_obj)
    #
    #
    #     # variable to store the people to mention for the reminder
    #     who = list[2].split("Who: ",1)[1]
    #     print(who)
    #     # variable to store the message to remind
    #     what = list[3].split("What: ",1)[1]
    #     print(what)
    #     # variable store how often to remind
    #     remind = list[4].split("Remind: ",1)[1]
    #     print(remind)
    #     # cursor for database
    #     mycursor = db.cursor()
    #     # store into table for the future
    #     mycursor.execute("INSERT INTO reminders VALUES(NULL, %s, %s, %s, %s)",(str(date_obj),who,what,remind))
    #     db.commit()
    #
    #     # test code for querying for table data
    #     mycursor.execute("SELECT * FROM reminders")
    #     table = mycursor.fetchall()
    #     for rows in table:
    #         print(rows)
    #     mycursor.execute("SELECT date FROM reminders WHERE id")
    #     all_dates = mycursor.fetchall()
    #
    #     # grab the user id for who set the reminder
    #     user = message.author.id
    #     # await message.channel.send(f"<@{user}> Reminder has been set. \n{content} ")
    #     await message.channel.send(f"<@{user}>\nWhen: {when_str}\nWho: {who}\nWhat: {what}\n")

@bot.command()
async def embed(ctx):
    soupPostings = redflagsPostings()
    urls, titles, postings = redflagsEmbed(soupPostings)
    for i in range(len(postings)):
        description = ""
        url = urls[i]
        title = titles[i]
        posting = postings[i]
        for key in posting:
            if key == "Deal Link:":
                if len(posting[key]) > 50:
                    shortenedURL = posting[key][0:40] + "..." + posting[key][-10:]
                else:
                    shortenedURL = posting[key]
                description += "**{}** [{}]({})\n".format(key, shortenedURL, posting[key])
            else:
                description += "**{}** {}\n".format(key, posting[key])
        string = "http://www.amazon.ca/gp/redirect.html?ie=UTF8&location=https%3A%2F%2Fwww.amazon.ca%2FACCO-Fold-Back-Binder-1-25-Inch-Medium%2Fdp%2FB0035OQGA6%2F&tag=redflagdealsc-20&linkCode=ur2&camp=15121&creative=330641"
        string2 = string[0:40] + " ... " + string[-10:]
        embed=discord.Embed(title=title, url=url, description=description, color=0xFF5733)
        await ctx.send(embed=embed)

@bot.command()
#command is already implemented in on message so this is here to remove errors of calling a command not decorated
async def ocr(ctx,*args):
    return

# command usage: !eng [string]
@bot.command()
async def eng(ctx,*args):
    if len(args) == 0:
        await ctx.send("Purpose: Auto detect language and convert to english \n"
                       "If you want to convert to a different language that isn't english, use !translate\n\n"
                       "Command Usage: !eng [words you want to translate to english]")
    else:
        string = " ".join(args)
        translation = translate2(string)
        await ctx.send(translation)

# command usage: !translate [string], [translate from], [translate to]
@bot.command()
async def translate(ctx,*args):
    if len(args) == 0:
        await ctx.send("Purpose: Translate from one language to another (must specify which languages)\n\n"
                       "Command Usage: !translate [words you want to translate] [language you want to translate from] [language you want to translate to]")
    else:
        string = args[:-2]
        string = " ".join(string)
        destLang = args[-1]
        sourceLang = args[-2]
        translation = translate2(string,destLang,sourceLang)
        print(translation)
        await ctx.send(translation)

# checking every minute to see if its time to remind
# @tasks.loop(minutes=1)
# async def check_time():
#     channel = client.get_channel(839197220431331349)
#     # await channel.send("hello")
#     mycursor = db.cursor()
#     mycursor.execute("SELECT date FROM reminders")
#
#     # getting current date and time
#     now = datetime.now()
#     formatNow = now.strftime("%m/%d/%Y %H:%M")
#     print(formatNow)
#
#     # grabbing the dates from the database
#     allDates = mycursor.fetchall()
#     mycursor.execute("SELECT who FROM reminders")
#     allWho = mycursor.fetchall()
#     mycursor.execute("SELECT what FROM reminders")
#     allWhat = mycursor.fetchall()
#     for i in range(len(allDates)):
#         date = allDates[i][0]
#         print(date)
#         date_obj = datetime.strptime(date, "%m/%d/%Y %H:%M")
#         date_obj = date_obj.strftime("%m/%d/%Y %H:%M")
#         if formatNow == date_obj:
#             print("It's time")
#             await channel.send(f"<@{user}>\nWhen: placeholder\nWho: {allWho[i][0]}\nWhat: {allWhat[i][0]}\n")

bot.run(os.getenv("TOKEN"))
# start app
if __name__ == "__main__":
    app.run(debug=True)