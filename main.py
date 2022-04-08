from dis import disco
import requests
import discord
from discord.ext import commands
import os
from bs4 import BeautifulSoup
from ast import literal_eval


# gosi url
url = "https://www.gosi.kr/uat/uia/gosiMain.do"


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
        newsList.append("새로운 글이 없습니다.")

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


bot = commands.Bot(command_prefix='!',
                   activity=discord.Game(name="시켜서"))


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='청소')
async def cleaner(ctx):
    if str(ctx.channel) == 'gosi':
        await ctx.channel.purge()
    else:
        await ctx.channel.send("여기 청소할 의무 없는데 제가 왜요?", delete_after=3)
        await ctx.message.delete(delay=3)


@bot.command(name='공지')
async def notice(ctx):
    if str(ctx.channel) == 'gosi':
        newsList = get_news_notice()
        for news in newsList:
            await ctx.channel.send(news)
    else:
        await ctx.channel.send("채널 이름도 읽지 않는 사람에겐 알려주기 싫어요", delete_after=3)
        await ctx.message.delete(delay=3)


@bot.command(name='새글')
async def new(ctx):
    if str(ctx.channel) == 'gosi':
        newsList = get_new_news()
        for news in newsList:
            await ctx.channel.send(news)
    else:
        await ctx.channel.send("채널 이름도 읽지 않는 사람에겐 알려주기 싫어요", delete_after=3)
        await ctx.message.delete(delay=3)


@bot.command(name='7급')
async def news7(ctx):
    if str(ctx.channel) == 'gosi':
        newsList = get_news7()
        for news in newsList:
            await ctx.channel.send(news)
    else:
        await ctx.channel.send("채널 이름도 읽지 않는 사람에겐 알려주기 싫어요", delete_after=3)
        await ctx.message.delete(delay=3)


bot.run(os.environ['TOKEN'])
