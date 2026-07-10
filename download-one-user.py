import asyncio
from bilibili_api import video

from logger import logger


async def get_video_info(bvid: str) -> dict:
    v = video.Video(bvid=bvid)
    info = await v.get_info()
    logger.info("Video info retrieved for %s", bvid)
    return info


if __name__ == "__main__":
    info = asyncio.run(get_video_info("BV1uv411q7Mv"))
    print(info)
