import base64
import hashlib
import hmac
import json
import os
import time
from typing import Optional

import requests
import urllib.parse

from config import config
from logger import logger

LFASR_HOST = "https://raasr.xfyun.cn/v2/api"
API_UPLOAD = "/upload"
API_GET_RESULT = "/getResult"


class XunfeiASR:
    def __init__(self, appid: Optional[str] = None, secret_key: Optional[str] = None):
        self.appid = appid or config.XUNFEI_APPID
        self.secret_key = secret_key or config.XUNFEI_SECRET_KEY

    def _get_signa(self, ts: str) -> str:
        m2 = hashlib.md5()
        m2.update((self.appid + ts).encode("utf-8"))
        md5 = m2.hexdigest()
        md5_bytes = bytes(md5, encoding="utf-8")
        signa = hmac.new(
            self.secret_key.encode("utf-8"), md5_bytes, hashlib.sha1
        ).digest()
        signa = base64.b64encode(signa)
        return str(signa, "utf-8")

    def upload(self, upload_file_path: str, ts: str, signa: str) -> dict:
        logger.info("Uploading file: %s", upload_file_path)
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)

        param_dict = {
            "appId": self.appid,
            "signa": signa,
            "ts": ts,
            "fileSize": file_len,
            "fileName": file_name,
            "duration": "200",
        }
        with open(upload_file_path, "rb") as f:
            data = f.read(file_len)

        response = requests.post(
            url=LFASR_HOST + API_UPLOAD + "?" + urllib.parse.urlencode(param_dict),
            headers={"Content-type": "application/json"},
            data=data,
        )
        result = json.loads(response.text)
        logger.info("Upload response: %s", result)
        return result

    def get_result(self, upload_file_path: str) -> dict:
        ts = str(int(time.time()))
        signa = self._get_signa(ts)

        uploadresp = self.upload(upload_file_path, ts, signa)
        order_id = uploadresp["content"]["orderId"]

        param_dict = {
            "appId": self.appid,
            "signa": signa,
            "ts": ts,
            "orderId": order_id,
            "resultType": "transfer,predict",
        }

        status = 3
        while status == 3:
            response = requests.post(
                url=LFASR_HOST + API_GET_RESULT + "?" + urllib.parse.urlencode(param_dict),
                headers={"Content-type": "application/json"},
            )
            result = json.loads(response.text)
            status = result["content"]["orderInfo"]["status"]
            logger.info("Xunfei ASR status: %d", status)
            if status == 4:
                break
            time.sleep(5)

        logger.info("Xunfei ASR result received")
        return result


def do_request(folder: str, filename: str) -> dict:
    api = XunfeiASR()
    file_path = os.path.join(config.AUDIO_SLICE_DIR, folder, filename)
    return api.get_result(file_path)


class RequestApi:
    def __init__(self, appid, secret_key, upload_file_path):
        self._asr = XunfeiASR(appid, secret_key)
        self.upload_file_path = upload_file_path

    def get_signa(self):
        ts = str(int(time.time()))
        return self._asr._get_signa(ts)

    def upload(self):
        ts = str(int(time.time()))
        signa = self._asr._get_signa(ts)
        return self._asr.upload(self.upload_file_path, ts, signa)

    def get_result(self):
        return self._asr.get_result(self.upload_file_path)


def doRequest(folder, filename):
    return do_request(folder, filename)
