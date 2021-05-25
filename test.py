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

print("test")
mycursor = db.cursor()
# mycursor.execute("SELECT * FROM reminders")
# table = mycursor.fetchall()
# for rows in table:
#     print(rows)
mycursor.execute("SELECT date FROM reminders")
now = datetime.now()
formatNow = now.strftime("%m/%d/%y %H:%M")
print(formatNow)
all_dates = mycursor.fetchall()
for i in range(len(all_dates)):
    all_datesStr = str(all_dates[i])
    date = all_datesStr.replace("(",'').replace(")",'').replace(",",'').replace("'","")
    # print(date)
    date_obj = datetime.strptime(date, "%m/%d/%y %H:%M")
    date_obj = date_obj.strftime("%m/%d/%y %H:%M")
    print(date_obj)
    print(formatNow)
    if formatNow == date_obj:
        print("It's time")
