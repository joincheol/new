import os
import urllib.request
import json
import pandas as pd

client_id = "PKYNBnqsYbJ2MIqab4IJ"
client_secret = "iBNCFSXoHH"
encText = urllib.parse.quote("날씨")
viewCount = urllib.parse.quote("100")
sort = urllib.parse.quote("sim")  # 관련도 순 정렬

url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display={viewCount}&sort={sort}"

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)

response = urllib.request.urlopen(request)
rescode = response.getcode()

if rescode == 200:
    response_body = response.read()
    json_data = json.loads(response_body.decode('utf-8'))
    
    # JSON 데이터를 pandas DataFrame으로 변환
    items = json_data['items']
    df = pd.DataFrame(items)
    
    # DataFrame을 엑셀 파일로 저장
    df.to_excel("news_results.xlsx", index=False)
    print("엑셀 파일이 성공적으로 저장되었습니다.")
else:
    print("Error Code:" + str(rescode))
