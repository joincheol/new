import os
import sys
import urllib.request
client_id = "PKYNBnqsYbJ2MIqab4IJ"
client_secret = "iBNCFSXoHH"
encText = urllib.parse.quote("날씨")
viewCount = urllib.parse.quote("3")

url = "https://openapi.naver.com/v1/search/news.json?query=" + encText + "&display=" + viewCount # JSON 결과
# url = "https://openapi.naver.com/v1/search/news.xml?query=" + encText + "&display=" + viewCount # XML 결과
request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
response = urllib.request.urlopen(request)
rescode = response.getcode()
if(rescode==200):
    response_body = response.read()
    print(response_body.decode('utf-8'))
else:
    print("Error Code:" + rescode)