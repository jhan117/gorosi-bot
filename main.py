import discord
from discord.ext import commands, tasks
import os
from datetime import datetime
import asyncio

from gosi_fuc import *
from weather_fuc import *

bot = commands.Bot(command_prefix='!',
                   activity=discord.Game(name="시켜서"))


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    test.start()

    while True:
        try:
            now_time = convert_int_time(datetime.now())

            if forecast.is_running() == True:
                if now_time > 123000:
                    forecast.stop()
            else:
                if 115000 <= now_time <= 123000:
                    forecast.start()
            await asyncio.sleep(1)
        except:
            print("on_ready has error")


# 새글 3시간마다 알림
@tasks.loop(seconds=1)
async def test():
    if datetime.now().time().isoformat(timespec='seconds') in time_list:
        get_new_post = get_new()

        if get_new_post:
            new_embed = make_embed(get_new_post)
            await bot.get_channel(gosi_channel).send(embed=new_embed)


@bot.command(name='청소')
async def cleaner(ctx):
    await ctx.channel.purge()


@bot.command(name='공지')
async def notice(ctx):
    if str(ctx.channel) == 'gosi':
        newsList = get_news_notice()
        notice_embed = make_embed(newsList)
        await ctx.channel.send(embed=notice_embed)


@bot.command(name='새글')
async def new(ctx):
    if str(ctx.channel) == 'gosi':
        newsList = get_new_news()
        if newsList:
            new_embed = make_embed(newsList)
            await ctx.channel.send(embed=new_embed)
        else:
            await ctx.channel.send('새로운 글이 없습니다')


@bot.command(name='7급')
async def news7(ctx, limit):
    if str(ctx.channel) == 'gosi':
        newsList = get_news7(limit)
        if newsList:
            news7_embed = make_embed(newsList)
            await ctx.channel.send(embed=news7_embed)


# === 기본 날씨 정보 ===
@bot.command(name='날씨')
async def weather(ctx):
    if str(ctx.channel) == "weather":
        await ctx.channel.send(embed=make_weather_embed())


# === 산책 날씨 정보 ===
@bot.command(name='산책')
async def walk_a_dog(ctx):
    if str(ctx.channel) == "weather":
        weather_result = WalkADog().check_weather()

        if not weather_result:
            await ctx.channel.send(WalkADog().check_clothes())
        else:
            await ctx.channel.send(weather_result)

        await ctx.channel.send(WalkADog().check_dust())
        await ctx.channel.send(WalkADog().check_wind())


# === 10분 간격으로 재 요청 30분까지 ===
@tasks.loop(seconds=1)
async def forecast():
    if 115000 <= convert_int_time(datetime.now()) <= 163000:
        forecast_message = get_forecast()
        if forecast_message:
            await bot.get_channel(walk_channel).send(forecast_message)


bot.run(os.environ['TOKEN'])
