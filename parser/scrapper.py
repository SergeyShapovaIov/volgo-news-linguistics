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

    # Подключение к удаленной базе даных
    client = pymongo.MongoClient("mongodb+srv://mongo-root:passw0rd@cluster0.qkh3grh.mongodb.net/?retryWrites=true&w=majority")
    db = client.test
    coll = db['news']

    # Создание клиента браузера и дабавление конфигураций
    browser = await launch({'args': ['--no-sandbox', '--disable-setuid-sandbox', '--disable-infobars',  '--ignore-certifcate-errors-spki-list']})
    page = await browser.newPage()
    await page.setViewport({
        'width': 1200,
        'height': 800
    })
    page.setDefaultNavigationTimeout(60000)

    # Переход на страницу со списком всех новоостей
    await page.goto('https://novostivolgograda.ru/news', {'waitUntil': 'domcontentloaded'})

    # Объявление массивов для хранения данных
    newsLinks = []
    titles = []
    texts = []
    dates = []

    # Прогрузка всех компонентов, которые необходимо распарсиить
    countPage = 0
    while countPage < 1:
        await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
        countPage += 1
        time.sleep(1)

    #Формирование списка ссылок
    newsLinksObjects = await page.querySelectorAll('.mb-8 a')
    for linkObject in newsLinksObjects:
        newsLinks.append('https://novostivolgograda.ru' + await page.evaluate('(element) => element.getAttribute("href")', linkObject))

    # Сбор недостающей информации
    for link in newsLinks:

        # Перехлд на страницу с новостью
        await page.goto(link, {'waitUntil': 'domcontentloaded'})

        # Получение текста новости со страницы
        textObjects = await page.querySelectorAll('.Common_common__MfItd span')
        text = ''
        for textObject in textObjects:
           text += await page.evaluate('(element) => element.textContent', textObject) + ' '
        if(text == ''):
            textObjects = await page.querySelectorAll('.Common_common__MfItd p')
            for textObject in textObjects:
                text += await page.evaluate('(element) => element.textContent', textObject) + ' '
        texts.append(text)

        # Получение даты новости со страницы
        date = await page.evaluate('document.evaluate("//*[contains(@class, \'MatterTop_date\')]",document.body, null, XPathResult.STRING_TYPE, null).stringValue')
        if(date == ''):
            date = await page.evaluate('document.evaluate("//*[contains(@class, \'MatterTopNoImage_date\')]",document.body, null, XPathResult.STRING_TYPE, null).stringValue')
        dates.append(date)

        # Получение заголовка новости со страницы
        title = await page.evaluate('document.evaluate("//h1[contains(@class, \'MatterTop_title\')]",document.body, null, XPathResult.STRING_TYPE, null).stringValue')
        if(title == ''):
            title = await page.evaluate('document.evaluate("//h1[contains(@class, \'MatterTopNoImage_title\')]",document.body, null, XPathResult.STRING_TYPE, null).stringValue')
        titles.append(title)

    # Закрытие клиента браузера
    await browser.close()

    # Отправка всех данных на кластер MongoDB
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