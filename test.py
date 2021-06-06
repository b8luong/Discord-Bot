# THIS FILE IS USED TO DEVELOP FUNCTIONS TO BE USED IN MAIN

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
from threading import Timer
import dateutil.parser

# .env file
load_dotenv()

TOKEN = os.getenv("TOKEN")
app_id = os.getenv("APP_ID")
public_key = os.getenv("PUBLIC_KEY")
# mySql credentials
sqlHost = os.getenv("host")
sqlUser = os.getenv("user")
sqlPasswd = os.getenv("passwd")
sqlDatabase = os.getenv("database")

db = mysql.connector.connect(
    host=sqlHost,
    user=sqlUser,
    passwd=sqlPasswd,
    database=sqlDatabase,
    autocommit=True
)

mycursor = db.cursor()
mycursor.execute("SELECT date FROM reminders")
# grabbing the dates from the database
allDates = mycursor.fetchall()
mycursor.execute("SELECT who FROM reminders")
allWho = mycursor.fetchall()
mycursor.execute("SELECT what FROM reminders")
allWhat = mycursor.fetchall()
for i in range(len(allDates)):
    date = allDates[i][0]
    print(date)
    date_obj = datetime.strptime(date, "%m/%d/%Y %H:%M")
    date_obj = date_obj.strftime("%m/%d/%Y %H:%M")
    if date_obj == date_obj:
        print(allWhat[0])