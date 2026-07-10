from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from typing import Optional

from config import config
from logger import logger


class ParaformerSTT:
    def __init__(self):
        self._pipeline = None

    def load_model(self) -> None:
        if self._pipeline is not None:
            logger.info("Paraformer model already loaded")
            return
        logger.info("Loading Paraformer model ...")
        self._pipeline = pipeline(
            task=Tasks.auto_speech_recognition,
            model="iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
            model_revision="v2.0.4",
        )
        logger.info("Paraformer model loaded")

    def transcribe(self, wav_path: str) -> dict:
        self.load_model()
        logger.info("Transcribing: %s", wav_path)
        result = self._pipeline(wav_path)
        logger.info("Transcription complete")
        return result


paraformer_stt = ParaformerSTT()


if __name__ == "__main__":
    result = paraformer_stt.transcribe(
        "./bilibili_video/BV1g8PfzkELG/test.wav"
    )
    print(result)
