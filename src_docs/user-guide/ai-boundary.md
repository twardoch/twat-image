---
this_file: src_docs/user-guide/ai-boundary.md
---

# AI Image Boundary

`twat-image` contains **no provider clients** for AI image generation or editing. The `generate_image` and `edit_image` functions are thin adapters that delegate to [`twat-genai`](https://github.com/twardoch/twat-genai) when it is installed.

## Usage

```python
from twat_image import generate_image, edit_image

# Requires twat-genai
generate_image("a black cat as clean vector art", output_dir="out")
edit_image("make it look like ink on paper", "input.png", output_dir="out")
```

If `twat-genai` is not installed, both functions raise `ImportError` with an explanatory message.

## Why the split?

Deterministic image operations (geometry, normalisation, alpha) are stable and dependency-light — `Pillow` and `NumPy`. AI backends carry large, frequently-changing dependency trees and require API keys. Keeping them separate lets you install and test `twat-image` without any AI credentials.

Provider support (OpenAI, Gemini, Fal, etc.) is configured and managed entirely inside `twat-genai`.
