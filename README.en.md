# Static Meme to GIF

Turn one static reaction image into a short looping GIF with coherent motion.

[中文](README.md) · [Skill instructions](SKILL.md) · [Examples](examples/README.md)

This repository contains an agent skill for Codex and compatible assistants, plus standalone Python helpers. **An image tool creates the motion frames; the scripts split sheets, assemble GIFs, and compress them.** No image model, hosted service, or API credentials are included.

## Real examples

Each output below contains 12 frames in a 2-second infinite loop at 240×240.

| Example | Source | GIF |
| --- | --- | --- |
| Allow everything: sway and lift a foot | <img src="examples/allow-everything/source.png" width="160" alt="Allow everything source"> | <img src="examples/allow-everything/small.gif" width="240" alt="Allow everything GIF"> |
| Bring it on: wind up, punch, recover | <img src="examples/bring-it-on/source.png" width="160" alt="Bring it on source"> | <img src="examples/bring-it-on/small.gif" width="240" alt="Bring it on GIF"> |
| Direction matters: look and point | <img src="examples/direction-matters/source.png" width="160" alt="Direction matters source"> | <img src="examples/direction-matters/small.gif" width="240" alt="Direction matters GIF"> |
| Party creature: bounce, wave, extend the party blower | <img src="examples/party-creature/source.png" width="160" alt="Party creature source"> | <img src="examples/party-creature/small.gif" width="240" alt="Party creature GIF"> |

Minor redraw variations remain. These are actual outputs, not a guarantee of pixel-perfect consistency. See [examples](examples/README.md) for frames, prompts, reports, and provenance.

## Install the skill

```bash
git clone https://github.com/tinyray1314/static-meme-to-gif.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/static-meme-to-gif"
```

Do not overwrite an existing installation without reviewing it. Start a new Codex session, attach your image, and ask:

> Use $static-meme-to-gif to animate this reaction image. Make a 2-second loop and deliver both a small GIF and a full-frame-size version.

Frame generation requires access to an image generation/editing tool. Existing frames or GIFs can be processed without one. Other assistants need equivalent image and filesystem tools. The skill instructions are in Chinese; the workflow and command-line interfaces are language-independent.

## Workflow and defaults

Static image → plan one coherent action → generate 10–16 distinct frames → review identity/text/loop continuity → encode a 2-second loop → produce a 240×240 small version and a report.

The default target is 12 frames. Two seconds reflects the author's preference in the original experiment, not a universal optimum; 1.2 seconds is an optional comparison. The total duration stays constant when the frame count changes.

All four included cases were generated as one 4×3 sprite sheet per case and then split. Independent single-frame generation is also supported through the agent workflow. No specific image model version is assumed or independently verified.

## Run locally without an image service

Requires Python 3.10+ and Pillow. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/build_gif.py \
  --manifest examples/allow-everything/manifest.json \
  --out output/allow-everything
```

Outputs: `master.gif`, `small.gif`, and `report.json`. Existing output files are never overwritten. Manifest frame paths are relative to the manifest:

```json
{"frames": ["frames/01.png", "frames/02.png"], "total_ms": 2000}
```

The shortened example shows the format; the creative workflow typically uses 10–16 frames. The encoder accepts at least two. Optional `durations_ms` must match the number of frames and sum to `total_ms`; each duration must be a multiple of 10ms and at least 20ms. Default 12-frame timing is eight 170ms frames and four 160ms frames.

Split an inspected, uniform, gutter-free sheet:

```bash
python scripts/split_sheet.py \
  --image examples/allow-everything/sprite-sheet.png \
  --columns 4 --rows 3 --out output/frames
python scripts/build_gif.py --manifest output/frames/manifest.json --out output/rebuilt
```

Recompress an existing GIF, preserving frame timing and setting infinite looping:

```bash
python scripts/build_gif.py --gif examples/party-creature/master.gif \
  --out output/party --size 240 --max-kb 500
```

`--max-kb` uses KiB (1024 bytes). Compression tries 256, 128, then 64 colors without removing frames. Check `budget_met` in the report: exceeding the budget leaves a best-effort file and does not itself cause a nonzero exit. Non-square images are padded proportionally. **Alpha is flattened to white**, configurable with `--background`; transparency is not preserved. Identical adjacent frames may merge during encoding while retaining total duration.

## Limitations and validation

- Image generation can change lettering, anatomy, materials, or static backgrounds. Complex source images may require smaller movements or manual iteration.
- Regenerating frames is nondeterministic. Existing-frame encoding is locally reproducible, but byte-for-byte output can vary by Pillow version.
- 240×240 and 500 KiB are project presets, not official WeChat requirements. WeChat import has not been tested.
- Included sheets and decoded small first frames were visually inspected. Continuous playback was not independently verified. Reports retain that distinction.
- Play at least two loops to check the seam, flicker, ghosting, and readability before treating an output as visually approved.

## Contributing and license

Run `python -m unittest discover -s tests -v`. See [CONTRIBUTING.md](CONTRIBUTING.md) for useful bug reports and example submissions.

Skill instructions, original documentation, and code use the [MIT License](LICENSE). Example images and derived media are excluded from that grant; see the [asset notice](examples/ASSET_NOTICE.md).
