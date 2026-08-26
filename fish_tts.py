"""OpenRouter Fish Audio S2.1 Pro Free text-to-speech client."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ENDPOINT = "https://openrouter.ai/api/v1/audio/speech"
MODEL = "fish-audio/s2.1-pro-free"
RETRYABLE_STATUS = {408, 409, 429, 500, 502, 503, 504}
VOICE_PROFILES = {
    "mainland_mandarin": {
        "voice": "7bbcf02c0398403fa3048aa9917c7a5f",
        "prefix": "[calm][measured][slow and thoughtful]",
        "description": "中國普通話；知性、沉穩、紀錄片／故事旁白",
    },
    "taiwan_mandarin": {
        "voice": "e855dc04a51f48549b484e41c4d4d4cc",
        "prefix": "[soft tone][gentle][calm][warm][slow and thoughtful]",
        "description": "台灣標記的普通話公開音色；溫柔、溫暖、慢速女聲實驗 profile",
    },
    "mainland_female_soft": {
        "voice": "fbe02f8306fc4d3d915e9871722a39d5",
        "prefix": "[bright][confident][energetic][clear][warm][natural and conversational]",
        "description": "中國普通話年輕女聲；明亮、陽光、有精神、清楚自然的故事旁白 profile",
    },
}


class FishTTSClientError(RuntimeError):
    """A user-facing TTS client error."""


@dataclass(frozen=True)
class SpeechResult:
    output_path: Path
    content_type: str
    generation_id: str | None
    attempts: int


class FishTTSClient:
    def __init__(self, api_key: str | None = None, *, endpoint: str = ENDPOINT,
                 timeout: float = 120.0, retries: int = 3, backoff: float = 1.0) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise FishTTSClientError("OPENROUTER_API_KEY is not set")
        self.endpoint = endpoint
        self.timeout = timeout
        self.retries = max(0, retries)
        self.backoff = max(0.0, backoff)

    def synthesize(self, text: str, output_path: str | Path, *, voice: str | None = None,
                   response_format: str = "mp3") -> SpeechResult:
        if not text.strip():
            raise FishTTSClientError("input text must not be empty")
        if response_format not in {"mp3", "pcm"}:
            raise FishTTSClientError("response_format must be mp3 or pcm")
        payload: dict[str, Any] = {"model": MODEL, "input": text, "response_format": response_format}
        if voice:
            payload["voice"] = voice
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 2):
            request = urllib.request.Request(
                self.endpoint, data=body,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    audio = response.read()
                    if not audio:
                        raise FishTTSClientError("OpenRouter returned an empty audio body")
                    tmp = destination.with_name(destination.name + ".part")
                    tmp.write_bytes(audio)
                    tmp.replace(destination)
                    return SpeechResult(destination, response.headers.get_content_type(),
                                        response.headers.get("X-Generation-Id"), attempt)
            except urllib.error.HTTPError as exc:
                raw = exc.read(4096).decode("utf-8", "replace")
                last_error = FishTTSClientError(f"OpenRouter HTTP {exc.code}: {raw}")
                if exc.code not in RETRYABLE_STATUS or attempt > self.retries:
                    raise last_error from exc
            except (urllib.error.URLError, TimeoutError, OSError, FishTTSClientError) as exc:
                last_error = exc
                if isinstance(exc, FishTTSClientError) and "empty audio" not in str(exc):
                    raise
                if attempt > self.retries:
                    raise FishTTSClientError(str(exc)) from exc
            if attempt <= self.retries:
                time.sleep(self.backoff * (2 ** (attempt - 1)))
        raise FishTTSClientError(str(last_error or "request failed"))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Synthesize speech with OpenRouter Fish Audio S2.1 Pro Free")
    p.add_argument("text", nargs="?", help="Text to synthesize; stdin is used when omitted")
    p.add_argument("-o", "--output", required=True, help="Output audio path")
    p.add_argument("--voice", help="Provider-specific Fish Audio voice ID")
    p.add_argument("--profile", choices=tuple(VOICE_PROFILES), default="mainland_female_soft",
                   help="Voice profile used when --voice is omitted")
    p.add_argument("--no-style-prefix", action="store_true",
                   help="Do not prepend the profile's Fish emotion/style markers")
    p.add_argument("--format", choices=("mp3", "pcm"), default="mp3", dest="response_format")
    p.add_argument("--timeout", type=float, default=120.0)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--json", action="store_true", dest="json_output")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    text = args.text if args.text is not None else sys.stdin.read()
    profile = VOICE_PROFILES[args.profile]
    voice = args.voice or profile["voice"]
    if not args.no_style_prefix and not text.lstrip().startswith("["):
        text = profile["prefix"] + "\n" + text
    try:
        result = FishTTSClient(timeout=args.timeout, retries=args.retries).synthesize(
            text, args.output, voice=voice, response_format=args.response_format)
    except FishTTSClientError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4 if "API_KEY" in str(exc) or "HTTP 401" in str(exc) else 5
    data = {"output": str(result.output_path), "content_type": result.content_type,
            "generation_id": result.generation_id, "attempts": result.attempts}
    print(json.dumps(data, ensure_ascii=False) if args.json_output else f"saved: {result.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
