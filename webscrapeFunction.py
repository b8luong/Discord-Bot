import requests
from bs4 import BeautifulSoup
import time

# This file will be used to contain webscraping functions

# browser settings
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def redflagsPostings():
    start = time.time()
    # website to be checked
    url = "https://forums.redflagdeals.com/hot-deals-f9/?sk=tt&rfd_sk=tt&sd=d"
    # getting the response from the website
    response = requests.get(url, headers=headers)
    # print(response)
    # beautifulsoup to parse the html
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
    print(soup)
    # remove sticky (aka ad posts)
    for div in soup.find_all("li", {'class':'sticky'}):
        div.decompose()
    for div in soup.find_all("li", {'class':'deleted'}):
        div.decompose()
    target = soup.select('li.topic')
    # print(target)
    # ids = soup.select('div.thread_meta_large_primary')
    # select all <a> elements with class topic_title_link
    elements = soup.select('a.thread_title_link')
    # href still needs to be extracted from these elements which will be used as post identifiers
    ids = [element['href'] for element in elements]
    # print('ids: {}'.format(ids))
    # combining the root URL and the href to get a full link
    homeURL = "https://forums.redflagdeals.com"
    finalIds = [homeURL+id for id in ids]
    end = time.time()
    duration = end-start
    # print(finalIds)
    return finalIds, target

# function to return things that is necessary to create an embed
def redflagsEmbed(postings):
    # for post in postings:
    #     print(post)
    homeURL = "https://forums.redflagdeals.com"
    urlList = []
    titleList = []
    outputList = []
    print(postings)
    for i in range(len(postings)-1,-1,-1):
        postURL = postings[i].find(class_ = "thread_title_link")['href']
        fullURL = homeURL + postURL
        output = {}
        response = requests.get(fullURL, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
        print(soup)
        details = soup.find("dl", {'class':"post_offer_fields"})
        if details:
            dt = details.find_all("dt")
            dd = details.find_all("dd")
            for i in range(len(dt)):
                if i == 0 and dt[0].text == 'Deal Link:':
                    output[dt[i].text] = dd[0].find("a")["href"]
                else:
                    output[dt[i].text] = dd[i].text
        else:
            body = soup.find("div", {'class':"content"})
            firstATag = body.find('a')
            if firstATag:
                firstURL = firstATag['href']
            else:
                firstURL = "No Link"
            output["Deal Link:"] = firstURL
            output["Body:"] = body.text
        title = soup.find("h2", {'class': 'post_title first'}).text
        urlList.append(fullURL)
        titleList.append(title)
        outputList.append(output)
    # print(details)
    # print(fullURL)
    return urlList,titleList,outputList
    # return postings[0]