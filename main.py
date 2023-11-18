import asyncio
import logging
import os
import re

import discord
import mysql.connector
from discord.ext import commands
from discord.ext.commands import bot
from dotenv import load_dotenv
from flask import Flask

from extFunction import OCR, translate2
from webscrapeFunction import redflagsEmbed, redflagsPostings

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

# default_channel to set a default channel to send messages
default_channel = int(os.getenv("CHANNEL_ID"))

# bot sends on_ready message sometimes when it's been online. need to only send when bot comes online for the first time
bot_status = False

# events for the bot to work
@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))   # 0 becomes client and user is how you get the username
    global bot_status
    if bot_status == False:
        bot_status = True
        channel = bot.get_channel(default_channel)
        if channel:
            await channel.send("Bot is back online and ready.")
    # await read_previous_messages(channel, 20)
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

async def read_previous_messages(channel, num_messages):
    # Retrieve the last 'num_messages' messages from the channel
    messages = await channel.history(limit=num_messages).flatten()

    # Process and print the retrieved messages
    for message in messages:
        print(f'{message.author}: {message.content}')
        if message.embeds:
            for embed in message.embeds:
                print(embed)
                # Access embed fields and attributes
                title = embed.title
                description = embed.description
                author = embed.author
                fields = embed.fields  # List of embed fields

                # Process the information from the embed as needed
            print(title, description, author, fields)
                # You can print or use this information in your code

            # Process the text content of the message if it's not an embed
        else:
            text_content = message.content
            # Process the text content as needed

# Example usage of the read_previous_messages function
@bot.command(name='example_command')
async def example_command(ctx):
    await read_previous_messages(ctx.channel, 20)  # Replace 10 with the number of messages you want to retrieve


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

# a variable to track if a command like !rfd is already running due to while True loop:
command_status = False

@bot.command()
async def rfd(ctx):
    ids = [0]
    global command_status
    # if command is already running, don't run again
    if command_status == True:
        await ctx.send("Command is already running")
        return
    else:
        command_status = True
        while True:
            try:
                ids2, soupPostings = redflagsPostings()
                # comparing posts to see where the lastest post of ids is in ids2 to see which posts are old so we don't parse them again
                oldPost = 0
                if ids != ids2:
                    print("There was a change")
                    for i in range(len(ids)):
                        for j in range(len(ids2)):
                            if ids[i] == ids2[j]:
                                oldPost = j
                                break
                        # if we went through all the ids, just send the last 5 posts
                            elif ids2[-1] == ids2[j] and ids[-1] == ids[i] and ids[0] != ids2[j]:
                                oldPost = 5
                        # once we find a matching post, break out of outer loop
                        if oldPost != 0:
                            break
                    # keep track of where the latest old post in the new postings list
                    print(oldPost)
                    # returning only the new posts
                    soupPostings = soupPostings[0:oldPost]
                    urls, titles, postings = redflagsEmbed(soupPostings)
                    print("postings made it here (if error occurred)")
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
                                # making the url start with www instead of https:// as discord hyperlink shortcut does not
                                # work with https://
                                shortenedURL = re.sub(r'https?://', '', shortenedURL)
                                description += "**{}** [{}]({})\n".format(key, shortenedURL, posting[key])
                            else:
                                description += "**{}** {}\n".format(key, posting[key])
                        string = "http://www.amazon.ca/gp/redirect.html?ie=UTF8&location=https%3A%2F%2Fwww.amazon.ca%2FACCO-Fold-Back-Binder-1-25-Inch-Medium%2Fdp%2FB0035OQGA6%2F&tag=redflagdealsc-20&linkCode=ur2&camp=15121&creative=330641"
                        string2 = string[0:40] + " ... " + string[-10:]
                        embed=discord.Embed(title=title, url=url, description=description, color=0xFF5733)
                        await ctx.send(embed=embed)
                ids = ids2
                print("End of command")
                await asyncio.sleep(120)
            except Exception as e:
                print("error")
                print(e)
                await ctx.send("There was an error")
                await asyncio.sleep(120)


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