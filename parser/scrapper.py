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
    client = pymongo.MongoClient(
        "mongodb+srv://mongo-root:passw0rd@cluster0.qkh3grh.mongodb.net/?retryWrites=true&w=majority")
    db = client.test

    # Создание клиента браузера и дабавление конфигураций
    browser = await launch({'args': ['--no-sandbox', '--disable-setuid-sandbox', '--disable-infobars',
                                     '--ignore-certifcate-errors-spki-list']})
    page = await browser.newPage()
    await page.setViewport({
        'width': 1200,
        'height': 800
    })
    page.setDefaultNavigationTimeout(60000)

    await parseNews(100, db, page)
    await parsePerson(db, page)
    await parseAttractions(db, page)

    await browser.close()


async def parseNews(countPage, database, page):
    # Create necessary collection
    collection = database['news']

    # Переход на страницу со списком всех новоостей
    await page.goto('https://novostivolgograda.ru/news', {'waitUntil': 'domcontentloaded'})

    # Объявление массива для хранения всем ссылок на новости
    newsLinks = []

    # Прогрузка всех компонентов, которые необходимо распарсиить
    for indexPage in range(0, countPage):
        await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
        time.sleep(1)

    # Формирование списка ссылок
    newsLinksObjects = await page.querySelectorAll('.mb-8 a')
    for linkObject in newsLinksObjects:
        newsLinks.append(
            'https://novostivolgograda.ru' + await page.evaluate('(element) => element.getAttribute("href")',
                                                                 linkObject))

    # Сбор недостающей информации и отправка данных в кластер
    for indexLink in range(0, len(newsLinks)):
        # Перехлд на страницу с новостью
        await page.goto(newsLinks[indexLink], {'waitUntil': 'domcontentloaded'})

        # Получение текста новости со страницы
        textObjects = await page.querySelectorAll('.Common_common__MfItd span')
        text = ''
        for textObject in textObjects:
            text += await page.evaluate('(element) => element.textContent', textObject) + ' '
        if (text == ''):
            textObjects = await page.querySelectorAll('.Common_common__MfItd p')
            for textObject in textObjects:
                text += await page.evaluate('(element) => element.textContent', textObject) + ' '

        # Получение даты новости со страницы
        date = await page.evaluate(
            'document.evaluate("//*[contains(@class, \'MatterTop_date\')]",document.body, null, XPathResult.STRING_TYPE, null).stringValue')
        if (date == ''):
            date = await page.evaluate(
                'document.evaluate("//*[contains(@class, \'MatterTopNoImage_date\')]",document.body, null, XPathResult.STRING_TYPE, null).stringValue')

        # Получение заголовка новости со страницы
        title = await page.evaluate(
            'document.evaluate("//h1[contains(@class, \'MatterTop_title\')]",document.body, null, XPathResult.STRING_TYPE, null).stringValue')
        if (title == ''):
            title = await page.evaluate(
                'document.evaluate("//h1[contains(@class, \'MatterTopNoImage_title\')]",document.body, null, XPathResult.STRING_TYPE, null).stringValue')

        collection.insert_one(
            {"newsDate": date, "newsName": title, "newsLink": newsLinks[indexLink], "newsText": text,
             "forAnalysis": True})

        print(str(indexLink) + " update, news date - " + str(date))


async def parseAttractions(db, page):
    # Определение необходимой коллекции
    collection = db['attractions']

    # Парсим сайты достопримичательностей
    await page.goto('https://avolgograd.com/sights?obl=vgg', {'waitUntil': 'domcontentloaded'})

    # Прокрутка страницы вниз и нажатие на кнопку
    await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
    time.sleep(1)
    await page.evaluate('document.getElementById(\'true-loadmore\').click()')
    time.sleep(1)

    # Получение всех объектов с именами достопримечательностей
    attractionsObjectsAll = await page.querySelectorAll('.ta-211 a')

    # Получение имени и отправка данных  в кластер
    for indexName in range(0, len(attractionsObjectsAll)):
        name = await page.evaluate('(element) => element.textContent', attractionsObjectsAll[indexName]);
        collection.insert_one({"attractionsNames": name})
        print(str(indexName) + "  update attraction")


async def parsePerson(db, page):
    # Парсим сайт персон
    collection = db['person']

    # Переход на страницу с персонами
    await page.goto('https://global-volgograd.ru/person', {'waitUntil': 'domcontentloaded'})

    # Получение ссылок всех страниц на которых расположены карточки с персонами
    pagesLinksObjects = await page.querySelectorAll('.pager-list .pager-item a')
    pagesLinks = ['https://global-volgograd.ru/person']
    for linkObject in pagesLinksObjects:
        link_string = await page.evaluate('(element) => element.getAttribute("href")', linkObject)
        pagesLinks.append('https://global-volgograd.ru' + link_string)

    for pageLink in pagesLinks:
        await page.goto(pageLink, {'waitUntil': 'domcontentloaded'})

        personObjects = await page.querySelectorAll('.person-text .title')

        for personObject in personObjects:
            personName = await page.evaluate('(element) => element.textContent', personObject)
            print(personName.strip())
            collection.insert_one({"personName": personName.strip()})


def run():
    try:
        print('парсинг начался')
        asyncio.get_event_loop().run_until_complete(main())
        print('парсинг закончен')
    except Exception:
        print(traceback.format_exc());
        print('Произошел казус')


run()
