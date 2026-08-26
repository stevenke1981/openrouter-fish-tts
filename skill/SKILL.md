---
name: openrouter-fish-tts
description: "Use for Fish Audio TTS through OpenRouter."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [tts, openrouter, fish-audio, audio]
    related_skills: [local-tts-generation, hermes-agent]
---

# OpenRouter Fish Audio TTS

## When to Use

Use this skill when主人 wants to generate narration or other speech with Fish Audio S2.1 Pro Free via OpenRouter, from Python, a CLI, or an existing audio pipeline.

## Overview

Use the reusable client at `C:/Users/steven/openrouter-fish-tts/fish_tts.py` to call OpenRouter's raw-audio Text-to-Speech endpoint with model `fish-audio/s2.1-pro-free`.

## Usage

1. Ensure `OPENROUTER_API_KEY` is available in the environment. Never put the key in source code, command arguments, logs, or generated metadata.
2. Generate MP3:
   ```bash
   python C:/Users/steven/openrouter-fish-tts/fish_tts.py "文字內容" -o C:/path/output.mp3 --json
   ```
3. Optional provider voice ID:
   ```bash
   python C:/Users/steven/openrouter-fish-tts/fish_tts.py "文字內容" -o C:/path/output.mp3 --voice VOICE_ID
   ```
4. For programmatic integration:
   ```python
   from fish_tts import FishTTSClient
   result = FishTTSClient().synthesize(text, output_path, voice=voice)
   ```

## Fish Audio model and voice catalog

- OpenRouter model: `fish-audio/s2.1-pro-free`.
- OpenRouter endpoint: `POST https://openrouter.ai/api/v1/audio/speech`.
- The OpenRouter `voice` field is provider-specific and expects a Fish voice/model ID.
- The documented sample ID `b347db033a6549378b48d00acb0d06cd` is not a reliable Chinese narration voice; do not use it for Mandarin/Taiwanese storytelling without listening first.
- Fish Audio's public model endpoint is `GET https://api.fish.audio/model?page_size=100&page_number=N`. The public catalog is window-limited; the current accessible window was 1,000 models.
- Current Chinese/narration candidate files:
  - `E:/liaozhai-jin-yong-rewrite/04-laoshan/tts-test/fish-public-voice-catalog.json`
  - `E:/liaozhai-jin-yong-rewrite/04-laoshan/tts-test/fish-chinese-voice-candidates.csv`
  - `E:/liaozhai-jin-yong-rewrite/04-laoshan/tts-test/fish-chinese-voice-candidates.md`
- Strong initial Chinese story-narration candidate: `6fc59d2b56cf402eb572934114c8d8aa` (male, middle-aged, narration, storytelling, clear, authoritative, Mandarin). Other candidates are recorded in the catalog; every voice must be auditioned because tags do not guarantee Taiwanese pronunciation or naturalness.
- `mainland_female_soft`: `fbe02f8306fc4d3d915e9871722a39d5`; Chinese Mandarin young female public model tagged soft, smooth, storytelling, and gentle. It is configured for a bright, sunny, energetic, clear narration with `[bright][confident][energetic][clear][warm][natural and conversational]`. Retroflex intensity is not directly controllable and must be auditioned.


## Emotion and delivery markers

Fish S2-family models support square-bracket control markers inside `input`; these are Fish syntax, not extra OpenRouter JSON fields. Examples:

```text
[calm][authoritative] 世人皆知華山論劍、少林七十二藝——非只刀劍一途。
[whispering] 夜深了……故事才正要開始。
[emphasis] 這一句，千萬記住。
```

Useful documented markers include `[happy]`, `[sad]`, `[angry]`, `[excited]`, `[calm]`, `[confident]`, `[scared]`, `[curious]`, `[determined]`, `[serious]`, `[whispering]`, `[soft tone]`, `[emphasis]`, `[break]`, and `[long-break]`. Natural-language bracket cues such as `[mysterious and slow]` may also work with S2. Put sentence-level cues near the sentence they control, use one primary emotion per sentence, and audition them because a provider may occasionally vocalize or ignore a marker.

Do not send unsupported JSON keys such as `emotion`, `style`, `speed`, or `pitch` through the OpenRouter TTS endpoint unless the routed API explicitly documents them. Use Fish bracket markers in `input`; use FFmpeg for post-generation speed/volume normalization when needed.

## Project profiles

The CLI now has explicit profiles. The default is `mainland_female_soft` (young, bright, energetic Chinese Mandarin female narration):

```bash
python C:/Users/steven/openrouter-fish-tts/fish_tts.py \
  "旁白文字" -o output.mp3
```

Use the older intellectual male profile explicitly when needed:

```bash
python C:/Users/steven/openrouter-fish-tts/fish_tts.py \
  "旁白文字" -o output.mp3 --profile mainland_mandarin
```

The experimental Taiwan-Mandarin profile is:

```bash
python C:/Users/steven/openrouter-fish-tts/fish_tts.py \
  "旁白文字" -o output.mp3 --profile taiwan_mandarin
```

Current profile voices:

- `mainland_female_soft` (default): `fbe02f8306fc4d3d915e9871722a39d5`; young, bright, energetic, clear Chinese Mandarin female narration.
- `mainland_mandarin`: `7bbcf02c0398403fa3048aa9917c7a5f`; measured, serious, professional Mandarin narration.
- `taiwan_mandarin` (experimental): `e855dc04a51f48549b484e41c4d4d4cc`; Fish public model tagged Taiwan female / Mandarin, now configured with `[soft tone][gentle][calm][warm][slow and thoughtful]`.

The CLI automatically prepends Fish S2 style markers for a profile. Use `--no-style-prefix` when the input already contains bracket markers. A profile is not a guarantee of regional accent; listen-test it before committing a production pipeline. For a stable Taiwan male voice, create a private model from authorized Taiwan-Mandarin reference audio and replace the experimental profile voice ID.


- Endpoint: `POST https://openrouter.ai/api/v1/audio/speech`.
- Required JSON: `model`, `input`; optional `voice`, `response_format` (`mp3` or `pcm`).
- Successful responses are raw audio bytes. Write the body directly; do not parse success responses as JSON.
- The client uses bounded exponential backoff for transient HTTP/network failures and atomically replaces `.part` output files.
- `401`/missing key is an authentication error; `429`, `5xx`, and network timeouts are retry candidates.
- Use short opt-in live tests only; unit tests use a local fake HTTP server and do not incur API charges.

## Verification checklist

- Run `python -m pytest -q` in the project folder.
- Run a short live generation when the key is configured.
- Confirm the output exists and is non-empty.
- Run `ffprobe -v error -show_entries format=duration:stream=codec_name,sample_rate,channels -of json output.mp3`.
- For Chinese narration, listen and optionally run ASR to check pronunciation and language drift.
