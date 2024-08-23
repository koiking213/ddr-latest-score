import re
from bs4 import BeautifulSoup
from typing import List

class ScoreInfo:
    def __init__(self, title, chart_kind, rank, score, date_played):
        self.title = title
        self.chart_kind = chart_kind
        self.rank = rank
        self.score = score
        self.date_played = date_played

    def __repr__(self):
        return f"SongInfo(title='{self.title}', difficulty='{self.chart_kind}', rank='{self.rank}', score='{self.score}', date_played='{self.date_played}')"

def concat_style_difficulty(style: str, difficulty: str) -> str:
    ret = ""
    if difficulty == "BEGINNER":
        ret = "b"
    elif difficulty == "BASIC":
        ret = "B"
    elif difficulty == "DIFFICULT":
        ret = "D"
    elif difficulty == "EXPERT":
        ret = "E"
    elif difficulty == "CHALLENGE":
        ret = "C"

    if style == "SINGLE":
        ret = ret + "SP"
    else:
        ret = ret + "DP"
    return ret

def parse_playdata(table_html: str) -> List[ScoreInfo]:
    pattern = r"_s_([a-zA-Z0-9_]+)\.png"

    table= BeautifulSoup(table_html, 'html.parser')
    songs_info = []

    for row in table.find_all('tr')[1:]:  # [1:] ヘッダを除外
        cols = row.find_all('td')

        title = cols[0].text.strip()
        chart_url = cols[0].find('a')['href']
        print("chart_url: ", chart_url)
        style = cols[1].find('div', class_='style').text.strip()
        difficulty = cols[1].find('div', class_='difficulty').text.strip()
        chart_kind = concat_style_difficulty(style, difficulty)
        rank_url = cols[2].find('img')['src'] # 例: "https://p.eagate.573.jp/game/ddr/ddra3/p/images/play_data/rank_s_aa_m.png"
        match = re.search(pattern, rank_url)
        if match:
            rank = match.group(1)
        else:
            rank = "Unknown"
        score = cols[3].text.strip()
        date_played = cols[4].text.strip()

        song_info = ScoreInfo(title, chart_kind, rank, score, date_played)
        songs_info.append(song_info)
    return songs_info
