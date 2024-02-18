from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
from login import login
from bs4 import BeautifulSoup
import time
import re

class SongInfo:
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
    
def parse_playdata(html_source: str):
    pattern = r"_s_([a-zA-Z0-9_]+)\.png"

    soup = BeautifulSoup(html_source, 'html.parser')
    table = soup.find('table', {'id': 'data_tbl'})
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

        song_info = SongInfo(title, difficulty, rank, score, date_played)
        songs_info.append(song_info)

    for song in songs_info:
        print(song)

def get_playdata(username: str, password: str, lambda_url: str, user_agent_path: str) -> str:
    # WebDriverのパスを指定
    driver_path = '/usr/local/bin/chromedriver'
    options = Options()
    options.add_argument(f"--user-data-dir={user_agent_path}")
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # スコアページを開く
    driver.get("https://p.eagate.573.jp/game/ddr/ddra3/p/playdata/music_recent.html")
    time.sleep(3)

    # ログインボタンを探す
    login_elements = driver.find_elements(By.ID, "login")
    if len(login_elements) > 0:
        login(driver, username, password, lambda_url)

        # 最新のプレイデータページに移動
        try:
            driver.get("https://p.eagate.573.jp/game/ddr/ddra3/p/playdata/music_recent.html")
        except Exception as e:
            print(f"最新のプレイデータページへの遷移に失敗しました: {e}")
            exit()

    source = driver.page_source
    driver.quit()
    return source

if __name__ == '__main__':
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    lambda_url = os.getenv("LAMBDA_URL")
    user_agent_path = os.getenv("USER_AGENT_PATH")

    source = get_playdata(username, password, lambda_url, user_agent_path)
    parse_playdata(source)
