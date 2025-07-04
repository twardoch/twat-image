"""Image Alpha Utilities: Convert images to include alpha channels."""

from importlib import metadata

from image_alpha_utils.gray2alpha import ColorSpec, igray2alpha

__version__ = metadata.version(__name__)

__all__ = [
    "ColorSpec",
    "__version__",
    "igray2alpha",
]
