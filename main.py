import discord
from discord.ext import commands, tasks
import os

from datetime import datetime
import asyncio

from functions.gosi_fuc import *
from functions.weather_fuc import *

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


@bot.command(name='청소')
async def cleaner(ctx):
    await ctx.channel.purge()


# === gosi 채널용 ===
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


# 새글 3시간마다 알림 -> 코드 수정 해야 함
@tasks.loop(seconds=1)
async def test():
    if datetime.now().time().isoformat(timespec='seconds') in time_list:
        get_new_post = get_new()

        if get_new_post:
            new_embed = make_embed(get_new_post)
            await bot.get_channel(gosi_channel).send(embed=new_embed)


@bot.command(name='7급')
async def news7(ctx, limit):
    if str(ctx.channel) == 'gosi':
        newsList = get_news7(limit)
        if newsList:
            news7_embed = make_embed(newsList)
            await ctx.channel.send(embed=news7_embed)


# === weather 채널용 ===
@bot.command(name='날씨')
async def weather(ctx):
    if str(ctx.channel) == "weather":
        await ctx.channel.send(embed=make_weather_embed())


@bot.command(name='산책')
async def walk_a_dog(ctx):
    if str(ctx.channel) == "weather":
        weather_result = WalkADog().check_weather()
        dust_result = WalkADog().check_dust()
        wind_result = WalkADog().check_wind()

        if not weather_result:
            await ctx.channel.send(WalkADog().check_clothes())
        else:
            await ctx.channel.send(weather_result)
        if dust_result:
            await ctx.channel.send(dust_result)
        if wind_result:
            await ctx.channel.send(wind_result)


# 예보 확인 후 기상이 안 좋을 것 같으면 알려줌
@tasks.loop(seconds=1)
async def forecast():
    if 115000 <= convert_int_time(datetime.now()) <= 163000:
        forecast_message = get_forecast()
        if forecast_message:
            await bot.get_channel(walk_channel).send(forecast_message)


bot.run(os.environ['TOKEN'])
