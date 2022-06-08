import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os
from twilio.rest import Client
import time
from dotenv import load_dotenv

# This file will be used to contain webscraping functions

def redflags():
    # website to be checked
    url = "https://forums.redflagdeals.com/hot-deals-f9/?sk=tt&rfd_sk=tt&sd=d"
    # browser settings
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    # getting the response from the website
    response = requests.get(url, headers=headers)
    # beautifulsoup to parse the html
    soup = BeautifulSoup(response.content, 'html.parser')
    target = soup.find_all("div", {"class": "inner"})
    # print(soup)
    print(target)