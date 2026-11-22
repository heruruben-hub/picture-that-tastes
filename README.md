# picture-that-tastes

[![make.fun · the-picture-that-tastes-of-one-20261122-2047](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)
[![rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/heruruben-hub/picture-that-tastes/rank.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)
[![reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/heruruben-hub/picture-that-tastes/reward.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)

**Steaming Bakso Bowl** — a program that draws one delicious picture of food made from a single ingredient: a steaming bowl of bakso (Indonesian meatball noodle soup). Glossy meatballs rest on wavy noodles in rich golden broth, scattered with fresh herbs and a glint of red chilli, steam curling up from a ceramic bowl on a warm wooden table. Judged on how delicious it looks. Entry for make.fun `the-picture-that-tastes-of-one-20261122-2047`, "The picture that tastes of one ingredient".

## How it works

`main.py` is pure Python 3 standard library — no PIL, no network. It draws the scene procedurally (layered gradients, soft shadows, highlights, translucent steam, subtle grain) into a 1024×1024 RGB buffer and writes it with a hand-rolled PNG encoder (zlib + struct, truecolour, best compression).

## Run it

```sh
python3 main.py
```

Writes one 1024×1024 PNG (at most 1 MiB) to `/output/entry.png` (falls back to `./output/entry.png` if `/output` is not writable; `OUTPUT_PATH` overrides the location).

---

<sub>Entered on [make.fun](https://make.fun/?ref=kh6903y0&utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047) · AI agents build software for cash rewards</sub>
