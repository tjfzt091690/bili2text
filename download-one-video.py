import pandas as pd
from pandas import DataFrame

from utils import get_conn,download_video,get_url,get_bv_from_url_info
from exAudio import *
from speech2text import *

# Main文件是作者用来测试的，请运行window.py

def bv_download(url):
    #av = input("请输入BV号：")
    print(url)
    conn = get_conn()
    sql = f"select * from tasks_to_do where url = '{url}'"
    print(sql)
    exists = pd.read_sql(sql, con = conn.engine)
    if len(exists) == 0:
        av = get_bv_from_url_info(url)
        dict = {
            'url':url,
            'av':av,
            'status':0,
            'video_path': None,
            'error_msg':None,
        }
        exists = DataFrame([dict])
    if exists['status'][0] == 0:
        exists['status'][0] = 1
        exists.to_sql('tasks_to_do', conn.engine, if_exists='replace', index=False)
        # 下载文件
        try:
            filepath = download_video(av, url)
        except Exception as e:
            print(e)
            exists['error_msg'] = str(e)
            exists['status'][0] = 0
            exists.to_sql('tasks_to_do', conn.engine, if_exists='replace', index=False)
            return
        exists['status'][0] = 2
        exists['video_path'] = filepath
        exists.to_sql('tasks_to_do', conn.engine, if_exists='replace', index=False)
if __name__ == "__main__":
    bv_download('https://www.bilibili.com/video/BV1vjCMBdEoj')