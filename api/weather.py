from flask import json
import requests
import os
import datetime

def weather(nx, ny):
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    now = datetime.datetime.now()
    date = now - datetime.timedelta(days=1)
    params = {
                "ServiceKey" : os.getenv("WEATHER_KEY"),
                "base_date" : date.strftime("%Y%m%d"),
                "base_time" : 2300, 
                "nx" : nx,
                "ny" : ny,
                "numOfRows" : "300",
                "pageNo" : 1,
                "dataType" : "JSON",
        }
    response = requests.get(url, params=params)
    data = json.loads(response.text)
    item = data["response"]["body"]["items"]["item"]
    info = {}
    for i in item:
        if i["fcstTime"] == now.strftime("%H00") or i["fcstTime"] == "1500" or i["fcstTime"] == "0600":
            info.setdefault(i["category"], i["fcstValue"])
    date = now.strftime("%Y년 %m월 %d일의 서울시 광진구 날씨입니다")
    if info["SKY"] == "1":
        sky = "맑음"
    elif info["SKY"] == "3":
        sky = "구름 많음"
    elif info["SKY"] == "4":
        sky = "흐림"
    tmp = str(info["TMP"])+"℃"
    min = str(info["TMN"])+"℃"
    max = str(info["TMX"])+"℃"
    humid = str(info["REH"])+"%"
    pop = str(info["POP"])+"%"
    result = {"날짜":date, "날씨":sky, "현재 기온":tmp, "최고 기온":max, "최저 기온":min, "습도":humid, "강수 확률":pop}
    contents = result["날짜"] + "\n"
    contents += "날씨:" + result["날씨"] + "\n"
    contents += "현재 기온: " + result["현재 기온"] + "\n"
    contents += "최저 기온: " + result["최저 기온"] + "\n"
    contents += "최고 기온: " + result["최고 기온"] + "\n"
    contents += "습도: " + result["습도"] + "\n" 
    contents += "강수확률: " + result["강수 확률"]
    return contents

'''
- Base_time : 0200, 0500, 0800, 1100, 1400, 1700, 2000, 2300 (1일 8회)
POP	강수확률	%
REH	습도	%
SKY	하늘상태	코드값
TMP	1시간 기온	℃
TMN	일 최저기온	℃
TMX	일 최고기온	℃
하늘상태(SKY) 코드 : 맑음(1), 구름많음(3), 흐림(4)
'''