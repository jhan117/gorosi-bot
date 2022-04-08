import requests
import discord
from bs4 import BeautifulSoup
from ast import literal_eval


# gosi url
url = "https://www.gosi.kr/uat/uia/gosiMain.do"

# env var
path = './env.txt'
f = open(path, 'r')
line = f.readline()
f.close()
env_dict = literal_eval(line)


# 각 리스트
def get_news_ul(id):
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")

    return soup.find(id=f"tab-content{id}")


# 공지사항
def get_news_notice():
    newsList = []

    ul = get_news_ul(1)

    infos = ul.select('b > a')
    dates = ul.find_all(class_='date')

    for i in range(len(infos)):
        newsList.append(dates[i].text + ' ' + infos[i].text)

    return newsList


# 새글
def get_new_news():
    newsList = []

    ul = get_news_ul(1)

    dates = ul.find_all(class_='date')

    newImg = ul.find_all('img')
    if newImg:
        for i in range(len(newImg)):
            infos = newImg[i].parent.find('a')
            newsList.append(dates[i].text + ' ' + infos.text)
    else:
        newsList.append("새 글이 없습니다.")

    return newsList


# 공채 7급 소식
def get_news7():
    newsList = []

    ul = get_news_ul(3)

    infos = ul.find_all('a')
    dates = ul.find_all(class_='date')

    for i in range(7):
        newsList.append(dates[i].text + ' ' + infos[i].text)

    return newsList


client = discord.Client()


@ client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


@ client.event
async def on_message(message):
    channel = client.get_channel(961515641699979285)

    if message.author == client.user:
        return

    if message.content.startswith('!공지'):
        newsList = get_news_notice()
        for news in newsList:
            await channel.send(news)

    if message.content.startswith('!새글'):
        newsList = get_new_news()
        for news in newsList:
            await channel.send(news)

    if message.content.startswith('!7급'):
        newsList = get_news7()
        for news in newsList:
            await channel.send(news)

client.run(env_dict["discord_token"])
