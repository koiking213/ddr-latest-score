from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
from login import login
import time
from parse import parse_playdata
import notion


def get_playdata(username: str, password: str, lambda_url: str, user_agent_path: str) -> str:
    driver_path = '/usr/local/bin/chromedriver'
    options = Options()
    options.add_argument(f"--user-data-dir={user_agent_path}")
    options.add_argument(f"--profile-directory={profile_dir}")
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # 最新のプレイデータページを開く
    driver.get("https://p.eagate.573.jp/game/ddr/ddrworld/playdata/music_recent.html")
    time.sleep(3)

    # ログインボタンを探す
    login_elements = driver.find_elements(By.ID, "login")
    if len(login_elements) > 0:
        login(driver, username, password, lambda_url)

        # 最新のプレイデータページに移動
        try:
            driver.get("https://p.eagate.573.jp/game/ddr/ddrworld/playdata/music_recent.html")
        except Exception as e:
            print(f"最新のプレイデータページへの遷移に失敗しました: {e}")
            exit()

    # 最新50件のテーブルを読み込み
    try:
        table_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "data_tbl"))
        )
    except Exception as e:
        print(f"プレイデータの取得に失敗しました: {e}")
        exit()


    source = table_element.get_attribute('outerHTML')
    driver.quit()
    return source

if __name__ == '__main__':
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    lambda_url = os.getenv("LAMBDA_URL")
    user_agent_path = os.getenv("USER_AGENT_PATH")
    profile_dir = os.getenv("PROFILE_DIR")
    notion_token = os.getenv("NOTION_TOKEN")
    notion_db_id = os.getenv("NOTION_DB_ID")

    table = get_playdata(username, password, lambda_url, user_agent_path)
    scores = parse_playdata(table)

    # debug
    for score in scores:
        print(score)

    notion.push_scores(scores, notion_token, notion_db_id)
