import ffmpeg
import os
from typing import Optional

from config import config
from logger import logger


def mp4_to_wav(
    mp4_path: str,
    wav_path: Optional[str] = None,
    sample_rate: Optional[int] = None,
    channels: Optional[int] = None,
) -> str:
    if sample_rate is None:
        sample_rate = config.WAV_SAMPLE_RATE
    if channels is None:
        channels = config.WAV_CHANNELS
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
    mp4_file = "./bilibili_video/BV1g8PfzkELG/test.mp4"
    mp4_to_wav(mp4_file)
