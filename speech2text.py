import os
from typing import Optional, Callable

import whisper

from config import config
from logger import logger


class WhisperSTT:
    def __init__(self):
        self._model = None
        self._model_name = None

    def is_cuda_available(self) -> bool:
        try:
            return whisper.torch.cuda.is_available()
        except Exception:
            return False

    def load_model(self, model_name: Optional[str] = None) -> None:
        if model_name is None:
            model_name = config.WHISPER_MODEL
        if self._model is not None and self._model_name == model_name:
            logger.info("Whisper model %s already loaded", model_name)
            return
        device = "cuda" if self.is_cuda_available() else "cpu"
        logger.info("Loading Whisper model %s on %s ...", model_name, device)
        self._model = whisper.load_model(model_name, device=device)
        self._model_name = model_name
        logger.info("Whisper model %s loaded", model_name)

    def run_analysis(
        self,
        filename: str,
        model: Optional[str] = None,
        prompt: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        if model is None:
            model = config.WHISPER_MODEL
        if prompt is None:
            prompt = config.WHISPER_DEFAULT_PROMPT
        self.load_model(model)
        slice_dir = os.path.join(config.AUDIO_SLICE_DIR, filename)
        if not os.path.isdir(slice_dir):
            raise FileNotFoundError(f"Slice directory not found: {slice_dir}")

        audio_files = sorted(
            os.listdir(slice_dir),
            key=lambda x: int(os.path.splitext(x)[0]),
        )
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(config.OUTPUT_DIR, f"{filename}.txt")
        logger.info("Starting transcription, %d slices total", len(audio_files))

        with open(output_path, "w", encoding="utf-8") as f:
            for idx, fn in enumerate(audio_files, 1):
                logger.info("Transcribing %d/%d: %s", idx, len(audio_files), fn)
                result = self._model.transcribe(
                    os.path.join(slice_dir, fn),
                    initial_prompt=prompt,
                )
                text = "".join(
                    seg["text"] for seg in result["segments"] if seg is not None
                )
                f.write(text)
                f.write("\n")
                if progress_callback:
                    progress_callback(idx, len(audio_files), text)

        logger.info("Transcription complete: %s", output_path)
        return output_path


whisper_stt = WhisperSTT()


def load_whisper(model: Optional[str] = None):
    whisper_stt.load_model(model)


def run_analysis(filename: str, model: Optional[str] = None, prompt: Optional[str] = None):
    return whisper_stt.run_analysis(filename, model, prompt)
