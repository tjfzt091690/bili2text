import os
from typing import Optional

from config import config
from logger import logger


class LLMService:
    def __init__(self):
        self._client = None
        self._provider = config.LLM_PROVIDER

    def _get_client(self):
        if self._client is not None:
            return self._client
        from openai import OpenAI
        self._client = OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_API_BASE,
        )
        return self._client

    def summarize(self, text: str, custom_prompt: Optional[str] = None) -> str:
        client = self._get_client()
        prompt = custom_prompt or "请对以下文本进行摘要，提取关键信息，保持简洁："
        full_prompt = f"{prompt}\n\n{text}"
        logger.info("LLM summarizing, input length: %d", len(text))
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=config.LLM_MAX_TOKENS,
            temperature=config.LLM_TEMPERATURE,
        )
        result = response.choices[0].message.content.strip()
        logger.info("LLM summary complete, output length: %d", len(result))
        return result

    def correct(self, text: str, custom_prompt: Optional[str] = None) -> str:
        client = self._get_client()
        prompt = custom_prompt or "请对以下语音转写文本进行纠错和润色，保持原意不变，修正明显的识别错误和标点问题："
        full_prompt = f"{prompt}\n\n{text}"
        logger.info("LLM correcting, input length: %d", len(text))
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=config.LLM_MAX_TOKENS,
            temperature=config.LLM_TEMPERATURE,
        )
        result = response.choices[0].message.content.strip()
        logger.info("LLM correction complete")
        return result

    def translate(self, text: str, target_lang: str = "English", custom_prompt: Optional[str] = None) -> str:
        client = self._get_client()
        prompt = custom_prompt or f"请将以下中文文本翻译成{target_lang}，保持专业性和准确性："
        full_prompt = f"{prompt}\n\n{text}"
        logger.info("LLM translating to %s", target_lang)
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=config.LLM_MAX_TOKENS,
            temperature=config.LLM_TEMPERATURE,
        )
        result = response.choices[0].message.content.strip()
        logger.info("LLM translation complete")
        return result

    def chat(self, text: str, system_prompt: str, user_prompt: Optional[str] = None) -> str:
        client = self._get_client()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt or f"请处理以下文本：\n\n{text}"},
        ]
        logger.info("LLM chat, system prompt length: %d", len(system_prompt))
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=messages,
            max_tokens=config.LLM_MAX_TOKENS,
            temperature=config.LLM_TEMPERATURE,
        )
        result = response.choices[0].message.content.strip()
        logger.info("LLM chat complete, output length: %d", len(result))
        return result


llm_service = LLMService()