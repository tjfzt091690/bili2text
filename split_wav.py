import ffmpeg
import os
from typing import Optional

from config import config
from logger import logger


def mp4_to_wav(
    mp4_path: str,
    wav_path: Optional[str] = None,
    sample_rate: int = 16000,
    channels: int = 1,
) -> str:
    if not os.path.exists(mp4_path):
        raise FileNotFoundError(f"MP4 file not found: {mp4_path}")
    if wav_path is None:
        wav_path = os.path.splitext(mp4_path)[0] + ".wav"
    try:
        (
            ffmpeg.input(mp4_path)
            .output(
                wav_path,
                format="wav",
                ar=sample_rate,
                ac=channels,
                sample_fmt="s16",
            )
            .overwrite_output()
            .run(quiet=True)
        )
        logger.info("Audio extracted to: %s", wav_path)
        return wav_path
    except ffmpeg.Error as e:
        try:
            err_msg = e.stderr.decode("utf-8")
        except (UnicodeDecodeError, AttributeError):
            err_msg = str(e)
        raise RuntimeError(f"Extraction failed: {err_msg}") from e


if __name__ == "__main__":
    mp4_file = "./bilibili_video/BV1g8PfzkELG/【3月10日午】特朗普：对伊朗军事行动很快结束；伊朗摧毁以色列关键卫星中心，宣布打击美军乌代里直升机基地；俄罗斯文化大楼被以军摧毁；马克龙登上戴高乐航母.mp4"
    mp4_to_wav(mp4_file)
