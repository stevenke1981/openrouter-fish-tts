# Fish Audio S2.1 Pro Free through OpenRouter

## Endpoint

`POST https://openrouter.ai/api/v1/audio/speech`

Model: `fish-audio/s2.1-pro-free`

Required request fields:

- `model`
- `input`

Optional fields:

- `voice`: provider-specific Fish Audio voice/model ID
- `response_format`: `mp3` or `pcm`

Successful responses are raw audio bytes. Save the response body directly; do not call `response.json()` on success.

## Profiles

| Profile | Voice ID | Purpose |
|---|---|---|
| `mainland_female_soft` (default) | `fbe02f8306fc4d3d915e9871722a39d5` | Young, bright, energetic Chinese Mandarin female narration |
| `mainland_mandarin` | `7bbcf02c0398403fa3048aa9917c7a5f` | Measured, intellectual Mandarin narration |
| `taiwan_mandarin` | `e855dc04a51f48549b484e41c4d4d4cc` | Taiwan-tagged Mandarin female experimental profile |

Regional accent and retroflex intensity are not guaranteed by catalog tags. Audition each voice before production. For a stable Taiwan male voice, use an authorized Taiwan-Mandarin reference recording to create a private Fish model.

## Fish S2 style markers

The client profiles prepend markers in `input`, such as:

- `[bright]`
- `[confident]`
- `[energetic]`
- `[clear]`
- `[warm]`
- `[natural and conversational]`
- `[soft tone]`
- `[gentle]`
- `[calm]`
- `[measured]`
- `[slow and thoughtful]`

These are provider text markers, not additional JSON fields. Do not send unsupported `emotion`, `style`, `pitch`, or `speed` keys through the OpenRouter endpoint.

## Public catalog

Fish Audio public models can be inspected with:

```text
GET https://api.fish.audio/model?page_size=100&page_number=N
```

The repository snapshot contains the 1,000-model public window collected during development and a 79-entry Chinese/narration candidate shortlist. Catalog tags are metadata, not a guarantee of pronunciation quality.
