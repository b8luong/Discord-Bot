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
    global channel
    if bot_status == False:
        bot_status = True
        channel = bot.get_channel(default_channel)
        if channel:
            await channel.send("Bot is back online and ready.")
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
    links = list()
    # Process and print the retrieved messages
    for message in messages:
        if message.embeds:
            for embed in message.embeds:
                # Access embed fields and attributes
                description = embed.description
                # Not needed but kept for future use if needed
                title = embed.title
                author = embed.author
                fields = embed.fields
                link = re.search(r"\*\*RFD Link: \*\*\s*(https?://[^\s]+)", description)
                if link is not None:
                    links.append(link.group(1))
            # print(title, description, author, fields)
    return links

# WORK IN PROGRESS COMMAND TO CREATE SPECIFIC ALERTS
@bot.command()
async def test(ctx):
    msgs = await ctx.channel.history().flatten()
    for msg in msgs:
        if bot.user in msg.mentions:
            print(f"{msg.author}{msg.content}")
            print("I was mentioned here")

# a variable to track if a command like !rfd is already running due to while True loop:
command_status = False

# a stop command for when the bot goes into an error loop or stops sending messages
@bot.command()
async def stop(ctx):
    global command_status
    command_status = False
    await ctx.send("Bot will restart the command loop after stopping.")

@bot.command()
async def rfd(ctx):
    # read previous messages to look for previous postings so there is no duplicate postings sent
    ids = await read_previous_messages(ctx.channel, 50)
    # a variable to track if a command like !rfd is already running due to while True loop:
    global command_status
    # if command is already running, don't run again
    if command_status == True:
        await ctx.send("Command is already running")
        return
    else:
        # set flag to true so command only runs once at all times
        command_status = True
        while True:
            # command_status can be set to false by calling !restart
            if command_status == False:
                print("broken")
                break
            else:
                try:
                    # grabbing all postings from the page (still needs to be parsed)
                    ids2, soupPostings = redflagsPostings()
                    # comparing posts to see where the lastest post of ids is in ids2 to see which posts are old so we don't parse them again
                    oldPost = False
                    if ids != ids2:
                        # Use case for when command is first ran and there was no previous messages
                        if ids == []:
                            oldPost = len(ids2)
                        else:
                            # print("There was a change")
                            for i in range(len(ids)):
                                for j in range(len(ids2)):
                                    # print(ids2)
                                    # homeURL = "https://forums.redflagdeals.com"
                                    # postURL1 = ids2[j]
                                    # print(homeURL + postURL1)
                                    if ids[i] == ids2[j]:
                                        oldPost = j
                                        # print(j)
                                        break
                                # if we went through all the ids, just send all new posts for the page
                                    elif ids2[-1] == ids2[j] and ids[-1] == ids[i] and ids[0] != ids2[j]:
                                        oldPost = j
                                        # print("sending all posts")
                                # once we find a matching post, break out of outer loop
                                if oldPost != False:
                                    break
                        # returning only the new posts
                        soupPostings = soupPostings[0:oldPost]
                        # print(soupPostings)
                        urls, titles, postings = redflagsEmbed(soupPostings)
                        # print(urls, titles, postings)
                        for i in range(len(postings)):
                            description = ""
                            url = urls[i]
                            title = titles[i]
                            posting = postings[i]
                            # Adding an identifier of RFD link to each post
                            description += "**{}** {}\n".format("RFD Link: ", url)
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
                    print("Done")
                    await asyncio.sleep(120)
                except Exception as e:
                    print("error")
                    print(e)
                    await ctx.author.send(e)
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