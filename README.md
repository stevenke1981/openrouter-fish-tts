# OpenRouter Fish Audio TTS

Zero-dependency Python client and CLI for `fish-audio/s2.1-pro-free` through OpenRouter.

## Features

- Writes raw MP3/PCM response bytes directly to disk
- Provider-specific Fish voice IDs and reusable profiles
- Default young, bright, energetic Chinese Mandarin female voice
- Experimental Taiwan-Mandarin profile
- Fish S2 emotion/style markers
- Bounded exponential retries for transient failures
- Atomic `.part` output replacement
- No API key in source code or command-line arguments

## Setup

Set `OPENROUTER_API_KEY` in the environment:

```bash
export OPENROUTER_API_KEY=sk-or-...
python fish_tts.py "主人，這是 Fish Audio 測試。" -o outputs/test.mp3 --json
```

Windows PowerShell:

```powershell
$env:OPENROUTER_API_KEY = "sk-or-..."
python fish_tts.py "主人，這是 Fish Audio 測試。" -o outputs/test.mp3 --json
```

## Profiles

The default is `mainland_female_soft`:

```bash
python fish_tts.py "旁白文字" -o outputs/mainland.mp3
```

Other profiles:

```bash
python fish_tts.py "旁白文字" -o outputs/male.mp3 --profile mainland_mandarin
python fish_tts.py "旁白文字" -o outputs/taiwan.mp3 --profile taiwan_mandarin
```

| Profile | Voice ID | Description |
|---|---|---|
| `mainland_female_soft` | `fbe02f8306fc4d3d915e9871722a39d5` | Young, bright, energetic Chinese Mandarin female |
| `mainland_mandarin` | `7bbcf02c0398403fa3048aa9917c7a5f` | Measured, intellectual Mandarin male |
| `taiwan_mandarin` | `e855dc04a51f48549b484e41c4d4d4cc` | Taiwan-tagged Mandarin female experiment |

Use `--no-style-prefix` when the input already contains Fish bracket markers.

## Python API

```python
from fish_tts import FishTTSClient

result = FishTTSClient().synthesize(
    "旁白文字",
    "outputs/narration.mp3",
    voice="fbe02f8306fc4d3d915e9871722a39d5",
)
print(result.output_path, result.generation_id)
```

## Tests

```bash
python -m pytest -q
```

Tests use a local fake HTTP server and do not require an API key or incur charges.

## Documentation and data

- [`docs/model-api.md`](docs/model-api.md): API contract, profiles, markers, and limitations
- [`docs/data/fish-chinese-voice-candidates.md`](docs/data/fish-chinese-voice-candidates.md): shortlist of Chinese/narration voices
- [`docs/data/fish-chinese-voice-candidates.csv`](docs/data/fish-chinese-voice-candidates.csv): machine-readable shortlist
- [`docs/data/fish-public-voice-catalog.json`](docs/data/fish-public-voice-catalog.json): public catalog snapshot
- [`skill/SKILL.md`](skill/SKILL.md): installable Hermes skill content
- [`examples/audio/`](examples/audio/): audition samples generated during development

## License

MIT. Voice models and generated audio remain subject to their provider terms and applicable voice/likeness permissions. Only clone or publish voices with proper authorization.
