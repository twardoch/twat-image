---
this_file: src_docs/user-guide/cli-reference.md
---

# CLI Reference

`twat-image` installs several entry points. The main one is `twat-image`; individual sub-commands are also available as standalone scripts for shell pipelines.

## `twat-image` (main dispatcher)

```
twat-image <command> [options]
```

Run `twat-image --help` for the full list of sub-commands.

---

## Commands

### `gray2alpha`

Convert an image to RGBA using its grayscale luminance as the alpha channel.

```bash
twat-image gray2alpha INPUT OUTPUT [--color COLOR] [--white_point WP] [--black_point BP] [--negative]
```

| Option | Default | Description |
|---|---|---|
| `--color` | `black` | Fill color (name, hex, or `R,G,B`) |
| `--white_point` | `0.9` | Threshold above which pixels become fully white in the mask |
| `--black_point` | `0.1` | Threshold below which pixels become fully black in the mask |
| `--negative` | off | Invert alpha assignment (bright → opaque) |

Pass `-` as `INPUT` or `OUTPUT` to use stdin / stdout.

### `scale`

Resize an image.

```bash
twat-image scale INPUT OUTPUT [--width W] [--height H] [--factor F]
```

### `crop`

Crop a rectangular region.

```bash
twat-image crop INPUT OUTPUT LEFT UPPER RIGHT LOWER
```

### `outcrop`

Pad an image with a solid border.

```bash
twat-image outcrop INPUT OUTPUT [--left N] [--right N] [--top N] [--bottom N] [--fill_color COLOR]
```

### `normalize`

Apply auto-contrast (and optionally histogram equalisation).

```bash
twat-image normalize INPUT OUTPUT [--no-autocontrast] [--equalize]
```

### `convert`

Transcode between formats.

```bash
twat-image convert INPUT OUTPUT
```

### `metadata`

Print image metadata as JSON.

```bash
twat-image metadata INPUT
```

### `info`

Print version and available sub-commands.

```bash
twat-image info
```

---

## Standalone scripts

| Script | Equivalent |
|---|---|
| `twat-image-gray2alpha` | `twat-image gray2alpha` |
| `twat-image-scale` | `twat-image scale` |
| `twat-image-crop` | `twat-image crop` |
| `twat-image-outcrop` | `twat-image outcrop` |
| `twat-image-normalize` | `twat-image normalize` |
| `twat-image-convert` | `twat-image convert` |
| `twat-image-info` | `twat-image info` |
| `imagealpha` | Legacy alias for `gray2alpha` |
