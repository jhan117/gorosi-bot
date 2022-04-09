from numpy import isin
import requests
import discord
from discord.ext import commands
import os
from bs4 import BeautifulSoup


# gosi url
gosi_url = "https://www.gosi.kr/uat/uia/gosiMain.do"


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


bot = commands.Bot(command_prefix='!',
                   activity=discord.Game(name="시켜서"))


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        message = '? 똑바로 쓴 거 맞아요?'
    else:
        message = '오류 떴네요 근데 뭔 오류인지 모르겠어요 ㅋㅋ ㅎㅎ ㅈㅅ'

    await ctx.send(message, delete_after=3)
    await ctx.message.delete(delay=3)


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
        notice_embed = make_embed(newsList)
        await ctx.channel.send(embed=notice_embed)
    else:
        await ctx.channel.send("채널 이름도 읽지 않는 사람에겐 알려주기 싫어요", delete_after=3)
        await ctx.message.delete(delay=3)


@bot.command(name='새글')
async def new(ctx):
    if str(ctx.channel) == 'gosi':
        newsList = get_new_news()
        if newsList:
            new_embed = make_embed(newsList)
            await ctx.channel.send(embed=new_embed)
        else:
            await ctx.channel.send('새로운 글이 없습니다')
    else:
        await ctx.channel.send("채널 이름도 읽지 않는 사람에겐 알려주기 싫어요", delete_after=3)
        await ctx.message.delete(delay=3)


@bot.command(name='7급')
async def news7(ctx, limit):
    if str(ctx.channel) == 'gosi':
        newsList = get_news7(limit)
        if newsList:
            news7_embed = make_embed(newsList)
            await ctx.channel.send(embed=news7_embed)
        else:
            await ctx.channel.send("7개만 쓰라고 했어요 안했어요", delete_after=3)
            await ctx.message.delete(delay=3)
    else:
        await ctx.channel.send("채널 이름도 읽지 않는 사람에겐 알려주기 싫어요", delete_after=3)
        await ctx.message.delete(delay=3)


@news7.error
async def news7_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingRequiredArgument):
        message = "하... 뒤에 숫자 제대로 쓰라고 했어요 안했어요"
    else:
        message = '오류 떴네요 근데 뭔 오류인지 모르겠어요 ㅋㅋ ㅎㅎ ㅈㅅ'

    await ctx.send(message, delete_after=3)
    await ctx.message.delete(delay=3)


bot.run(os.environ['TOKEN'])
