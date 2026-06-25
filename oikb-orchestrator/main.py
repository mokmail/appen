"""
oikb Orchestrator GUI
=====================

A lightweight FastAPI web GUI that orchestrates an `oikb` daemon
(https://github.com/open-webui/oikb) by proxying every major API endpoint
through forms / interactive pages so users can send any type of request
and provide the parameters needed without touching a terminal.

The app runs on port 8086 (see `--port` arg / `OIKB_GUI_PORT` env) and
talks to the oikb daemon reachable at `${OIKB_URL:-http://oikb:8080}`.

Endpoints exposed by the daemon (from docs/guide.md "API Endpoints"):
    GET  /health
    GET  /health/ready
    GET  /metrics
    GET  /history
    POST /sync/{name-or-kb-id}
    POST /sync/{id}?dry_run=true
    POST /webhooks/github
    POST /webhooks/gitlab
    POST /webhooks/slack
    POST /webhooks/confluence
"""

from __future__ import annotations

import asyncio
import json
import os
import shlex
from typing import Any

import httpx
import yaml
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

OIKB_CONTAINER = os.environ.get("OIKB_CONTAINER", "oikb")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OIKB_URL = os.environ.get("OIKB_URL", "http://oikb:8080").rstrip("/")
OIKB_API_KEY = os.environ.get("OIKB_API_KEY", "")
# Path to the oikb config file (mounted into the orchestrator container too).
OIKB_CONFIG_PATH = os.environ.get("OIKB_CONFIG_PATH", "/data/oikb.yaml")

HTTP_TIMEOUT = float(os.environ.get("OIKB_GUI_TIMEOUT", "30"))

app = FastAPI(title="oikb Orchestrator", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def _headers() -> dict[str, str]:
    h = {"Accept": "application/json"}
    if OIKB_API_KEY:
        h["Authorization"] = f"Bearer {OIKB_API_KEY}"
    return h


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=OIKB_URL,
        headers=_headers(),
        timeout=HTTP_TIMEOUT,
        follow_redirects=True,
    )


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "oikb_url": OIKB_URL,
            "has_api_key": bool(OIKB_API_KEY),
        },
    )


# ---------------------------------------------------------------------------
# Proxy endpoints (called by the browser SPA).
# Every daemon endpoint is reachable via /proxy/<path:path> so the GUI
# can issue arbitrary requests with the user-supplied parameters.
# ---------------------------------------------------------------------------
@app.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request):
    """Forward a request to the oikb daemon.

    The browser always POSTs to this route with a JSON body:
        {
          "method": "GET" | "POST" | "PUT" | "DELETE",   # target method on daemon
          "params": {...}                                # query params
          "json":   {...}                                # JSON body (mutually exclusive with body)
          "body":   "raw string"                         # raw body (used for webhooks)
          "headers": {...}                               # extra headers (signature/token)
        }
    The target `method` is honored — the incoming HTTP method is ignored.
    """
    body: Any = {}
    try:
        body = await request.json()
    except Exception:
        body = {}

    method = str(body.get("method") or request.method or "GET").upper()
    if method not in {"GET", "POST", "PUT", "DELETE"}:
        return JSONResponse({"error": f"unsupported method: {method}"}, status_code=405)

    params = body.get("params") or {}
    json_body = body.get("json")
    raw_body = body.get("body")
    extra_headers = body.get("headers") or {}
    headers = dict(_headers())
    headers.pop("Accept", None)  # let httpx negotiate

    # Merge user-supplied headers; drop empty-string values so we don't
    # send e.g. "X-Slack-Signature:" which the daemon may reject.
    for k, v in extra_headers.items():
        if v not in (None, ""):
            headers[k] = str(v)

    async with _client() as client:
        try:
            kwargs: dict[str, Any] = {"params": params, "headers": headers, "follow_redirects": True}
            if method in {"POST", "PUT"}:
                if raw_body is not None:
                    kwargs["content"] = raw_body
                    if "Content-Type" not in {k.lower() for k in headers}:
                        kwargs["headers"] = {**headers, "Content-Type": "application/json"}
                elif json_body is not None:
                    kwargs["json"] = json_body
            resp = await client.request(method, path, **kwargs)
        except httpx.RequestError as exc:
            return JSONResponse(
                {"error": f"cannot reach oikb daemon at {OIKB_URL}: {exc}"},
                status_code=502,
            )

    content_type = resp.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            return JSONResponse(resp.json(), status_code=resp.status_code)
        except Exception:
            return JSONResponse({"raw": resp.text}, status_code=resp.status_code)
    # text/plain (e.g. /metrics) or anything else → pass through untouched
    return JSONResponse(
        {"raw": resp.text, "content_type": content_type, "status": resp.status_code},
        status_code=resp.status_code,
    )


@app.get("/info")
async def info():
    """Return orchestrator settings to the browser (no secrets)."""
    return {
        "oikb_url": OIKB_URL,
        "has_api_key": bool(OIKB_API_KEY),
        "timeout": HTTP_TIMEOUT,
        "config_path": OIKB_CONFIG_PATH,
        "endpoints": [
            {"method": "GET", "path": "/health", "desc": "Sync status for all sources (k8s readiness probe)"},
            {"method": "GET", "path": "/health/ready", "desc": "Liveness probe"},
            {"method": "GET", "path": "/metrics", "desc": "Prometheus metrics"},
            {"method": "GET", "path": "/history", "desc": "Sync history (filterable by KB, errors)"},
            {"method": "POST", "path": "/sync/{name-or-kb-id}", "desc": "Trigger immediate sync"},
            {"method": "POST", "path": "/sync/{id}?dry_run=true", "desc": "Preview changes without uploading"},
            {"method": "POST", "path": "/webhooks/github", "desc": "GitHub push webhook"},
            {"method": "POST", "path": "/webhooks/gitlab", "desc": "GitLab push webhook"},
            {"method": "POST", "path": "/webhooks/slack", "desc": "Slack event webhook"},
            {"method": "POST", "path": "/webhooks/confluence", "desc": "Confluence update webhook"},
        ],
    }


# ---------------------------------------------------------------------------
# Config + connectors
# ---------------------------------------------------------------------------
def _read_config() -> dict[str, Any]:
    """Read the mounted oikb.yaml. Returns {} if missing/invalid."""
    try:
        with open(OIKB_CONFIG_PATH, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
            if not isinstance(data, dict):
                return {}
            return data
    except FileNotFoundError:
        return {"_error": f"config not found at {OIKB_CONFIG_PATH}"}
    except yaml.YAMLError as exc:
        return {"_error": f"invalid YAML: {exc}"}


@app.get("/config")
async def get_config():
    """Return the parsed oikb.yaml so the GUI can render the source list."""
    return _read_config()


@app.post("/config")
async def save_config(request: Request):
    """Overwrite oikb.yaml with the posted document (full replace)."""
    try:
        doc = await request.json()
    except Exception:
        return JSONResponse({"error": "body must be JSON"}, status_code=400)
    try:
        with open(OIKB_CONFIG_PATH, "w", encoding="utf-8") as fh:
            yaml.safe_dump(doc, fh, sort_keys=False, default_flow_style=False, allow_unicode=True)
    except OSError as exc:
        return JSONResponse({"error": f"cannot write {OIKB_CONFIG_PATH}: {exc}"}, status_code=500)
    return {"saved": True, "path": OIKB_CONFIG_PATH}


# Exhaustive connector catalogue from docs/guide.md "All Connectors".
CONNECTORS = [
    {"category": "Git", "sources": ["GitHub", "GitLab", "Bitbucket"]},
    {"category": "Cloud Storage", "sources": ["S3", "GCS", "Azure Blob", "Dropbox", "R2", "Google Drive", "SharePoint", "Nextcloud", "Egnyte", "Oracle Cloud"]},
    {"category": "Wikis & KBs", "sources": ["Confluence", "Notion", "BookStack", "Discourse", "GitBook", "Guru", "Outline", "Slab", "Document360", "DokuWiki", "Google Sites"]},
    {"category": "Ticketing", "sources": ["Jira", "Linear", "Zendesk", "Freshdesk", "Asana", "ClickUp", "Airtable", "ServiceNow", "ProductBoard"]},
    {"category": "Messaging", "sources": ["Slack", "Discord", "Microsoft Teams", "Gmail", "Zulip"]},
    {"category": "Meetings", "sources": ["Gong", "Fireflies"]},
    {"category": "Forums", "sources": ["XenForo"]},
    {"category": "Sales & CRM", "sources": ["Salesforce", "HubSpot"]},
    {"category": "Web", "sources": ["Website / Sitemap crawler"]},
]

# Flat list of all possible source types with their URI prefixes and placeholders.
# Used by the GUI to render a dropdown when adding/editing sources.
SOURCE_TYPES = [
    {"id": "local",          "label": "Local filesystem",                              "prefix": "",              "placeholder": "./docs or /absolute/path", "extra_fields": []},
    {"id": "website",        "label": "Website / Sitemap crawler",                     "prefix": "web:",          "placeholder": "https://bev.gv.at or https://example.com/sitemap.xml", "extra_fields": []},
    {"id": "github",         "label": "GitHub",                                        "prefix": "github:",       "placeholder": "owner/repo", "extra_fields": ["branch", "path"]},
    {"id": "gitlab",         "label": "GitLab",                                        "prefix": "gitlab:",       "placeholder": "owner/repo", "extra_fields": ["branch", "path"]},
    {"id": "bitbucket",      "label": "Bitbucket",                                     "prefix": "bitbucket:",    "placeholder": "owner/repo", "extra_fields": ["branch", "path"]},
    {"id": "s3",             "label": "S3",                                            "prefix": "s3://",         "placeholder": "bucket/prefix", "extra_fields": ["path"]},
    {"id": "gcs",            "label": "GCS",                                           "prefix": "gcs://",        "placeholder": "bucket/prefix", "extra_fields": ["path"]},
    {"id": "azure",          "label": "Azure Blob",                                    "prefix": "azure://",      "placeholder": "container/path", "extra_fields": ["path"]},
    {"id": "dropbox",        "label": "Dropbox",                                       "prefix": "dropbox://",    "placeholder": "path", "extra_fields": []},
    {"id": "r2",             "label": "R2",                                            "prefix": "r2://",         "placeholder": "bucket/prefix", "extra_fields": ["path"]},
    {"id": "googledrive",    "label": "Google Drive",                                  "prefix": "google-drive:", "placeholder": "folder-id", "extra_fields": []},
    {"id": "sharepoint",     "label": "SharePoint",                                    "prefix": "sharepoint://", "placeholder": "site/path", "extra_fields": []},
    {"id": "nextcloud",      "label": "Nextcloud",                                     "prefix": "nextcloud://",  "placeholder": "path", "extra_fields": []},
    {"id": "egnyte",         "label": "Egnyte",                                        "prefix": "egnyte://",     "placeholder": "path", "extra_fields": []},
    {"id": "oraclecloud",    "label": "Oracle Cloud",                                  "prefix": "oracle-cloud://", "placeholder": "bucket/prefix", "extra_fields": ["path"]},
    {"id": "confluence",     "label": "Confluence",                                    "prefix": "confluence:",   "placeholder": "SPACE_KEY", "extra_fields": []},
    {"id": "notion",         "label": "Notion",                                        "prefix": "notion:",       "placeholder": "page-id", "extra_fields": []},
    {"id": "bookstack",      "label": "BookStack",                                     "prefix": "bookstack:",    "placeholder": "space", "extra_fields": []},
    {"id": "discourse",      "label": "Discourse",                                     "prefix": "discourse:",    "placeholder": "topic-id", "extra_fields": []},
    {"id": "gitbook",        "label": "GitBook",                                       "prefix": "gitbook:",      "placeholder": "space", "extra_fields": []},
    {"id": "guru",           "label": "Guru",                                          "prefix": "guru:",         "placeholder": "card-id", "extra_fields": []},
    {"id": "outline",        "label": "Outline",                                       "prefix": "outline:",      "placeholder": "collection-id", "extra_fields": []},
    {"id": "slab",           "label": "Slab",                                          "prefix": "slab:",         "placeholder": "post-id", "extra_fields": []},
    {"id": "document360",    "label": "Document360",                                   "prefix": "document360:",  "placeholder": "project", "extra_fields": []},
    {"id": "dokuwiki",       "label": "DokuWiki",                                      "prefix": "dokuwiki:",     "placeholder": "page", "extra_fields": []},
    {"id": "googlesites",    "label": "Google Sites",                                  "prefix": "google-sites:", "placeholder": "site-url", "extra_fields": []},
    {"id": "jira",           "label": "Jira",                                          "prefix": "jira:",         "placeholder": "project-key", "extra_fields": []},
    {"id": "linear",         "label": "Linear",                                        "prefix": "linear:",       "placeholder": "team-id", "extra_fields": []},
    {"id": "zendesk",        "label": "Zendesk",                                       "prefix": "zendesk:",      "placeholder": "subdomain", "extra_fields": []},
    {"id": "freshdesk",      "label": "Freshdesk",                                     "prefix": "freshdesk:",    "placeholder": "subdomain", "extra_fields": []},
    {"id": "asana",          "label": "Asana",                                         "prefix": "asana:",        "placeholder": "project-id", "extra_fields": []},
    {"id": "clickup",        "label": "ClickUp",                                       "prefix": "clickup:",      "placeholder": "space-id", "extra_fields": []},
    {"id": "airtable",       "label": "Airtable",                                      "prefix": "airtable:",     "placeholder": "base-id", "extra_fields": []},
    {"id": "servicenow",     "label": "ServiceNow",                                    "prefix": "servicenow:",   "placeholder": "instance", "extra_fields": []},
    {"id": "productboard",   "label": "ProductBoard",                                  "prefix": "productboard:", "placeholder": "notebook", "extra_fields": []},
    {"id": "slack",          "label": "Slack",                                         "prefix": "slack:",        "placeholder": "channel-id", "extra_fields": []},
    {"id": "discord",        "label": "Discord",                                       "prefix": "discord:",      "placeholder": "channel-id", "extra_fields": []},
    {"id": "msteams",        "label": "Microsoft Teams",                               "prefix": "msteams:",      "placeholder": "channel-id", "extra_fields": []},
    {"id": "gmail",          "label": "Gmail",                                         "prefix": "gmail:",        "placeholder": "label", "extra_fields": []},
    {"id": "zulip",          "label": "Zulip",                                         "prefix": "zulip:",        "placeholder": "stream", "extra_fields": []},
    {"id": "gong",           "label": "Gong",                                          "prefix": "gong:",         "placeholder": "call-id", "extra_fields": []},
    {"id": "fireflies",      "label": "Fireflies",                                     "prefix": "fireflies:",    "placeholder": "meeting-id", "extra_fields": []},
    {"id": "xenforo",        "label": "XenForo",                                       "prefix": "xenforo:",      "placeholder": "forum-url", "extra_fields": []},
    {"id": "salesforce",     "label": "Salesforce",                                    "prefix": "salesforce:",   "placeholder": "object-type", "extra_fields": []},
    {"id": "hubspot",        "label": "HubSpot",                                       "prefix": "hubspot:",      "placeholder": "object-id", "extra_fields": []},
    {"id": "custom",         "label": "Custom (free-form)",                            "prefix": "",              "placeholder": "Full source URI (e.g. confluence:ENG, s3://bucket/…)", "extra_fields": ["branch", "path"]},
]

# Source-prefix → required-env-var map (from guide) for the connectors that
# need credentials. Used by the GUI to hint at what env vars to set.
CONNECTOR_AUTH = {
    "github": ["GITHUB_TOKEN (private repos)"],
    "gitlab": ["GITLAB_TOKEN"],
    "bitbucket": ["BITBUCKET_TOKEN"],
    "confluence": ["CONFLUENCE_URL", "CONFLUENCE_USERNAME", "CONFLUENCE_API_TOKEN"],
    "s3": ["AWS credentials (profile / env)"],
    "gcs": ["Google service account"],
    "azure": ["Azure storage credentials"],
    "sharepoint": ["SHAREPOINT_TENANT_ID", "SHAREPOINT_CLIENT_ID", "SHAREPOINT_CLIENT_SECRET or SHAREPOINT_CERTIFICATE_PATH"],
    "nextcloud": ["NEXTCLOUD_URL", "NEXTCLOUD_USER", "NEXTCLOUD_PASSWORD"],
}


@app.get("/connectors")
async def connectors():
    """Return the exhaustive connector catalogue + auth hints."""
    return {"categories": CONNECTORS, "auth": CONNECTOR_AUTH, "total": sum(len(c["sources"]) for c in CONNECTORS)}


@app.get("/source-types")
async def source_types():
    """Return the flat list of all possible source types with prefixes and placeholders."""
    return {"types": SOURCE_TYPES}


# ---------------------------------------------------------------------------
# Host directory browser
# ---------------------------------------------------------------------------
@app.post("/browse")
async def browse_host(request: Request):
    """List host directory contents using a temporary container.

    Uses the orchestrator's own base image (python:3.12-slim, already
    cached) with the host root mounted at /host.  This lets users
    navigate the host filesystem from the GUI.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}
    path = body.get("path", "/")
    path = os.path.normpath(path) if path != "/" else "/"

    res = await _docker_host([
        "run", "--rm",
        "-v", "/:/host:ro",
        "python:3.12-slim",
        "ls", "-1p",
        f"/host{path}",
    ], timeout=30)

    if res["exit_code"] != 0:
        stderr = (res.get("stderr") or "").strip()
        return JSONResponse({
            "error": f"cannot list directory: {stderr or 'unknown error'}",
            "path": path,
            "parent": os.path.dirname(path.rstrip("/")) if path != "/" else None,
            "items": [],
        }, status_code=400)

    items = []
    stdout = (res.get("stdout") or "").strip()
    if stdout:
        for line in stdout.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.endswith("/"):
                items.append({"name": line[:-1], "is_dir": True})
            else:
                items.append({"name": line, "is_dir": False})

    parent = os.path.dirname(path.rstrip("/")) if path != "/" else None
    return {"path": path, "parent": parent, "items": items}


# ---------------------------------------------------------------------------
# Run oikb CLI commands inside the oikb container via `docker exec`.
# This gives the GUI the *real* CLI output (file counts, diff, errors)
# that the daemon's async POST /sync/{id} endpoint does not return.
# ---------------------------------------------------------------------------
async def _docker_exec(args: list[str], timeout: float = 120.0) -> dict[str, Any]:
    """Run `docker exec <OIKB_CONTAINER> <args...>` and capture output."""
    cmd = ["docker", "exec", OIKB_CONTAINER] + args
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return {
            "exit_code": proc.returncode,
            "output": out.decode("utf-8", errors="replace"),
        }
    except asyncio.TimeoutError:
        proc.kill()
        return {"exit_code": -1, "output": f"command timed out after {timeout}s"}


@app.post("/run/sync")
async def run_sync(request: Request):
    """Run `oikb sync` in the oikb container.

    Body:
      { "name": "<source name or kb-id>", "dry_run": false }
    If `name` is given, runs `oikb sync --name <name>` (targets one entry in
    .oikb.yaml by name/kb-id). If omitted, runs `oikb sync` (all sources).
    The oikb container's working directory is /data where .oikb.yaml lives.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}
    name = body.get("name")
    dry = bool(body.get("dry_run"))

    args = ["oikb", "sync"]
    if name:
        args += ["--name", str(name)]
    if dry:
        args += ["--dry-run"]

    res = await _docker_exec(args, timeout=float(os.environ.get("OIKB_CLI_TIMEOUT", "120")))
    res["command"] = " ".join(shlex.quote(a) for a in args)
    return res


@app.post("/run/validate")
async def run_validate():
    """Run `oikb validate --deep` in the oikb container."""
    res = await _docker_exec(["oikb", "validate", "--deep", "--config", "/data/.oikb.yaml"])
    res["command"] = "oikb validate --deep"
    return res


# ---------------------------------------------------------------------------
# Volume mounts — manage bind mounts on the oikb container via the Docker
# socket so users can add host directories as local filesystem sources.
# ---------------------------------------------------------------------------
async def _docker_host(args: list[str], timeout: float = 30.0) -> dict[str, Any]:
    """Run a docker CLI command on the host (via mounted /var/run/docker.sock)."""
    cmd = ["docker"] + args
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return {
            "exit_code": proc.returncode,
            "stdout": out.decode("utf-8", errors="replace"),
            "stderr": err.decode("utf-8", errors="replace"),
        }
    except asyncio.TimeoutError:
        proc.kill()
        return {"exit_code": -1, "stdout": "", "stderr": f"timed out after {timeout}s"}


@app.get("/volumes")
async def list_volumes():
    """Return the current bind mounts of the oikb container."""
    res = await _docker_host(["inspect", OIKB_CONTAINER])
    if res["exit_code"] != 0:
        return JSONResponse(
            {"error": f"cannot inspect container {OIKB_CONTAINER}: {res['stderr']}"},
            status_code=502,
        )
    try:
        data = json.loads(res["stdout"])
    except json.JSONDecodeError as exc:
        return JSONResponse({"error": f"invalid inspect output: {exc}"}, status_code=502)

    container = data[0] if isinstance(data, list) else data
    mounts = []
    for m in container.get("Mounts", []):
        if m.get("Type") == "bind":
            mounts.append({
                "host_path": m["Source"],
                "container_path": m["Destination"],
                "read_only": m.get("Mode", "").find("ro") >= 0,
            })
    return {
        "container": OIKB_CONTAINER,
        "mounts": mounts,
        "image": container.get("Config", {}).get("Image", ""),
        "state": container.get("State", {}).get("Status", "unknown"),
    }


@app.post("/volumes")
async def add_volume(request: Request):
    """Add a bind mount to the oikb container (recreates it)."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "body must be JSON"}, status_code=400)

    host_path = body.get("host_path", "").strip()
    container_path = body.get("container_path", "").strip()
    read_only = body.get("read_only", False)

    if not host_path or not container_path:
        return JSONResponse({"error": "host_path and container_path are required"}, status_code=400)

    # Validate the host path exists — use a temporary container that mounts
    # the host root so we check against the real host filesystem (the
    # orchestrator container itself does not see arbitrary host paths).
    check_res = await _docker_host([
        "run", "--rm", "-v", "/:/host:ro",
        "python:3.12-slim",
        "test", "-d", f"/host{host_path}",
    ], timeout=15)
    if check_res["exit_code"] != 0:
        return JSONResponse(
            {"error": f"host path does not exist or is not a directory: {host_path}"},
            status_code=400,
        )

    # Inspect current container config
    res = await _docker_host(["inspect", OIKB_CONTAINER])
    if res["exit_code"] != 0:
        return JSONResponse(
            {"error": f"cannot inspect container {OIKB_CONTAINER}: {res['stderr']}"},
            status_code=502,
        )
    try:
        data = json.loads(res["stdout"])
    except json.JSONDecodeError as exc:
        return JSONResponse({"error": f"invalid inspect output: {exc}"}, status_code=502)

    c = data[0] if isinstance(data, list) else data
    cfg = c.get("Config", {})
    host_cfg = c.get("HostConfig", {})

    # Gather existing bind mounts
    existing_mounts = []
    for m in c.get("Mounts", []):
        if m.get("Type") == "bind":
            existing_mounts.append(f"type=bind,source={m['Source']},destination={m['Destination']}")
        elif m.get("Type") == "volume":
            src = m.get("Source", "")
            dst = m["Destination"]
            if m.get("Mode", "").find("ro") >= 0:
                existing_mounts.append(f"type=volume,source={src},destination={dst},readonly")
            else:
                existing_mounts.append(f"type=volume,source={src},destination={dst}")

    # Add the new mount (skip if already present)
    mount_str = f"type=bind,source={host_path},destination={container_path}"
    if read_only:
        mount_str += ",readonly"
    if mount_str in existing_mounts:
        return JSONResponse({"error": "This mount already exists"}, status_code=409)

    existing_mounts.append(mount_str)

    # Build the recreate command
    image = cfg.get("Image", "")
    cmd = cfg.get("Cmd") or []
    entrypoint = cfg.get("Entrypoint") or []
    env_vars = cfg.get("Env") or []
    ports = host_cfg.get("PortBindings") or {}
    restart_policy = (host_cfg.get("RestartPolicy") or {}).get("Name", "no")
    network_mode = host_cfg.get("NetworkMode") or ""
    extra_hosts = host_cfg.get("ExtraHosts") or []
    ulimits = host_cfg.get("Ulimits") or []

    run_args = ["run", "-d", f"--name={OIKB_CONTAINER}"]

    for env in env_vars:
        run_args.extend(["-e", env])

    for mount_arg in existing_mounts:
        run_args.extend(["--mount", mount_arg])

    # Map ports
    for container_port, bindings in ports.items():
        for b in bindings:
            host_port = b.get("HostPort", "")
            run_args.extend(["-p", f"{host_port}:{container_port.split('/')[0]}"])

    if network_mode and network_mode != "default":
        run_args.extend(["--network", network_mode])

    if restart_policy and restart_policy != "no":
        run_args.extend(["--restart", restart_policy])

    if entrypoint:
        run_args.extend(["--entrypoint"] + entrypoint)

    for host in extra_hosts:
        run_args.extend(["--add-host", host])

    for u in ulimits:
        name = u.get("Name", "")
        soft = u.get("Soft", "")
        hard = u.get("Hard", "")
        if name:
            run_args.extend(["--ulimit", f"{name}={soft}:{hard}"])

    # Healthcheck
    hc = cfg.get("Healthcheck") or {}
    hc_test = hc.get("Test") or []
    if hc_test:
        hc_interval = hc.get("Interval", 0) // 1000000000
        hc_timeout = hc.get("Timeout", 0) // 1000000000
        hc_retries = hc.get("Retries", 0)
        test_str = " ".join(shlex.quote(t) for t in hc_test)
        run_args.extend(["--health-cmd", test_str])
        if hc_interval:
            run_args.extend(["--health-interval", f"{hc_interval}s"])
        if hc_timeout:
            run_args.extend(["--health-timeout", f"{hc_timeout}s"])
        if hc_retries:
            run_args.extend(["--health-retries", str(hc_retries)])

    run_args.append(image)
    run_args.extend(cmd)

    # Stop & remove old container, then create the new one
    await _docker_host(["stop", OIKB_CONTAINER], timeout=30)
    await _docker_host(["rm", OIKB_CONTAINER], timeout=15)

    create_res = await _docker_host(run_args, timeout=60)
    if create_res["exit_code"] != 0:
        # Try to restart old container on failure
        await _docker_host(["start", OIKB_CONTAINER], timeout=15)
        return JSONResponse(
            {"error": f"failed to recreate container: {create_res['stderr']}"},
            status_code=500,
        )

    return {
        "message": f"Mounted {host_path} → {container_path}",
        "container": OIKB_CONTAINER,
        "mount": {"host_path": host_path, "container_path": container_path, "read_only": read_only},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.environ.get("OIKB_GUI_HOST", "0.0.0.0"),
        port=int(os.environ.get("OIKB_GUI_PORT", "8086")),
        log_level=os.environ.get("OIKB_GUI_LOG_LEVEL", "info"),
    )