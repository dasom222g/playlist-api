from datetime import datetime
from app.model import (
    AddSongRequest,
    ChartResponse,
    PlaylistResponse,
    PlaylistSong,
    PlaylistSongDetail,
    Song,
    SongDetailResponse,
    UpdateSongRequest,
)
from fastapi import FastAPI, Query, HTTPException
import os
import json

# FastAPI 앱 생성
app = FastAPI(
    title="플레이리스트 API",
    description="멜론 TOP 100 차트 데이터를 제공하는 API",
    version="1.0.0",
)

# ======================= Song API =======================

chart_data: list[Song] = []  # 전역변수
playlist_data: list[PlaylistSong] = []


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
    }


@app.get("/songs", response_model=ChartResponse)
def get_all_songs():
    """
    전체 멜론 차트 조회
    """
    if not chart_data:
        return ChartResponse(total=0, songs=[])

    return ChartResponse(total=len(chart_data), songs=chart_data)


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


# ======================= Song API =======================

# ======================= Playlist API =======================


# READ - 플레이리스트 전체 조회
@app.get("/playlist", response_model=PlaylistResponse)
def get_playlist():
    """
    내 플레이리스트 전체 조회 (READ)

    - 플레이리스트에 담긴 모든 곡 조회
    - 추가된 시간 순으로 정렬
    """
    # 추가된 시간 순으로 정렬 (원본영향 x)
    sorted_playlist = sorted(playlist_data, key=lambda x: x.added_at)

    return PlaylistResponse(total=len(sorted_playlist), songs=sorted_playlist)


# CREATE - 플레이리스트에 곡 추가
@app.post("/playlist", response_model=PlaylistSongDetail)
def add_song_to_playlist(request: AddSongRequest):
    """
    플레이리스트에 곡 추가 (CREATE)

    - **rank**: 멜론 차트에서 추가할 곡의 순위
    - 멜론 차트 데이터에서 곡 정보를 가져와서 플레이리스트에 추가
    """
    # 멜론 차트에서 해당 ID의 곡 찾기
    chart_song = next((song for song in chart_data if song.id == request.id), None)

    if not chart_song:
        raise HTTPException(
            status_code=404,
            detail=f"멜론 차트 {request.id}에 해당하는 곡을 찾을 수 없습니다",
        )

    # 이미 플레이리스트에 있는 곡인지 확인
    existing_song = next(
        (song for song in playlist_data if song.id == request.id), None
    )
    if existing_song:
        return PlaylistSongDetail(
            success=False,
            message=f"'{chart_song.title}'은(는) 이미 플레이리스트에 있습니다",
        )

    # 새로운 플레이리스트 곡 생성
    new_playlist_song = PlaylistSong(
        **chart_song.dict(),  # Song의 모든 필드 언패킹
        added_at=datetime.now().isoformat(),
        comment=request.comment,
    )

    # 플레이리스트에 추가
    # appent와 같은 수정메소드는 전역변수 아니어도 데이터 수정가능 (재할당만 global)
    playlist_data.append(new_playlist_song)

    return PlaylistSongDetail(
        success=True,
        song=new_playlist_song,
        message=f"'{chart_song.title}'이(가) 플레이리스트에 추가되었습니다",
    )


# READ - 플레이리스트 특정 곡 조회
@app.get("/playlist/{id}", response_model=PlaylistSongDetail)
def get_playlist_song(id: int):
    """
    플레이리스트 특정 곡 조회 (READ)

    - **id**: 곡의 고유 ID
    """
    # ID로 곡 찾기
    playlist_song = next((song for song in playlist_data if song.id == id), None)

    if playlist_song:
        return PlaylistSongDetail(
            success=True, song=playlist_song, message=f"플레이리스트 곡 조회 성공"
        )
    else:
        return PlaylistSongDetail(
            success=False,
            song=None,
            message=f"플레이리스트에서 ID {id}에 해당하는 곡을 찾을 수 없습니다",
        )


# UPDATE - 플레이리스트 곡 정보 수정
@app.put("/playlist/{id}", response_model=PlaylistSongDetail)
def update_playlist_song(id: int, request: UpdateSongRequest):
    """
    플레이리스트 곡 정보 수정 (UPDATE)

    - **id**: 수정할 곡의 플레이리스트 ID
    - **request**: 수정할 정보 (title, artist, album 중 선택적으로)
    """
    # ID로 곡 찾기
    song_index = next(
        (i for i, song in enumerate(playlist_data) if song.id == id), None
    )

    if song_index is None:
        return PlaylistSongDetail(
            success=False,
            message=f"플레이리스트에서 ID {id}에 해당하는 곡을 찾을 수 없습니다",
        )

    # 기존 곡 정보 가져오기
    current_song = playlist_data[song_index]

    # 수정된 정보로 업데이트 (Pydantic copy로 comment만 수정)
    updated_song = current_song.copy(update={"comment": request.comment})

    # 플레이리스트에서 곡 정보 업데이트
    playlist_data[song_index] = updated_song

    return PlaylistSongDetail(
        success=True,
        song=updated_song,
        message=f"플레이리스트 곡 정보가 수정되었습니다",
    )


# DELETE - 플레이리스트에서 곡 삭제
@app.delete("/playlist/{id}", response_model=PlaylistSongDetail)
def delete_playlist_song(id: int):
    """
    플레이리스트에서 곡 삭제 (DELETE)

    - **id**: 삭제할 곡의 플레이리스트 ID
    """
    # ID로 곡 찾기
    song_to_delete = next((song for song in playlist_data if song.id == id), None)

    if not song_to_delete:
        return PlaylistSongDetail(
            success=False,
            message=f"플레이리스트에서 ID {id}에 해당하는 곡을 찾을 수 없습니다",
        )

    # 플레이리스트에서 곡 제거
    playlist_data.remove(song_to_delete)

    return PlaylistSongDetail(
        success=True,
        song=song_to_delete,
        message=f"'{song_to_delete.title}'이(가) 플레이리스트에서 삭제되었습니다. 총 플레이리스트 갯수: {len(playlist_data)}",
    )


# ======================= Playlist API =======================
