from app.model import ChartResponse, Song, SongDetailResponse
from fastapi import FastAPI, Query, HTTPException
import os
import json

# FastAPI 앱 생성
app = FastAPI(
    title="플레이리스트 API",
    description="멜론 TOP 100 차트 데이터를 제공하는 API",
    version="1.0.0",
)

chart_data: list[Song] = []  # 전역변수


def load_chart_data():
    """멜론 차트 데이터 로드하고 반환"""
    try:
        data_path = os.path.join(
            os.path.dirname(__file__), "data", "melon_chart_top100.json"
        )

        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # **song: 딕셔너리 언패킹
        # Song(rank=1, title="Seven", album="Seven")과 같음
        songs: list[Song] = [Song(**song) for song in data]
        print(f"✅ 멜론 차트 데이터 로드 완료: {len(songs)}곡")
        return songs  # 데이터 반환

    except FileNotFoundError:
        print("❌ 멜론 차트 데이터 파일을 찾을 수 없습니다.")
        return []
    except Exception as e:
        print(f"❌ 데이터 로드 중 오류: {e}")
        return []


# 앱 시작시 데이터 로드
@app.on_event("startup")
async def startup_event():
    # 전역변수의 값을 재할당하기 위해서 global필요
    global chart_data
    chart_data = load_chart_data()  # 반환값을 전역변수에 할당


# @app.get("/")
# def test():
#     """API 상태 확인용 기본 엔드포인트"""
#     return {"message": "Hello FastAPI"}


@app.get("/")
async def root():
    """API 기본 정보"""
    return {
        "message": "🎵 플레이리스트 API에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "loaded_songs": len(chart_data),
        "endpoints": [
            "/songs - 전체 차트 조회",
            "/songs/{rank} - 특정 순위 곡 조회",
            "/songs/search?artist=아티스트명 - 아티스트 검색",
        ],
    }


@app.get("/songs", response_model=ChartResponse)
def get_all_songs():
    """
    전체 멜론 차트 조회
    """
    if not chart_data:
        return ChartResponse(total=0, songs=[])

    return ChartResponse(total=len(chart_data), songs=chart_data)


@app.get("/songs/{rank}", response_model=SongDetailResponse)
def get_song_by_rank(rank: int):
    """
    특정 순위의 곡 정보 조회

    - **rank**: 조회할 순위 (1-100)
    """
    # 순위 유효성 검사
    if rank < 1 or rank > 100:
        return SongDetailResponse(
            success=False, message=f"순위는 1-100 사이여야 합니다. 입력값: {rank}"
        )

    if not chart_data:
        raise HTTPException(status_code=404, detail="차트 데이터가 없습니다")

    # 순위에 해당하는 곡 찾기
    # next(...) - 조건에 맞는 아이템 중 첫 번째 곡 가져오기
    # None - 못 찾으면 None 반환
    song = next((s for s in chart_data if s.rank == rank), None)

    if song:
        return SongDetailResponse(
            success=True, song=song, message=f"{rank}위 곡 정보 조회 성공"
        )
    else:
        return SongDetailResponse(
            success=False, message=f"{rank}위에 해당하는 곡을 찾을 수 없습니다"
        )


@app.get("/songs/search", response_model=ChartResponse)
def search_songs_by_artist(
    artist: str = Query(description="검색할 아티스트명"),
):
    """
    아티스트명으로 곡 검색

    - **artist**: 검색할 아티스트명
    """
    if not chart_data:
        raise HTTPException(status_code=404, detail="차트 데이터가 없습니다")

    # 아티스트명으로 검색 (부분 일치)
    matched_songs = [
        song for song in chart_data if artist.lower() in song.artist.lower()
    ]

    return ChartResponse(total=len(matched_songs), songs=matched_songs)
