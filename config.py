import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).parent.resolve()

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/bilibili",
    )

    LOG_DIR = os.getenv("LOG_DIR", "./log")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "10485760"))
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    VIDEO_BASE_DIR = os.getenv("VIDEO_BASE_DIR", "bilibili_video")
    AUDIO_CONV_DIR = os.getenv("AUDIO_CONV_DIR", "audio/conv")
    AUDIO_SLICE_DIR = os.getenv("AUDIO_SLICE_DIR", "audio/slice")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")

    SLICE_LENGTH_MS = int(os.getenv("SLICE_LENGTH_MS", "45000"))

    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")

    XUNFEI_APPID = os.getenv("XUNFEI_APPID", "")
    XUNFEI_SECRET_KEY = os.getenv("XUNFEI_SECRET_KEY", "")

    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"


config = Config()
