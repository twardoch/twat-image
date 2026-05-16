"""Deprecated: Use twat_image instead."""

import warnings

warnings.warn(
    "image_alpha_utils is deprecated. Use twat_image instead.",
    DeprecationWarning,
    stacklevel=2,
)

from twat_image import *  # noqa: E402, F403
from twat_image.gray2alpha import *  # noqa: E402, F403
