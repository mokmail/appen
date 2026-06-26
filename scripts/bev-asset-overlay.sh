#!/usr/bin/env bash
# BEV asset overlay — copies BEV-branded static assets from assets/bev/
# into the upstream static directories.
#
# Run after an upstream upgrade to re-apply BEV branding assets.
# See BEV_CUSTOMIZATIONS.md.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "[BEV] Overlaying backend static assets…"
BACKEND_SRC="$REPO_ROOT/assets/bev/backend-static"
BACKEND_DST="$REPO_ROOT/backend/open_webui/static"

cp "$BACKEND_SRC/favicon.png"          "$BACKEND_DST/favicon.png"
cp "$BACKEND_SRC/favicon-96x96.png"    "$BACKEND_DST/favicon-96x96.png"
cp "$BACKEND_SRC/favicon-dark.png"     "$BACKEND_DST/favicon-dark.png"
cp "$BACKEND_SRC/favicon.ico"          "$BACKEND_DST/favicon.ico"
cp "$BACKEND_SRC/favicon.svg"          "$BACKEND_DST/favicon.svg"
cp "$BACKEND_SRC/logo.png"             "$BACKEND_DST/logo.png"
cp "$BACKEND_SRC/splash.png"           "$BACKEND_DST/splash.png"
cp "$BACKEND_SRC/splash-dark.png"      "$BACKEND_DST/splash-dark.png"
cp "$BACKEND_SRC/apple-touch-icon.png" "$BACKEND_DST/apple-touch-icon.png"
cp "$BACKEND_SRC/web-app-manifest-192x192.png" "$BACKEND_DST/web-app-manifest-192x192.png"
cp "$BACKEND_SRC/web-app-manifest-512x512.png" "$BACKEND_DST/web-app-manifest-512x512.png"
cp "$BACKEND_SRC/user.png"             "$BACKEND_DST/user.png"
cp "$BACKEND_SRC/site.webmanifest"     "$BACKEND_DST/site.webmanifest"
mkdir -p "$BACKEND_DST/swagger-ui"
cp "$BACKEND_SRC/swagger-ui-favicon.png" "$BACKEND_DST/swagger-ui/favicon.png"

echo "[BEV] Overlaying frontend static assets…"
FE_SRC="$REPO_ROOT/assets/bev/frontend-static"
FE_DST="$REPO_ROOT/static/static"

cp "$FE_SRC/favicon.png"          "$FE_DST/favicon.png"
cp "$FE_SRC/favicon-96x96.png"    "$FE_DST/favicon-96x96.png"
cp "$FE_SRC/favicon-dark.png"     "$FE_DST/favicon-dark.png"
cp "$FE_SRC/favicon.ico"          "$FE_DST/favicon.ico"
cp "$FE_SRC/favicon.svg"          "$FE_DST/favicon.svg"
cp "$FE_SRC/logo.png"             "$FE_DST/logo.png"
cp "$FE_SRC/logo_mit_text.png"    "$FE_DST/logo_mit_text.png"
cp "$FE_SRC/splash.png"           "$FE_DST/splash.png"
cp "$FE_SRC/splash-dark.png"      "$FE_DST/splash-dark.png"
cp "$FE_SRC/apple-touch-icon.png" "$FE_DST/apple-touch-icon.png"
cp "$FE_SRC/web-app-manifest-192x192.png" "$FE_DST/web-app-manifest-192x192.png"
cp "$FE_SRC/web-app-manifest-512x512.png" "$FE_DST/web-app-manifest-512x512.png"
cp "$FE_SRC/site.webmanifest"     "$FE_DST/site.webmanifest"

# Root-level frontend assets
cp "$FE_SRC/favicon-root.png" "$REPO_ROOT/static/favicon.png"
cp "$FE_SRC/opensearch.xml"   "$REPO_ROOT/static/opensearch.xml"

# Theme CSS
cp "$REPO_ROOT/src/lib/bev-theme.css" "$REPO_ROOT/static/themes/bev.css"

echo "[BEV] Asset overlay complete."