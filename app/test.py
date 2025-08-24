from app.model import Song
from fastapi import FastAPI
from typing import List, Optional
import json
import os

# FastAPI 앱 생성
app = FastAPI(
    title="플레이리스트 API",
    description="멜론 TOP 100 차트 데이터를 제공하는 API",
    version="1.0.0",
)

# 전역 변수로 차트 데이터 저장
chart_data: list[Song] = []


def load_chart_data():
    """멜론 차트 데이터 로드"""
    global chart_data
    try:
        # JSON 파일 경로
        data_path = os.path.join(
            os.path.dirname(__file__), "data", "melon_chart_top100.json"
        )

        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Song 모델로 변환
        # **song: 딕셔너리 언패킹
        # Song(rank=1, title="Seven", album="Seven")과 같음
        chart_data = [Song(**song) for song in data]
        print(f"✅ 멜론 차트 데이터 로드 완료: {len(chart_data)}곡")

    except FileNotFoundError:
        print("❌ 멜론 차트 데이터 파일을 찾을 수 없습니다.")
        chart_data = []
    except Exception as e:
        print(f"❌ 데이터 로드 중 오류: {e}")
        chart_data = []


# 앱 시작시 데이터 로드
@app.on_event("startup")
def startup_event():
    load_chart_data()


@app.get("/")
def root():
    """API 기본 정보"""
    return {
        "message": "🎵 플레이리스트 API에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "loaded_songs": len(chart_data),
    }
