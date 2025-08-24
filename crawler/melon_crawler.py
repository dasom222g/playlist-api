import requests
from bs4 import BeautifulSoup
import json
import os


def crawl_melon_chart():
    """멜론 차트 TOP 100 크롤링 함수"""

    # 멜론 차트 URL
    url = "https://www.melon.com/chart/index.htm"

    # 브라우저 헤더 설정 (멜론은 User-Agent 체크함)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # 웹 페이지 요청
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTP 오류 체크

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(response.content, "lxml")

        # 차트 데이터 수집
        chart_data = []

        # 멜론 차트의 각 곡 정보를 담고 있는 tr 태그 선택
        song_rows = soup.select("tbody tr")

        for row in song_rows:
            try:
                # 순위 추출
                rank_tag = row.select_one(".rank")
                rank = rank_tag.text.strip()

                # 곡명 추출
                title_tag = row.select_one(".ellipsis.rank01 a")
                title = title_tag.text.strip() if title_tag else "정보 없음"

                # 아티스트 추출
                artist_tags = row.select(".ellipsis.rank02 > a")
                if artist_tags:
                    # 여러 아티스트가 있을 경우 쉼표로 연결
                    artists = [tag.text.strip() for tag in artist_tags]
                    artist = ", ".join(artists)
                else:
                    artist = "정보 없음"

                # 앨범명 추출
                album_tag = row.select_one(".ellipsis.rank03 a")
                album = album_tag.text.strip() if album_tag else "정보 없음"

                # 데이터 저장
                song_info = {
                    "rank": int(rank) if rank.isdigit() else 0,
                    "title": title,
                    "artist": artist,
                    "album": album,
                }

                chart_data.append(song_info)
                print(f"{rank}위: {title} - {album})")

            except Exception as e:
                print(f"곡 정보 추출 중 오류: {e}")
                continue

        return chart_data

    except requests.exceptions.RequestException as e:
        print(f"웹 페이지 요청 실패: {e}")
        return []
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        return []


def save_to_json(data, filename="melon_chart_top100.json"):
    """크롤링한 데이터를 JSON 파일로 저장"""
    # 현재 파일 위치
    current_dir = os.path.dirname(__file__)  # crawler 폴더
    # 프로젝트 루트
    project_root = os.path.dirname(current_dir)  # playlist-api 폴더
    # data 폴더 경로
    data_dir = os.path.join(project_root, "app", "data")

    # 폴더 생성
    os.makedirs(data_dir, exist_ok=True)

    # 파일 경로
    file_path = os.path.join(data_dir, filename)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON 파일 저장 완료: {filename}")
    except Exception as e:
        print(f"❌ JSON 파일 저장 실패: {e}")


if __name__ == "__main__":
    # 멜론 차트 크롤링
    melon_data = crawl_melon_chart()
    save_to_json(melon_data, filename="melon_chart_top100.json")
