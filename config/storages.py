"""Custom static files storage.

The theme's minified JS/CSS bundles reference `.map` source-map files that were
never shipped with the theme. WhiteNoise's default manifest storage treats every
referenced file as required and raises MissingFileError during collectstatic.

Setting ``manifest_strict = False`` keeps all the cache-busting/compression
benefits of the manifest storage, but downgrades a missing referenced file from
a hard error to a skip, so collectstatic succeeds.
"""

from whitenoise.storage import CompressedManifestStaticFilesStorage


class WhiteNoiseStaticFilesStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False
