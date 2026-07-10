import os
import re
import subprocess
import glob

from sqlalchemy import create_engine, text

from config import config
from logger import logger


def get_conn():
    return create_engine(config.DATABASE_URL)


def ensure_folders_exist(output_dir: str) -> None:
    os.makedirs(config.VIDEO_BASE_DIR, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.AUDIO_CONV_DIR, exist_ok=True)
    os.makedirs(config.AUDIO_SLICE_DIR, exist_ok=True)


def get_url(bv_number: str) -> str:
    if not bv_number.startswith("BV"):
        bv_number = "BV" + bv_number
    return f"https://www.bilibili.com/video/{bv_number}"


def get_bv_from_url_info(url: str) -> str:
    match = re.search(r"BV[\w]+", url)
    if match:
        return match.group(0)
    parts = url.rstrip("/").split("/")
    last_part = parts[-1]
    if last_part.startswith("BV"):
        return last_part
    return last_part[2:]


def download_video(bv_number: str, video_url: str) -> str:
    logger.info("Downloading video %s ...", video_url)
    output_dir = os.path.join(config.VIDEO_BASE_DIR, bv_number)
    ensure_folders_exist(output_dir)
    logger.info("Using you-get to download: %s", video_url)
    try:
        result = subprocess.run(
            ["you-get", "-l", "-o", output_dir, video_url],
            capture_output=True,
        )
        if result.returncode != 0:
            try:
                msg = result.stderr.decode("utf-8")
            except UnicodeDecodeError:
                msg = result.stderr.decode("gbk", errors="replace")
            logger.error("Download failed: %s", msg)
            raise Exception(msg)
        else:
            try:
                stdout_text = result.stdout.decode("utf-8")
            except UnicodeDecodeError:
                stdout_text = result.stdout.decode("gbk", errors="replace")
            logger.info(stdout_text)
            logger.info("Video downloaded to: %s", output_dir)
            video_files = glob.glob(os.path.join(output_dir, "*.mp4"))
            if video_files:
                xml_files = glob.glob(os.path.join(output_dir, "*.xml"))
                for xml_file in xml_files:
                    os.remove(xml_file)
            else:
                logger.error("No video files found in %s", output_dir)
                raise Exception("video_files is empty")
    except Exception as e:
        logger.error("Error downloading video: %s", str(e))
        raise
    return output_dir
