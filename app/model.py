from pydantic import BaseModel


# 차트 관련 모델들
class Song(BaseModel):
    """곡 정보 모델"""

    id: int
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


# 플레이리스트 관련 모델들
class PlaylistSong(Song):
    """플레이리스트 내 곡 정보"""

    comment: str  # 추가 설명
    added_at: str  # 추가된 시간


class PlaylistResponse(BaseModel):
    """플레이리스트 응답 모델"""

    total: int
    songs: list[PlaylistSong]


class PlaylistSongDetail(BaseModel):
    """플레이리스트 곡 상세 응답"""

    success: bool
    song: PlaylistSong | None = None
    message: str


class AddSongRequest(BaseModel):
    """곡 추가 요청 모델"""

    id: int  # 멜론 차트에서 가져올 곡의 ID
    comment: str = ""  # 사용자 코멘트


class UpdateSongRequest(BaseModel):
    """곡 정보 수정 요청 모델"""

    comment: str
