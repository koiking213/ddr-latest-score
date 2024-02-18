# ddr-latest-score

## 下準備

### 自動画像選択

自動ログインのため、キャラクターを選択する部分を突破する必要がある。
以下のjsonをリクエストすると、imagesのうちtargetと同じキャラクターである画像のインデックス(0~4)を返すAPIを想定している。([実装例](https://github.com/koiking213/konami-character-recognizer))

```json
{
    "target": <base64化された画像>,
    "images": [
        <base64化された画像>,
        <base64化された画像>,
        <base64化された画像>,
        <base64化された画像>,
        <base64化された画像>,
    ]
}
```

### Notion DB

以下のプロパティを想定している。

```
曲名: ページ本体
難易度: セレクト (bsp, BSP, DSP, ESP, CSP, BDP, DDP, EDP, CDP)
スコア: 数値
日付: 日付
CLEARED: チェックボックス
```

## 使い方

.envに書く内容:

- USERNAME=e-amusementのログインID
- PASSWORD=e-amusementのパスワード
- LAMBDA_URL=画像選択APIのURL
- NOTION_TOKEN=NotionのDBに登録するためのtoken
- NOTION_DB_ID=NotionのDBのID
- USER_AGENT_PATH=ブラウザのユーザーエージェントのパス
    - `about:version` で調べられる

`poetry run python main.py` で、データの取得からNotion DBへの追加まで行う。

## 参考

[Notion API を使用してデータベースを操作する](https://zenn.dev/kou_pg_0131/articles/notion-api-usage)
