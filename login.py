import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from recog import recog

def login(driver: webdriver.Chrome, username: str, password: str, lambda_url: str):
    # ログインページに移動するボタンをクリック
    try:
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login"))
        )
        login_button.click()
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