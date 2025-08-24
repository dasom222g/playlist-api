from pydantic import BaseModel


class Song(BaseModel):
    """곡 정보 모델"""

    rank: int
    title: str
    artist: str
    album: str


class ChartResponse(BaseModel):
    """차트 응답 모델"""

    total: int
    songs: list[Song]


class SongDetailResponse(BaseModel):
    """곡 상세 정보 응답 모델"""

    success: bool
    song: Song | None  # Song타입 or None
    message: str
