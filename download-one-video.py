import pandas as pd
from pandas import DataFrame
from sqlalchemy import text

from utils import get_conn, download_video, get_bv_from_url_info
from exAudio import process_audio_split
from speech2text import whisper_stt
from logger import logger


def bv_download(url: str) -> None:
    logger.info("Processing URL: %s", url)
    conn = get_conn()

    sql = text("SELECT * FROM tasks_to_do WHERE url = :url")
    exists = pd.read_sql(sql, con=conn.engine, params={"url": url})

    if len(exists) == 0:
        av = get_bv_from_url_info(url)
        task_data = {
            "url": url,
            "av": av,
            "status": 0,
            "video_path": None,
            "error_msg": None,
        }
        exists = DataFrame([task_data])

    if exists["status"][0] == 0:
        exists["status"][0] = 1
        exists.to_sql(
            "tasks_to_do", conn.engine, if_exists="replace", index=False
        )
        try:
            filepath = download_video(av, url)
        except Exception as e:
            logger.error("Download failed: %s", str(e))
            exists["error_msg"] = str(e)
            exists["status"][0] = 0
            exists.to_sql(
                "tasks_to_do", conn.engine, if_exists="replace", index=False
            )
            return
        exists["status"][0] = 2
        exists["video_path"] = filepath
        exists.to_sql(
            "tasks_to_do", conn.engine, if_exists="replace", index=False
        )
        logger.info("Task completed successfully")


if __name__ == "__main__":
    bv_download("https://www.bilibili.com/video/BV1vjCMBdEoj")
