from PIL import Image, ImageEnhance, ImageFilter, ImageChops
from googletrans import Translator, constants

import pytesseract
import urllib.request
import requests
import shutil
from urllib.request import Request, urlopen
import pycountry

def OCR(imgURL, language):
    if language != "chinese":
        language = pycountry.languages.get(name=language)
        language = language.alpha_3     #convert full language name to 693-3 code for tesseract
    elif language == "chinese":
        language ='chi_tra'
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    imgURL, headers = urllib.request.urlretrieve(imgURL)
    # img = urllib.request.urlretrieve(img)
    img = Image.open(imgURL)
    # sharpen image to make characters clearer to read
    img = img.filter(ImageFilter.SHARPEN)
    # img.show()
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Billy\AppData\Local\Programs\Tesseract-OCR\tesseract'
    text = pytesseract.image_to_string(img, lang=language)  #Specify language to look after!
    return(text.replace('\n',' '))

def translate2(string, languageTo="en", languageFrom="auto"):
    # init the Google API translator
    translator = Translator()
    translation = translator.translate(string,languageTo,languageFrom)
    output = (f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
    return output