from datetime import datetime, date
from pytz import timezone
import discord

from common_func import *

# 산책 채널
weather_channel = 977417914548359228


# 나갈 수 있는 날씨
weather_main_list = ['Clear', 'Clouds', 'Snow']
# 강수형태 코드 - 나갈 수 없는 날씨
# 없음(0), 비(1), 비/눈(2), 눈(3), 빗방울(5), 빗방울눈날림(6), 눈날림(7)
PTY_list = ["1", "2", "5", "6"]


class OpenWeatherMap:
    def __init__(self):
        self.response = request_get(weather_url, weather_params).json()

    def weather(self):
        return self.response["weather"][0]

    def main(self):
        return self.response["main"]

    def wind(self):
        return self.response["wind"]["speed"]


class WalkADog(OpenWeatherMap):
    def __init__(self):
        super().__init__()

        self.dust_api = request_get(dust_url, dust_params).json()["response"][
            "body"]["items"][0]["khaiGrade"]

    def check_clothes(self):
        feels_like = super().main()["feels_like"]

        if feels_like <= 5:
            clothes_message = f"체감 온도 {feels_like}, 패딩 추천합니다"
        elif feels_like <= 15:
            clothes_message = f"체감 온도 {feels_like}, 맨투맨이나 겉옷을 걸치는 걸 추천합니다"
        elif feels_like < 30:
            clothes_message = f"체감 온도 {feels_like}, 가볍게 긴팔 입는 걸 추천합니다"
        else:
            clothes_message = f"체감 온도 {feels_like}, 반팔 추천"

        return clothes_message

    def check_weather(self):
        weather = super().weather()

        if not weather["main"] in weather_main_list:
            return f'현재 {weather["description"]}입니다. 밖을 보고 나가든가 하세요.'

    def check_dust(self):
        print(f"값 : {self.dust_api}, 타입 : {type(self.dust_api)}")
        if self.dust_api >= '3':
            return f"미세먼지 개쩜"

    def check_wind(self):
        wind = super().wind()
        if wind >= 4:
            return f"풍속 {wind}입니다. 바람에 죽지 마세요."


# 기본 날씨 정보 임베드
def make_weather_embed():
    API = OpenWeatherMap()
    colors = AnsiColors()
    white = colors.white()

    # 내용물
    desc = f'{white}{API.weather()["description"]}'

    main = API.main()
    temp = f'{white}{main["temp"]}'
    temp_min = f'{colors.blue()}{main["temp_min"]}'
    temp_max = f'{colors.red()}{main["temp_max"]}'

    wind = f'{white}{API.wind()}'

    # 임베드
    embed = discord.Embed(title=f"{date.today(timezone('Asia/Seoul'))}의 날씨")

    embed.add_field(name="날씨", value=colors.template(desc), inline=False)
    embed.add_field(name="기온", value=colors.template(temp))
    embed.add_field(
        name="최저 기온", value=colors.template(temp_min))
    embed.add_field(
        name="최고 기온", value=colors.template(temp_max))
    embed.add_field(name="풍속", value=colors.template(wind), inline=False)

    embed.set_footer(text=datetime.now(
        timezone('Asia/Seoul')).replace(microsecond=0))

    return embed


# 예보 확인
def get_forecast():
    forecast_dict = {}
    forecast_message = ''
    current = datetime.now(timezone('Asia/Seoul'))

    base_date = convert_to_int("date", current)

    if current.minute < 30:
        base_time = str(current.hour - 1) + '30'
    else:
        base_time = str(convert_to_int("time", current))[:-2]

    forecast_params = {'serviceKey': forecast_key, 'numOfRows': '60', 'dataType': 'JSON',
                       'base_date': base_date, 'base_time': base_time, 'nx': forecast_nx, 'ny': forecast_ny}

    forecast_response = request_get(forecast_url, forecast_params).json()["response"][
        "body"]["items"]["item"]

    for item in forecast_response:
        if item["category"] == 'PTY':
            forecast_dict = item
            forecast_value = forecast_dict["fcstValue"]
            break

    if forecast_value in PTY_list:
        if forecast_value == '1':
            forecast_message == "비 올 것 같아요"
        elif forecast_value == '2':
            forecast_message == "비랑 눈이 같이 올 것 같아요"
        elif forecast_value == '5':
            forecast_message == "빗방울이 올 것 같 같아요"
        else:
            forecast_message == "빗방울눈날림이 올 것 같 같아요"

    return forecast_message
