from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
from recog import recog
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

def get_playdata() -> str:
    # ユーザ名とパスワードを.envファイルから読み込む
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    lambda_url = os.getenv("LAMBDA_URL")
    user_agent_path = os.getenv("USER_AGENT_PATH")

    # WebDriverのパスを指定
    driver_path = '/usr/local/bin/chromedriver'
    options = Options()
    options.add_argument(f"--user-data-dir={user_agent_path}")
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # ログインページを開く
    driver.get("https://p.eagate.573.jp/game/ddr/ddra3/p/playdata/music_recent.html")

    # ログインフォームを見つけて操作
    time.sleep(3)
    login_elements = driver.find_elements(By.ID, "login")
    if len(login_elements) > 0:

        # ログインページに移動するボタンをクリック
        try:
            login_elements[0].click()
            #login_button = WebDriverWait(driver, 10).until(
            #    EC.presence_of_element_located((By.ID, "login"))
            #)
            #login_button.click()
        except:
            print("ログインページへの遷移に失敗しました")
            exit()

        time.sleep(2)

        ### 画像認証を突破する
        # まずは探したい画像のデータを取得
        try:
            target_image_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "captcha-correct-picture"))
            )
            target_image_base64 = target_image_element.screenshot_as_base64
        except Exception as e:
            print(f"ターゲット画像の取得に失敗しました: {e}")
            exit()

        # 次に探す対象の画像のデータを取得
        try:
            images = []
            for i in range(5):
                image_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, f"captcha-test-picture-{i}"))
                )
                images.append(image_element.screenshot_as_base64)
        except Exception as e:
            print(f"選択画像の取得に失敗しました: {e}")
            exit()

        # 画像認識APIを呼び出す
        try:
            res = recog(target_image_base64, images, lambda_url)
            # debug
            print(res)
        except Exception as e:
            print(f"画像認識APIの呼び出しに失敗しました: {e}")
            exit()

        time.sleep(2)
        ## ユーザ名入力フィールドを見つける
        try:
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "login-form-id"))
            )
            if not username_input.get_attribute("value"):
                username_input.send_keys(username)
        except Exception as e:
            print(f"ユーザ名の入力に失敗しました: {e}")
            exit()

        # パスワード入力フィールドを見つける
        try:
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "login-form-password"))
            )
            password_input.send_keys(password)
        except Exception as e:
            print(f"パスワードの入力に失敗しました: {e}")
            exit()

        # 画像認識APIの結果を使って、画像をクリック
        try:
            for i in res:
                image_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, f"captcha-test-picture-{i}"))
                )
                image_element.click()
        except Exception as e:
            print(f"画像のクリックに失敗しました: {e}")
            exit()

        time.sleep(5)
        # ログインボタンをクリック
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "login-form-login-button-id"))
            )
            button.click()
        except Exception as e:
            print(f"ログインボタンのクリックに失敗しました: {e}")
            exit()

        time.sleep(5)

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
    source = get_playdata()
    parse_playdata(source)
