from parse import ScoreInfo
from notion_client import Client
from typing import List
from dotenv import load_dotenv
import os

def push_scores(score_info: List[ScoreInfo], token: str, db_id: str):
    notion = Client(auth=token)
    for score in score_info:
        cleared = score.rank != "e"
        # 全く同じ時刻の曲がすでにあるか調べる
        notion_query = notion.databases.query(
            **{
                "database_id": db_id,
                "filter": {
                    "property": "日付",
                    "date": {
                        "equals": f"{score.date_played}+09:00"  # タイムゾーンを合わせる
                    }
                }
            }
        )
        if len(notion_query["results"]) == 0:
            # なければ新規作成
            notion.pages.create(
                **{
                    "parent": {"database_id": db_id},
                    "properties": {
                        "曲名": {"title": [{"text": {"content": score.title}}]},
                        "難易度": {"select": {"name": score.chart_kind}},
                        "スコア": {"number": int(score.score)},
                        "日付": {
                            "date": {
                                "time_zone": "Asia/Tokyo",
                                "start": score.date_played}
                                },
                        "CLEARED": {"checkbox": cleared},
                    },
                }
            )

if __name__ == '__main__':
    load_dotenv()
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("NOTION_DB_ID")
    scores = [
        ScoreInfo("曲名1", "ESP", "s", 1000000, "2021-10-01 10:00:00"),
        ScoreInfo("曲名2", "ESP", "s", 1000000, "2021-10-01 12:00:00"),
    ]
    push_scores(scores, token, db_id)
