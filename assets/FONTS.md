# Fonts

The SVGs embed subsets (ASCII plus a few symbols, WOFF2, base64 `@font-face`) of:

- **Inter** 4.1, Regular and Bold. Copyright (c) 2016 The Inter Project Authors. SIL Open Font License 1.1. https://github.com/rsms/inter
- **JetBrains Mono** 2.304, Regular and Bold. Copyright 2020 The JetBrains Mono Project Authors. SIL Open Font License 1.1. https://github.com/JetBrains/JetBrainsMono

Subset files live in `scripts/fonts/` and are inlined by `scripts/design.py`. They are embedded under the family names "SW Inter" and "SW Mono" (renamed in CSS only; the font files are unmodified subsets).
