import os
import re
import subprocess
import glob  # 新增导入

from sqlalchemy import create_engine
def get_conn():
    return create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/bilibili")

def ensure_folders_exist(output_dir):
    if not os.path.exists("bilibili_video"):
        os.makedirs("bilibili_video")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

def get_url(bv_number):
    if not bv_number.startswith("BV"):
        bv_number = "BV" + bv_number
    video_url = f"https://www.bilibili.com/video/{bv_number}"
    return video_url

# https://www.bilibili.com/video/BV1vjCMBdEoj
def get_bv_from_url_info(url):
    return url.split("/")[-1][2:]

def download_video(bv_number, video_url):
    """
    使用you-get下载B站视频。
    参数:
        bv_number: 字符串形式的BV号（不含"BV"前缀）或完整BV号
    返回:
        文件路径
    """
    print("Downloading video %s..." % video_url)
    output_dir = f"bilibili_video/{bv_number}" # 下载视频到 bilibili_video/{bv_number} 目录
    ensure_folders_exist(output_dir)
    print(f"使用you-get下载视频: {video_url}")
    try:
        result = subprocess.run(["you-get", "-l", "-o", output_dir, video_url], capture_output=True, text=True)
        if result.returncode != 0:
            msg = result.stderr.decode("gbk")
            print("下载失败:", msg)
            raise Exception(msg)
        else:
            print(result.stdout.decode("gbk"))
            print(f"视频已成功下载到目录: {output_dir}")
            video_files = glob.glob(os.path.join(output_dir, "*.mp4"))
            if video_files:
                # 删除xml文件
                xml_files = glob.glob(os.path.join(output_dir, "*.xml"))
                for xml_file in xml_files:
                    os.remove(xml_file)
            else:
                print("video_files 为空")
                raise Exception("video_files 为空")
    except Exception as e:
        print("发生错误:", str(e))
        raise e
    return output_dir
