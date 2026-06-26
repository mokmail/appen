"""BEV branding overlay.

Single source of truth for all brand-related strings and colours so that
upstream merges never silently revert the rebrand.  Every value is
overridable through environment variables, mirroring the upstream env
convention.

Keep this file *additive* (no upstream file imports it at module top in a
way that changes upstream semantics).  Upstream files reference these
constants via a one-line import shim — see BEV_CUSTOMIZATIONS.md.
"""

import os

# ---- Identity -------------------------------------------------------------
BRAND_NAME = os.getenv('WEBUI_NAME', 'Bundesamt für Eich- und Vermessungswesen')
BRAND_SHORT_NAME = os.getenv('WEBUI_SHORT_NAME', 'BEV')
BRAND_DESCRIPTION = os.getenv(
    'WEBUI_DESCRIPTION',
    f'{BRAND_NAME} — KI-Plattform des Bundesamtes für Eich- und Vermessungswesen.',
)

# ---- URLs / assets --------------------------------------------------------
BRAND_FAVICON_URL = os.getenv('WEBUI_FAVICON_URL', '/favicon.png')
BRAND_URL = os.getenv('WEBUI_BRAND_URL', 'https://www.bev.gv.at')
BRAND_THEME_KEY = os.getenv('WEBUI_THEME_KEY', 'bev')

# ---- Colours --------------------------------------------------------------
# BEV "blaugrau" dark — used for PWA manifest background.
BRAND_BG_COLOR_DARK = os.getenv('WEBUI_BG_COLOR_DARK', '#1a2530')
BRAND_BG_COLOR_LIGHT = os.getenv('WEBUI_BG_COLOR_LIGHT', '#eff4f7')
BRAND_META_COLOR_DARK = os.getenv('WEBUI_META_COLOR_DARK', '#1a1a1a')
BRAND_META_COLOR_LIGHT = os.getenv('WEBUI_META_COLOR_LIGHT', '#ffffff')

# ---- Error / display strings ---------------------------------------------
# Upstream prefixes connection errors with "Open WebUI: ".  We de-brand.
BRAND_CONNECTION_ERROR = os.getenv('WEBUI_CONNECTION_ERROR', 'Server Connection Error')

# ---- OpenRouter X-Title ---------------------------------------------------
BRAND_OPENROUTER_TITLE = os.getenv('WEBUI_OPENROUTER_TITLE', BRAND_SHORT_NAME)

# ---- OAuth dynamic-client name -------------------------------------------
BRAND_OAUTH_CLIENT_NAME = os.getenv('WEBUI_OAUTH_CLIENT_NAME', BRAND_SHORT_NAME)


__all__ = [
    'BRAND_NAME',
    'BRAND_SHORT_NAME',
    'BRAND_DESCRIPTION',
    'BRAND_FAVICON_URL',
    'BRAND_URL',
    'BRAND_THEME_KEY',
    'BRAND_BG_COLOR_DARK',
    'BRAND_BG_COLOR_LIGHT',
    'BRAND_META_COLOR_DARK',
    'BRAND_META_COLOR_LIGHT',
    'BRAND_CONNECTION_ERROR',
    'BRAND_OPENROUTER_TITLE',
    'BRAND_OAUTH_CLIENT_NAME',
]