from typing import Union
import urllib.request
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json


from pydantic import BaseModel
import requests
import config

from dotenv import load_dotenv
import openai
load_dotenv()

client = openai.OpenAI()

def get_response_from_gpt(message):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "딩신은 마케팅 전문가 입니다. 입련된 글을 바탕으로 가장 중요한 핵심 키워드 3개를 뽑아주세요.  키워드는 무조건 컴마로만 구분지어야만 해."},
            {"role": "user", "content": message}
        ]
    )
    return completion.choices[0].message.content
    


app = FastAPI()


# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처에서의 요청을 허용합니다.
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드를 허용합니다.
    allow_headers=["*"],  # 모든 헤더를 허용합니다.
)


@app.get("/blog")
def get_blog(query:str = "날씨"):
    client_id = "PKYNBnqsYbJ2MIqab4IJ"
    client_secret = "iBNCFSXoHH"
    encText = urllib.parse.quote(query, encoding='utf-8')
    viewCount = urllib.parse.quote("6")
    sort = urllib.parse.quote("sim")  # 관련도 순 정렬


    url = "https://openapi.naver.com/v1/search/news.json?query=" + encText + "&display=" + viewCount + "&sort=" + sort # JSON 결과
    # url = "https://openapi.naver.com/v1/search/news.xml?query=" + encText + "&display=" + viewCount # XML 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        response_body_str = response_body.decode('utf-8')
        json_body = json.loads(response_body_str)
        return json_body
    else:
        return "Error Code:" + rescode
    


# config.py에서 API 키와 URL을 가져옵니다.
API_KEY = config.WATSON_API_KEY
API_URL = config.WATSON_URL + '/v1/analyze?version=2021-08-01'

# Pydantic 모델을 사용하여 요청 데이터를 검증
class TextRequest(BaseModel):
    text: str

# 감성 분석 함수 정의
def analyze_sentiment(text: str):
    try:
        response = requests.post(
            API_URL,
            json={
                "text": text,
                "features": {
                    "sentiment": {}
                }
            },
            auth=('apikey', API_KEY),
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()  # 요청에 실패하면 예외 발생
        # print(response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print('Error analyzing sentiment:', e)
        return None

# 엔드포인트 정의
@app.post("/analyze")
def analyze(request: TextRequest):
    result = analyze_sentiment(request.text)
    # print(result)

    if result and 'sentiment' in result:
        sentiment = result['sentiment']['document']
        return sentiment
    else:
        raise HTTPException(status_code=500, detail="감성 분석 중 오류가 발생했습니다.")
    


@app.get("/blog2")
def get_blog(query: str = "날씨"):
    client_id = "PKYNBnqsYbJ2MIqab4IJ"
    client_secret = "iBNCFSXoHH"
    encText = urllib.parse.quote(query)
    viewCount = urllib.parse.quote("5")
    sort = urllib.parse.quote("sim")  # 관련도 순 정렬

    url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display={viewCount}&sort={sort}"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()




    
    if rescode == 200:
        response_body = response.read()
        response_body_str = response_body.decode('utf-8')
        json_body = json.loads(response_body_str)
        
        # 감정 분석 결과를 저장할 리스트
        sentiment_results = []

        # 각 뉴스 아이템의 description에 대해 감정 분석 수행
        for item in json_body.get('items', []):
            description = item.get('description', '')
            link = item.get('link', '')
            # score, _, label = analyze_sentiment(description)

            keyword = get_response_from_gpt(description)
            keywords = [k.strip() for k in keyword.split(',')]
            # print(f"Assistant: {response}")

            result = analyze_sentiment(description)
            # print(result)

            if result and 'sentiment' in result:
                sentiment = result['sentiment']['document']
                
            # print(sentiment)
            label = sentiment.get('label', '')
            if label is not None:
                sentiment_results.append({
                    "title": item.get('title'),
                    "description": description,
                    "link": link,
                    "label": label,
                    "keywords": keywords
                })
            else:
                raise HTTPException(status_code=500, detail="감성 분석 중 오류가 발생했습니다.")
        
        
        return {"items": sentiment_results}
    
    else:
        raise HTTPException(status_code=rescode, detail=f"Error Code: {rescode}")
    
#asst_tRFG5NR1pXfaDbH4ZjG9Nkpx