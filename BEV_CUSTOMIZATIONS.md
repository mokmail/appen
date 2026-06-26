# BEV Customizations Manifest

This document tracks every BEV overlay layer on top of upstream open-webui.
On each upstream upgrade, diff against this manifest to confirm nothing drifted.

**Base version:** open-webui 0.9.6 (fork point `1a97751e3`)

---

## Overlay architecture

The principle is **overlay, don't inline**.  BEV customizations live in
dedicated overlay files.  Upstream files are either untouched or contain
only minimal, clearly-marked shim lines (`# --- BEV overlay ---`).

### Upgrade procedure

1. `git fetch origin` (upstream open-webui)
2. `git tag pre-upgrade-<date>` (safety tag)
3. `git checkout -b upgrade/v0.9.X`
4. `git merge origin/main` (or rebase)
5. Resolve conflicts — should be limited to the shim files listed below
6. `make bev-overlay`  — re-apply BEV static assets
7. `make icons-generate` — if upstream touched Lucide versions
8. `make backend-dev` + `npm run build` — smoke test
9. Verify: theme switch (BEV), GitLab import, prompt suggestions, oikb orchestrator

---

## 1. Backend branding module

| File | Type | Description |
|---|---|---|
| `backend/open_webui/branding.py` | **New** | Single source of truth for brand strings, colours, error prefixes. All values env-overridable (reads from `.env`). |
| `backend/open_webui/bev_content.py` | **New** | BEV-specific content (prompt suggestions). |

### `.env` variables (all optional — defaults are BEV values)

| Env var | Default | Description |
|---|---|---|
| `WEBUI_VERSION` | `package.json` version | Version string shown in UI + used for frontend build. **Must be set at build time** (`WEBUI_VERSION=x npm run build`) so the frontend matches the backend and no reload loop triggers. |
| `WEBUI_NAME` | `Bundesamt für Eich- und Vermessungswesen` | Full display name |
| `WEBUI_SHORT_NAME` | `BEV` | Short name (PWA, OpenRouter, OAuth) |
| `WEBUI_DESCRIPTION` | `KI-Plattform des …` | Description / tagline |
| `WEBUI_FAVICON_URL` | `/favicon.png` | Favicon path |
| `WEBUI_BRAND_URL` | `https://www.bev.gv.at` | External website URL |
| `WEBUI_THEME_KEY` | `bev` | Theme key (must match CSS class in bev-theme.css) |
| `WEBUI_BG_COLOR_DARK` | `#1a2530` | PWA manifest dark background |
| `WEBUI_BG_COLOR_LIGHT` | `#eff4f7` | PWA manifest light background |
| `WEBUI_META_COLOR_DARK` | `#1a1a1a` | `<meta name="theme-color">` dark |
| `WEBUI_META_COLOR_LIGHT` | `#ffffff` | `<meta name="theme-color">` light |
| `WEBUI_CONNECTION_ERROR` | `Server Connection Error` | De-branded error string |
| `WEBUI_OPENROUTER_TITLE` | `BEV` | OpenRouter X-Title header |
| `WEBUI_OAUTH_CLIENT_NAME` | `BEV` | OAuth dynamic client name |

### Frontend delivery

The backend `/api/config` endpoint now includes a `brand` block with all
values above.  The frontend `BRAND` store (`src/lib/stores/index.ts`) is
populated from this block at startup.  Components read `\$BRAND.url`,
`\$BRAND.short_name`, `\$BRAND.description`, etc. instead of hardcoding.

### Upstream files with BEV shim (1-line import + override)

| Upstream file | Shim | What it does |
|---|---|---|
| `backend/open_webui/env.py` | `from open_webui.branding import BRAND_NAME, BRAND_FAVICON_URL` | Overrides `WEBUI_NAME` and `WEBUI_FAVICON_URL` after upstream default |
| `backend/open_webui/config.py` | `from open_webui.bev_content import BEV_PROMPT_SUGGESTIONS` | Replaces `default_prompt_suggestions` after upstream block |
| `backend/open_webui/main.py` | `from open_webui.branding import BRAND_SHORT_NAME, BRAND_DESCRIPTION, BRAND_BG_COLOR_DARK` | Overrides manifest `short_name`, `description`, `background_color` |
| `backend/open_webui/routers/openai.py` | `from open_webui.branding import BRAND_CONNECTION_ERROR, BRAND_OPENROUTER_TITLE` | Replaces `'Open WebUI: Server Connection Error'` and `X-Title` |
| `backend/open_webui/routers/audio.py` | `from open_webui.branding import BRAND_CONNECTION_ERROR` | Replaces `'Open WebUI: Server Connection Error'` (5 occurrences) |
| `backend/open_webui/utils/automations.py` | `from open_webui.branding import BRAND_NAME` | Fallback `WEBUI_NAME` in calendar webhook |
| `backend/open_webui/utils/oauth.py` | `from open_webui.branding import BRAND_OAUTH_CLIENT_NAME` | OAuth dynamic client `client_name` |

---

## 2. GitLab knowledge integration (extracted router)

| File | Type | Description |
|---|---|---|
| `backend/open_webui/routers/knowledge_gitlab.py` | **New** | Full GitLab repo/wiki integration: 4 endpoints, models, helpers. Mounted at `/api/v1/knowledge`. |
| `backend/open_webui/main.py` | Shim | `import knowledge_gitlab` + `app.include_router(knowledge_gitlab.router, ...)` |
| `backend/open_webui/routers/knowledge.py` | **Upstream (restored)** | No longer modified by BEV — upgraded wholesale. |

### GitLab endpoints

- `POST /api/v1/knowledge/{id}/gitlab/repo` — sync import
- `POST /api/v1/knowledge/{id}/gitlab/wiki` — sync import
- `POST /api/v1/knowledge/{id}/gitlab/repo/stream` — SSE streaming import
- `POST /api/v1/knowledge/{id}/gitlab/wiki/stream` — SSE streaming import

---

## 3. Frontend branding

| File | Type | Description |
|---|---|---|
| `src/lib/brand.ts` | **New** | Frontend brand constants: `BRAND_NAME`, `BRAND_SHORT_NAME`, `BRAND_TAGLINE`, `BRAND_URL`, `BRAND_THEME_KEY`, colours. |
| `src/lib/constants.ts` | Shim | `APP_NAME` stays `'Open WebUI'` (upstream); `BEV_APP_NAME` exported from `brand.ts` |
| `src/lib/stores/index.ts` | Shim | `WEBUI_NAME` store initial value uses `BEV_APP_NAME` (updated from backend at runtime) |

---

## 4. Theme / design system

| File | Type | Description |
|---|---|---|
| `src/lib/bev-theme.css` | **New (670 lines)** | All BEV CSS: global Tailwind color-scale overrides (`:root`), `.bev` scoped component classes, contour background, sidebar, tooltips, editor selection. |
| `static/themes/bev.css` | **Generated** | Copy of `bev-theme.css` for the theme-switcher. Synced by `make bev-overlay`. |
| `src/tailwind.css` | **Upstream (restored)** | No longer modified — BEV color overrides moved to `bev-theme.css` |
| `src/app.css` | **Upstream (restored)** | No longer modified — editor-selection override moved to `bev-theme.css` |
| `src/app.html` | Modified (minimal) | BEV theme branch in boot script, `<title>`, theme-color meta, splash colours. All marked `<!-- BEV overlay -->` |
| `src/routes/+layout.svelte` | Modified (minimal) | Imports `bev-theme.css`, `$WEBUI_NAME` in notifications, `bev` theme in array + class logic, window-message origin allowlist |
| `src/lib/components/chat/Settings/General.svelte` | Modified (minimal) | `bev` theme option, bev theme resolution, BEV colour values. Marked `// BEV overlay` |

### New frontend components (no upstream counterpart — zero conflict)

| File | Description |
|---|---|
| `src/lib/components/common/ContourBackground.svelte` | SVG topographic contour-line background |
| `src/lib/components/workspace/Knowledge/KnowledgeBase/AddGitlabModal.svelte` | GitLab import modal |
| `src/lib/components/workspace/Knowledge/KnowledgeBase/GitlabProgressModal.svelte` | GitLab progress modal |

### Frontend API client (GitLab)

| File | Type | Description |
|---|---|---|
| `src/lib/apis/knowledge/index.ts` | Modified | GitLab API functions appended (addGitlabRepoToKnowledge, etc.) |

---

## 5. Static assets (overlay dir + build script)

| Path | Type | Description |
|---|---|---|
| `assets/bev/backend-static/` | **New** | BEV-branded backend static assets (favicons, logos, splash, manifest) |
| `assets/bev/frontend-static/` | **New** | BEV-branded frontend static assets |
| `scripts/bev-asset-overlay.sh` | **New** | Copies BEV assets from `assets/bev/` into upstream static dirs |
| `Makefile` | Modified | `bev-overlay` target runs the script |

**After every upstream upgrade, run `make bev-overlay`** to re-apply BEV assets
onto the (possibly updated) upstream static directories.

---

## 6. Out-of-tree infrastructure (no upstream counterpart — inherently safe)

| Path | Description |
|---|---|
| `oikb-orchestrator/` | FastAPI GUI orchestrator for oikb knowledge-base sync |
| `oikb-data/` | Config dir for oikb daemon |
| `intranet/` | Glossary import artifact |
| `docker-compose.bev.yaml` | BEV production stack |
| `docker-compose.oikb.yaml` | oikb variant stack |
| `Styleguide_4-0_Corporate-Design-des-Bundes.pdf` | Federal CD reference |
| `Webseiten-Styleguide_Corporate-Design-des-Bundes.pdf` | Federal web styleguide |
| `BEV_Organsiation_Aufgaben_2026_ECO_CST.docx` | BEV organisation reference |
| `scripts/generate-lucide-icons.cjs` | Lucide icon wrapper generator |

---

## 7. Config / manifest files

| File | Type | Notes |
|---|---|---|
| `package.json` | Modified | `name` → `'bev-ki-plattform'` |
| `Makefile` | Modified | BEV targets, `icons-generate`, `bev-overlay` |
| `README.md` | Modified | German BEV readme |
| `Dockerfile` | Modified | `libmariadb-dev`, `bge-micro-v2`, torch pin |
| `.env` | Modified | BEV env vars (**contains secrets — do not commit**) |

---

## Conflict-risk summary (after refactor)

| Hotspot | Before | After |
|---|---|---|
| `knowledge.py` | merge nightmare (GitLab + regressions) | **zero conflict** (upstream, GitLab isolated) |
| Branding in 10 files | 10 conflicts | **1 module + shims** |
| `tailwind.css` + `app.css` | core-scale collision | **upstream-owned**, overrides in `bev-theme.css` |
| Static assets | clobbered on upgrade | **overlay dir + `make bev-overlay`** |
| Svelte components | large in-file diffs | minimal, marked `// BEV overlay` |
| oikb/BEV infra | already safe | unchanged |