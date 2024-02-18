import base64
import requests
from typing import List

def recog(target_img_base64: str, imgs_base64: List[str], url: str) -> List[int]:
    # リクエストのbodyを作成
    body = {
        "target": target_img_base64,
        "images": [img for img in imgs_base64]
    }
    # リクエストを送信
    res = requests.post(url, json=body)

    return res.json()

if __name__ == '__main__':
    # カレントディレクトリのkonami_testから画像を読み込んでbase64にエンコードする
    with open('konami_test/picture.png', 'rb') as f:
        img = f.read()
        target_img_base64 = base64.b64encode(img).decode('utf-8')
    # konami_testディレクトリ中のpicture_*.pngをimgs_base64に格納
    imgs_base64 = []
    for i in range(1, 6):
        with open(f'konami_test/picture_{i}.png', 'rb') as f:
            img = f.read()
            imgs_base64.append(base64.b64encode(img).decode('utf-8'))
    res = recog(target_img_base64, imgs_base64)
    print(res)