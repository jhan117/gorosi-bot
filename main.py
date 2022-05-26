import discord
from discord.ext import commands, tasks
import os

from datetime import datetime
import asyncio

from common_func import *
from gosi_func import *
from weather_func import *

bot = commands.Bot(command_prefix='!',
                   activity=discord.Game(name="시켜서"))


# 9, 12, 18시
# 21(9), 3시
time_list = ['090000', '120000', '180000']


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print("======")

    while True:
        try:
            now_time = convert_to_int("time", datetime.now())

            # 지정된 시간에 실행
            if forecast.is_running() == True:
                if now_time > 123000:
                    forecast.stop()
            else:
                if 115000 <= now_time <= 123000:
                    forecast.start()

            # gosi 새 글 정해진 시간에 알림
            if str(now_time) in time_list:
                # 시간 테스트
                print(f'내가 입력한 시간{time_list}, 컴터 시간{str(now_time)}')
                new_list = GetPost().new()
                if new_list:
                    await bot.get_channel(gosi_channel).send(embed=make_gosi_embed(new_list))

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
        await ctx.channel.send(embed=make_gosi_embed(GetPost().notice()))


@bot.command(name='새글')
async def new(ctx):
    if str(ctx.channel) == 'gosi':
        new_list = GetPost().new()

        if new_list:
            await ctx.channel.send(embed=make_gosi_embed(new_list))
        else:
            await ctx.channel.send('새로운 글이 없습니다')


@bot.command(name='7급')
async def news7(ctx):
    if str(ctx.channel) == 'gosi':
        await ctx.channel.send(embed=make_gosi_embed(GetPost().grade_7()))


# === weather 채널용 ===
@bot.command(name='날씨')
async def weather(ctx):
    if str(ctx.channel) == "weather":
        await ctx.channel.send(embed=make_weather_embed())


@bot.command(name='산책')
async def walk_a_dog(ctx):
    if str(ctx.channel) == "weather":
        walk = WalkADog()
        weather_result = walk.check_weather()
        dust_result = walk.check_dust()
        wind_result = walk.check_wind()

        if not weather_result:
            await ctx.channel.send(walk.check_clothes())
        else:
            await ctx.channel.send(weather_result)
        if dust_result:
            await ctx.channel.send(dust_result)
        if wind_result:
            await ctx.channel.send(wind_result)


# 예보 확인 후 기상이 안 좋을 것 같으면 알려줌
@tasks.loop(seconds=1)
async def forecast():
    forecast_message = get_forecast()
    if forecast_message:
        await bot.get_channel(weather_channel).send(forecast_message)


bot.run(os.environ['TOKEN'])
