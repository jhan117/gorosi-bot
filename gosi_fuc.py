import requests
import discord
from bs4 import BeautifulSoup

# gosi url
gosi_url = "https://www.gosi.kr/uat/uia/gosiMain.do"
# 고시 채널
gosi_channel = 961515641699979285
# 0, 6, 12, 18시
time_list = ["00:00:00", "06:00:00", "12:00:00", "18:00:00"]


# embed maker
def make_embed(newsList):
    embed = discord.Embed(
        title='사이버국가고시센터', url=gosi_url, color=0xFF0000)
    for value in newsList.values():
        embed.add_field(name=value[1], value=value[0], inline=False)
    return embed


# 각 리스트
def get_news_ul(id):
    html = requests.get(gosi_url)
    soup = BeautifulSoup(html.content, "html.parser")

    return soup.find(id=f"tab-content{id}")


# 공지사항
def get_news_notice():
    newsList = {}

    ul = get_news_ul(1)

    infos = ul.select('b > a')
    dates = ul.find_all(class_='date')

    for i in range(len(infos)):
        newsList[i] = [dates[i].text]
        newsList[i].append(infos[i].text)
    return newsList


# 새글
def get_new_news():
    newsList = {}

    ul = get_news_ul(1)

    dates = ul.find_all(class_='date')

    newImg = ul.find_all('img')
    if newImg:
        for i in range(len(newImg)):
            infos = newImg[i].parent.find('a')
            newsList[i] = [dates[i].text]
            newsList[i].append(infos.text)

    return newsList


# 공채 7급 소식
def get_news7(limit):
    try:
        newsList = {}

        ul = get_news_ul(3)

        infos = ul.find_all('a')
        dates = ul.find_all(class_='date')

        for i in range(int(limit)):
            newsList[i] = [dates[i].text]
            newsList[i].append(infos[i].text)

        return newsList
    except:
        return None


# get new post
def get_new():
    get_current_post = {}

    ul = get_news_ul(1)
    dates = ul.find_all(class_='date')
    newImg = ul.find_all('img')

    if newImg:
        for i in range(len(newImg)):
            infos = newImg[i].parent.find('a')
            get_current_post[i] = [dates[i].text]
            get_current_post[i].append(infos.text)

    return get_current_post
