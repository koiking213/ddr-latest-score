import re
from bs4 import BeautifulSoup
from typing import List

class ScoreInfo:
    def __init__(self, title, difficulty, rank, score, date_played):
        self.title = title
        self.difficulty = difficulty
        self.rank = rank
        self.score = score
        self.date_played = date_played

    def __repr__(self):
        return f"SongInfo(title='{self.title}', difficulty='{self.difficulty}', rank='{self.rank}', score='{self.score}', date_played='{self.date_played}')"

def num_to_difficulty(num: int) -> str:
    if num == 0:
        return "bSP"
    elif num == 1:
        return "BSP"
    elif num == 2:
        return "DSP"
    elif num == 3:
        return "ESP"
    elif num == 4:
        return "CSP"
    elif num == 5:
        return "BDP"
    elif num == 6:
        return "DDP"
    elif num == 7:
        return "EDP"
    elif num == 8:
        return "CDP"
    
def parse_playdata(table_html: str) -> List[ScoreInfo]:
    pattern = r"_s_([a-zA-Z0-9_]+)\.png"

    table= BeautifulSoup(table_html, 'html.parser')
    songs_info = []

    for row in table.find_all('tr')[1:]:  # [1:] ヘッダを除外
        cols = row.find_all('td')

        title = cols[0].text.strip()
        chart_url = cols[0].find('a')['href']
        print("chart_url: ", chart_url)
        difficulty = num_to_difficulty(int(chart_url[-1]))
        rank_url = cols[2].find('img')['src'] # 例: "https://p.eagate.573.jp/game/ddr/ddra3/p/images/play_data/rank_s_aa_m.png"
        match = re.search(pattern, rank_url)
        if match:
            rank = match.group(1)
        else:
            rank = "Unknown"
        score = cols[3].text.strip()
        date_played = cols[4].text.strip()

        song_info = ScoreInfo(title, difficulty, rank, score, date_played)
        songs_info.append(song_info)
    return songs_info
