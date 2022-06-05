from PIL import Image
import pytesseract
import urllib.request
import requests
import shutil
from urllib.request import Request, urlopen
import pycountry

def OCR(imgURL, language):
    language = pycountry.languages.get(name=language)
    language = language.alpha_3     #convert full language name to 693-3 code for tesseract
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    imgURL, headers = urllib.request.urlretrieve(imgURL)
    # img = urllib.request.urlretrieve(img)
    img = Image.open(imgURL)
    img.load()
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Billy\AppData\Local\Programs\Tesseract-OCR\tesseract'
    text = pytesseract.image_to_string(img, lang=language)  #Specify language to look after!
    return(text)
