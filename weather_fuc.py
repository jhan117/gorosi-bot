import requests
from datetime import datetime, date
import discord

# 산책 채널
walk_channel = 977417914548359228

# OpenWeatherMap, 기상청 단기예보 조회 서비스, 한국환경공단 에어코리아 대기오염정보
# API key
current_key = "1329228661497ea2e257686e2ff7cef5"
forecast_key = 'umso4gXSEBO4ctxQa9aUZtxV+0MTLfHuWdKnYGwC+e8F4BCDGaC01h6DZ6nL/3FkeV0ASk97hev+Qhgz9vjS3A=='
dust_key = "umso4gXSEBO4ctxQa9aUZtxV+0MTLfHuWdKnYGwC+e8F4BCDGaC01h6DZ6nL/3FkeV0ASk97hev+Qhgz9vjS3A=="

# URL
current_url = "https://api.openweathermap.org/data/2.5/weather"
forecast_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
dust_url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"

# 내 위치
lat = "37.6378"
lon = "126.6702"
nx = "55"
ny = "128"

# parmas
current_params = {'lat': lat, 'lon': lon,
                  'appid': current_key, 'units': 'metric', 'lang': 'kr'}
dust_params = {'serviceKey': dust_key,  'returnType': 'json',
               'numOfRows': '1', 'stationName': '사우동', 'dataTerm': 'DAILY'}


# 나갈 수 있는 날씨
weather_main_list = ['Clear', 'Clouds', 'Snow']
# 강수형태 코드 - 나갈 수 없는 날씨
# 없음(0), 비(1), 비/눈(2), 눈(3), 빗방울(5), 빗방울눈날림(6), 눈날림(7)
PTY_list = ["1", "2", "5", "6"]


def request_get(url, params):
    return requests.get(url, params=params).json()


class OpenWeatherMap:
    def __init__(self):
        self.response = request_get(current_url, current_params)

    def weather(self):
        return self.response["weather"][0]

    def main(self):
        return self.response["main"]

    def wind(self):
        return self.response["wind"]["speed"]


class AnsiColors:
    def template(self, contents):
        return f"```ansi\n{contents}\n```"

    def white(self):
        return f"\u001b[{0};{37}m"

    def red(self):
        return f"\u001b[{0};{31}m"

    def blue(self):
        return f"\u001b[{0};{34}m"


class WalkADog:
    def __init__(self):
        self.weather_api = OpenWeatherMap()
        self.dust_api = request_get(dust_url, dust_params)["response"][
            "body"]["items"][0]["khaiGrade"]

    def check_clothes(self):
        feels_like = self.weather_api.main()["feels_like"]

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
        weather = self.weather_api.weather()

        if not weather["main"] in weather_main_list:
            return f'현재 {weather["description"]}입니다. 밖을 보고 나가든가 하세요.'

    def check_dust(self):
        if self.dust_api >= '3':
            return f"미세먼지 개쩜"

    def check_wind(self):
        wind = self.weather_api.wind()
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
    embed = discord.Embed(title=f"{date.today()}의 날씨")

    embed.add_field(name="날씨", value=colors.template(desc), inline=False)
    embed.add_field(name="기온", value=colors.template(temp))
    embed.add_field(
        name="최저 기온", value=colors.template(temp_min))
    embed.add_field(
        name="최고 기온", value=colors.template(temp_max))
    embed.add_field(name="풍속", value=colors.template(wind), inline=False)

    embed.set_footer(text=datetime.now().replace(microsecond=0))

    return embed


def convert_int(datetime_date):
    return datetime_date.year * 10000 + datetime_date.month * 100 + datetime_date.day


def convert_int_time(datetime_date):
    return datetime_date.hour * 10000 + datetime_date.minute * 100 + datetime_date.second


def get_forecast():
    forecast_dict = {}
    forecast_message = ''
    base_date = convert_int(datetime.now())

    if datetime.now().minute < 30:
        base_time = str(datetime.now().hour - 1) + '30'
    else:
        base_time = str(convert_int_time(datetime.now()))[:-2]

    forecast_params = {'serviceKey': forecast_key, 'numOfRows': '60', 'dataType': 'JSON',
                       'base_date': base_date, 'base_time': 1530, 'nx': nx, 'ny': ny}

    forecast_response = request_get(forecast_url, forecast_params)["response"][
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
