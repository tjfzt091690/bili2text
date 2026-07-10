import os
import subprocess
import time
from typing import Optional

from config import config
from logger import logger


def check_video_integrity(file_path: str) -> bool:
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", file_path, "-f", "null", "-"],
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.stderr:
        logger.warning("Video file may be corrupted: %s", file_path)
        logger.warning("FFmpeg error: %s", result.stderr)
        return False
    return True


def convert_video_to_mp3(
    name: str,
    target_name: Optional[str] = None,
    folder: Optional[str] = None,
) -> str:
    if folder is None:
        folder = config.VIDEO_BASE_DIR
    input_path = os.path.join(folder, f"{name}.mp4")
    if not os.path.exists(input_path):
        dir_path = os.path.join(folder, name)
        if os.path.isdir(dir_path):
            for file in os.listdir(dir_path):
                if file.endswith((".mp4", ".flv", ".mkv", ".avi")):
                    input_path = os.path.join(dir_path, file)
                    break
            else:
                raise FileNotFoundError(f"No video file found in: {dir_path}")
        else:
            raise FileNotFoundError(f"Video file not found: {input_path}")
    if not check_video_integrity(input_path):
        raise ValueError(f"Video file corrupted: {input_path}")

    import ffmpeg

    output_name = target_name if target_name else name
    os.makedirs(config.AUDIO_CONV_DIR, exist_ok=True)
    output_path = os.path.join(config.AUDIO_CONV_DIR, f"{output_name}.mp3")

    try:
        (
            ffmpeg.input(input_path)
            .output(output_path, format="mp3", acodec=config.AUDIO_CODEC)
            .overwrite_output()
            .run(quiet=True)
        )
        logger.info("Audio extracted to: %s", output_path)
    except Exception as e:
        logger.error("Failed to extract audio: %s", str(e))
        raise

    return output_path


def split_mp3(
    filename: str,
    folder_name: str,
    slice_length: Optional[int] = None,
    target_folder: Optional[str] = None,
) -> str:
    from pydub import AudioSegment

    if slice_length is None:
        slice_length = config.SLICE_LENGTH_MS
    if target_folder is None:
        target_folder = config.AUDIO_SLICE_DIR

    audio = AudioSegment.from_mp3(filename)
    total_slices = (len(audio) + slice_length - 1) // slice_length
    target_dir = os.path.join(target_folder, folder_name)
    os.makedirs(target_dir, exist_ok=True)
    for i in range(total_slices):
        start = i * slice_length
        end = start + slice_length
        slice_audio = audio[start:end]
        slice_path = os.path.join(target_dir, f"{i + 1}.mp3")
        slice_audio.export(slice_path, format="mp3")
        logger.info("Slice %d/%d saved: %s", i + 1, total_slices, slice_path)
    return target_dir


def process_audio_split(name: str) -> str:
    folder_name = time.strftime("%Y%m%d%H%M%S")
    conv_path = convert_video_to_mp3(name, target_name=folder_name)
    if not os.path.exists(conv_path):
        raise FileNotFoundError(f"Converted audio not found: {conv_path}")
    split_mp3(conv_path, folder_name)
    return folder_name
