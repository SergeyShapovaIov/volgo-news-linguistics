import asyncio
import datetime
import re
import time
import traceback

from pyppeteer import launch
from pymongo import MongoClient
import pymongo
from urllib.parse import quote_plus

async def main():


    client = pymongo.MongoClient(
        "mongodb+srv://mongo-root:passw0rd@cluster0.qkh3grh.mongodb.net/?retryWrites=true&w=majority")
    db = client.test
    coll = db['news']


    # print results
    print(db)
    # client = MongoClient('45.11.24.111', username='mongo-root', password='passw0rd', authSource='admin')
    # print(client)
    # db = client.news
    # data = db.data
    browser = await launch({'args': ['--no-sandbox', '--disable-setuid-sandbox', '--disable-infobars',  '--ignore-certifcate-errors-spki-list']})
    page = await browser.newPage()
    await page.setViewport({
        'width': 1200,
        'height': 800
    })
    page.setDefaultNavigationTimeout(60000)
    await page.goto('https://novostivolgograda.ru/news', {'waitUntil': 'domcontentloaded'})
    newsLinks = []
    titles = []
    texts = []
    dates = []
    countPage = 0
    index = 0
    while countPage < 1:
        await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
        countPage += 1
        time.sleep(1)

    #Формируем список ссылок
    newsLinksObjects = await page.querySelectorAll('.mb-8 a')
    for linkObject in newsLinksObjects:
        newsLinks.append('https://novostivolgograda.ru' + await page.evaluate('(element) => element.getAttribute("href")', linkObject))

    for link in newsLinks:

        await page.goto(link, {'waitUntil': 'domcontentloaded'})

        textObjects = await page.querySelectorAll('.Common_common__MfItd span')
        text = ''
        for textObject in textObjects:
           text += await page.evaluate('(element) => element.textContent', textObject) + ' '
        if(text == ''):
            textObjects = await page.querySelectorAll('.Common_common__MfItd p')
            for textObject in textObjects:
                text += await page.evaluate('(element) => element.textContent', textObject) + ' '
        texts.append(text)

        date = await page.evaluate('document.evaluate("//*[contains(@class, \'MatterTop_date\')]",document.body, null, XPathResult.STRING_TYPE, null).stringValue')
        if(date == ''):
            date = await page.evaluate('document.evaluate("//*[contains(@class, \'MatterTopNoImage_date\')]",document.body, null, XPathResult.STRING_TYPE, null).stringValue')
        dates.append(date)

        title = await page.evaluate('document.evaluate("//h1[contains(@class, \'MatterTop_title\')]",document.body, null, XPathResult.STRING_TYPE, null).stringValue')
        if(title == ''):
            title = await page.evaluate('document.evaluate("//h1[contains(@class, \'MatterTopNoImage_title\')]",document.body, null, XPathResult.STRING_TYPE, null).stringValue')
        titles.append(title)

        print(date)

    # path = await page.evaluate('(element) => element.getAttribute("href")', await page.querySelector('.left-block'))
    # newslink = "https://novostivolgograda.ru" + path
    # newsLinks.append(newslink)
    # titles.append(await page.evaluate('(element) => element.textContent', await page.querySelector('.left-block .title-text')))
    # for el in elements:
    #     path = await page.evaluate('(element) => element.getAttribute("href")', el)
    #     newslink = "https://novostivolgograda.ru" + path
    #     newsLinks.append(newslink)
    #     titles.append(await page.evaluate('(element) => element.textContent', await el.querySelector('.title-text')))
    # elements = await page.querySelectorAll('#other-matters-chosen .item')
    # for el in elements:
    #     path = await page.evaluate('(element) => element.getAttribute("href")', el)
    #     newslink = "https://novostivolgograda.ru" + path
    #     newsLinks.append(newslink)
    #     titles.append(await page.evaluate('(element) => element.textContent', await el.querySelector('.title-text')))
    # elements = await page.querySelectorAll('.mat-card-small')
    # for el in elements:
    #     path = await page.evaluate('(element) => element.getAttribute("href")', el)
    #     newslink = "https://novostivolgograda.ru" + path
    #     newsLinks.append(newslink)
    #     titles.append(await page.evaluate('(element) => element.textContent', await el.querySelector('.title')))
    # for el in newsLinks:
    #     await page.goto(el, {'waitUntil': 'domcontentloaded', 'timeout': 300000})
    #     elements = await page.querySelectorAll('.cm-par-medium')
    #     text = ""
    #     for elem in elements:
    #         text = text + await page.evaluate('(element) => element.textContent', elem)
    #     texts.append(text)
    #     date = re.search(r'[\d]*-[\d]*-[\d]+', el)
    #     dates.append(date.group())
    #     print(el)
    #     print(text)
    # await browser.close()
    for i in range(0, len(newsLinks)):
        coll.insert_one({"newsDate": dates[i], "newsName": titles[i], "newsLink": newsLinks[i] , "newsText" : texts[i]})
        # data.update({u'newsDate': dates[i], u'newsName': titles[i], u'newsLink': newsLinks[i], u'newsText': texts[i]}, { u'$setOnInsert': { u'newsDate': dates[i], u'newsName': titles[i], u'newsLink': newsLinks[i], u'newsText': texts[i], u'forAnalysis': True } }, **{ 'upsert': True })
        print(str(i) + "  update")

def run():
    try:
        print('парсинг начался')
        asyncio.get_event_loop().run_until_complete(main())
        print('парсинг закончен')
    except Exception:
        print(traceback.format_exc());
        print('Произошел казус')


run();