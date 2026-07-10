import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


class Config:
    BASE_DIR = Path(__file__).parent.resolve()

    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise EnvironmentError("DATABASE_URL is not set in .env")

    LOG_DIR = os.getenv("LOG_DIR")
    if not LOG_DIR:
        raise EnvironmentError("LOG_DIR is not set in .env")
    LOG_LEVEL = os.getenv("LOG_LEVEL")
    if not LOG_LEVEL:
        raise EnvironmentError("LOG_LEVEL is not set in .env")
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "0"))
    if LOG_MAX_BYTES == 0:
        raise EnvironmentError("LOG_MAX_BYTES is not set in .env")
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "0"))
    if LOG_BACKUP_COUNT == 0:
        raise EnvironmentError("LOG_BACKUP_COUNT is not set in .env")

    VIDEO_BASE_DIR = os.getenv("VIDEO_BASE_DIR")
    if not VIDEO_BASE_DIR:
        raise EnvironmentError("VIDEO_BASE_DIR is not set in .env")
    AUDIO_CONV_DIR = os.getenv("AUDIO_CONV_DIR")
    if not AUDIO_CONV_DIR:
        raise EnvironmentError("AUDIO_CONV_DIR is not set in .env")
    AUDIO_SLICE_DIR = os.getenv("AUDIO_SLICE_DIR")
    if not AUDIO_SLICE_DIR:
        raise EnvironmentError("AUDIO_SLICE_DIR is not set in .env")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR")
    if not OUTPUT_DIR:
        raise EnvironmentError("OUTPUT_DIR is not set in .env")

    SLICE_LENGTH_MS = int(os.getenv("SLICE_LENGTH_MS", "0"))
    if SLICE_LENGTH_MS == 0:
        raise EnvironmentError("SLICE_LENGTH_MS is not set in .env")
    AUDIO_CODEC = os.getenv("AUDIO_CODEC")
    if not AUDIO_CODEC:
        raise EnvironmentError("AUDIO_CODEC is not set in .env")
    WAV_SAMPLE_RATE = int(os.getenv("WAV_SAMPLE_RATE", "0"))
    if WAV_SAMPLE_RATE == 0:
        raise EnvironmentError("WAV_SAMPLE_RATE is not set in .env")
    WAV_CHANNELS = int(os.getenv("WAV_CHANNELS", "0"))
    if WAV_CHANNELS == 0:
        raise EnvironmentError("WAV_CHANNELS is not set in .env")

    WHISPER_MODEL = os.getenv("WHISPER_MODEL")
    if not WHISPER_MODEL:
        raise EnvironmentError("WHISPER_MODEL is not set in .env")
    WHISPER_DEFAULT_PROMPT = os.getenv("WHISPER_DEFAULT_PROMPT")
    if not WHISPER_DEFAULT_PROMPT:
        raise EnvironmentError("WHISPER_DEFAULT_PROMPT is not set in .env")

    PARAFORMER_MODEL = os.getenv("PARAFORMER_MODEL")
    if not PARAFORMER_MODEL:
        raise EnvironmentError("PARAFORMER_MODEL is not set in .env")
    PARAFORMER_MODEL_REVISION = os.getenv("PARAFORMER_MODEL_REVISION")
    if not PARAFORMER_MODEL_REVISION:
        raise EnvironmentError("PARAFORMER_MODEL_REVISION is not set in .env")

    XUNFEI_APPID = os.getenv("XUNFEI_APPID", "")
    XUNFEI_SECRET_KEY = os.getenv("XUNFEI_SECRET_KEY", "")
    XUNFEI_LFASR_HOST = os.getenv("XUNFEI_LFASR_HOST")
    if not XUNFEI_LFASR_HOST:
        raise EnvironmentError("XUNFEI_LFASR_HOST is not set in .env")
    XUNFEI_UPLOAD_DURATION = os.getenv("XUNFEI_UPLOAD_DURATION")
    if not XUNFEI_UPLOAD_DURATION:
        raise EnvironmentError("XUNFEI_UPLOAD_DURATION is not set in .env")
    XUNFEI_RESULT_TYPE = os.getenv("XUNFEI_RESULT_TYPE")
    if not XUNFEI_RESULT_TYPE:
        raise EnvironmentError("XUNFEI_RESULT_TYPE is not set in .env")
    XUNFEI_POLL_INTERVAL = int(os.getenv("XUNFEI_POLL_INTERVAL", "0"))
    if XUNFEI_POLL_INTERVAL == 0:
        raise EnvironmentError("XUNFEI_POLL_INTERVAL is not set in .env")

    LLM_PROVIDER = os.getenv("LLM_PROVIDER")
    if not LLM_PROVIDER:
        raise EnvironmentError("LLM_PROVIDER is not set in .env")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_API_BASE = os.getenv("LLM_API_BASE")
    if not LLM_API_BASE:
        raise EnvironmentError("LLM_API_BASE is not set in .env")
    LLM_MODEL = os.getenv("LLM_MODEL")
    if not LLM_MODEL:
        raise EnvironmentError("LLM_MODEL is not set in .env")
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "0"))
    if LLM_MAX_TOKENS == 0:
        raise EnvironmentError("LLM_MAX_TOKENS is not set in .env")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

    FLASK_HOST = os.getenv("FLASK_HOST")
    if not FLASK_HOST:
        raise EnvironmentError("FLASK_HOST is not set in .env")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "0"))
    if FLASK_PORT == 0:
        raise EnvironmentError("FLASK_PORT is not set in .env")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "").lower() == "true"
    FLASK_MAX_CONTENT_LENGTH = int(os.getenv("FLASK_MAX_CONTENT_LENGTH", "0"))
    if FLASK_MAX_CONTENT_LENGTH == 0:
        raise EnvironmentError("FLASK_MAX_CONTENT_LENGTH is not set in .env")


config = Config()