"""
BEV uvicorn entrypoint — applies branding patches to upstream modules
at import time, then delegates to the real app.

Usage in start.sh:
    uvicorn bev_runner:app ...

Never COPYs or modifies upstream files — all patching is in-memory.
"""

# 1. Load BEV modules (zero conflict — new files)
from open_webui import branding as _branding
from open_webui import bev_content as _bev_content

# 2. Patch upstream module-level values BEFORE main.py imports them.
#    main.py does `from open_webui.env import WEBUI_NAME`, which reads
#    the current value from the already-cached (and patched) module.

import open_webui.env as _env
_env.WEBUI_NAME = _branding.BRAND_NAME
_env.WEBUI_FAVICON_URL = _branding.BRAND_FAVICON_URL

import open_webui.config as _config
_config.default_prompt_suggestions = _bev_content.BEV_PROMPT_SUGGESTIONS

# 3. Import the real app — all modules it imports will see the patched values
from open_webui.main import app

# 4. Register BEV GitLab knowledge router
from open_webui.routers.knowledge_gitlab import router as _kg_router
app.include_router(_kg_router, prefix='/api/v1/knowledge', tags=['knowledge'])
