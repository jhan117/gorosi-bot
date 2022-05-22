import requests
import os

# API 정보
# 사이버국가고시센터
gosi_url = "https://www.gosi.kr/uat/uia/gosiMain.do"

# OpenWeather
weather_url = "https://api.openweathermap.org/data/2.5/weather"
weather_key = os.environ['WEATHER']
weather_lat = "37.6378"
weather_lon = "126.6702"
weather_params = {'lat': weather_lat, 'lon': weather_lon,
                  'appid': weather_key, 'units': 'metric', 'lang': 'kr'}

# 기상청 단기예보 조회 서비스
forecast_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
forecast_key = os.environ['FORECAST']
forecast_nx = "55"
forecast_ny = "128"

# 한국환경공단 에어코리아 대기오염정보
dust_url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
dust_key = os.environ['DUST']
dust_params = {'serviceKey': dust_key,  'returnType': 'json',
               'numOfRows': '1', 'stationName': '사우동', 'dataTerm': 'DAILY'}


class AnsiColors:
    def template(self, contents):
        return f"```ansi\n{contents}\n```"

    def white(self):
        return f"\u001b[{0};{37}m"

    def red(self):
        return f"\u001b[{0};{31}m"

    def blue(self):
        return f"\u001b[{0};{34}m"


# URL, API 요청
def request_get(url, params=None):
    return requests.get(url, params=params)


# datetime to integer
def convert_to_int(format, datetime_date):
    if format == "date":
        return datetime_date.year * 10000 + datetime_date.month * 100 + datetime_date.day
    elif format == "time":
        return datetime_date.hour * 10000 + datetime_date.minute * 100 + datetime_date.second
