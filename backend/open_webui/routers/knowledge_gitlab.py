"""BEV overlay — GitLab knowledge-base integration router.

Extracted from ``routers/knowledge.py`` so that upstream knowledge.py
can be refreshed wholesale on upgrade without losing the GitLab feature.
Mounted in ``main.py`` via ``app.include_router(knowledge_gitlab.router)``.
See BEV_CUSTOMIZATIONS.md.
"""

from typing import Optional

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse

import asyncio
import gc
import io
import json
import logging
import time
import uuid
from urllib.parse import quote, urlparse

import requests

from sqlalchemy.ext.asyncio import AsyncSession
from open_webui.internal.db import get_async_session, get_async_db
from open_webui.models.knowledge import (
    Knowledges,
)
from open_webui.models.files import Files, FileForm
from open_webui.routers.retrieval import (
    process_file,
    ProcessFileForm,
)
from open_webui.routers.knowledge import KnowledgeFilesResponse
from open_webui.storage.provider import Storage
from open_webui.constants import ERROR_MESSAGES
from open_webui.utils.auth import get_verified_user
from open_webui.models.access_grants import AccessGrants

log = logging.getLogger(__name__)

router = APIRouter()


############################
# Models
############################


class GitlabForm(BaseModel):
    url: str
    access_token: Optional[str] = None
    branch: Optional[str] = None
    ignored_extensions: Optional[str] = None


class GitlabFileItem(BaseModel):
    filename: str
    content: str


class GitlabProgressEvent(BaseModel):
    phase: str  # 'fetching' | 'processing' | 'done' | 'error'
    current: int = 0
    total: int = 0
    filename: str = ''
    success_count: int = 0
    fail_count: int = 0
    message: str = ''


############################
# GitLab API helpers
############################

GITLAB_API_TIMEOUT = 60
GITLAB_API_RETRIES = 3
GITLAB_API_BACKOFF = 2


def _gitlab_request_with_retry(method, url, **kwargs):
    """Make an HTTP request with retries and exponential backoff."""
    last_exc = None
    for attempt in range(GITLAB_API_RETRIES):
        try:
            response = method(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError as e:
            last_exc = e
            if attempt < GITLAB_API_RETRIES - 1:
                wait = GITLAB_API_BACKOFF ** attempt
                log.warning(f'GitLab API connection error (attempt {attempt + 1}/{GITLAB_API_RETRIES}), retrying in {wait}s: {e}')
                time.sleep(wait)
        except requests.exceptions.Timeout as e:
            last_exc = e
            if attempt < GITLAB_API_RETRIES - 1:
                wait = GITLAB_API_BACKOFF ** attempt
                log.warning(f'GitLab API timeout (attempt {attempt + 1}/{GITLAB_API_RETRIES}), retrying in {wait}s: {e}')
                time.sleep(wait)
        except requests.exceptions.HTTPError:
            raise
    raise last_exc


def _parse_gitlab_url(url: str) -> tuple[str, str, str]:
    """Parse GitLab URL into (base_url, encoded_project_path, raw_project_path)."""
    parsed = urlparse(url)
    base_url = f'{parsed.scheme}://{parsed.netloc}'
    path = parsed.path.strip('/')

    if path.endswith('.git'):
        path = path[:-4]

    # Remove /-/tree/branch/path or /-/wikis/...
    if '/-/' in path:
        path = path.split('/-')[0]

    encoded_path = quote(path, safe='')
    return base_url, encoded_path, path


def _gitlab_api_get(
    base_url: str, endpoint: str, access_token: Optional[str] = None
) -> list | dict:
    """Make a GET request to the GitLab API v4."""
    headers = {}
    if access_token:
        headers['PRIVATE-TOKEN'] = access_token

    url = f'{base_url}/api/v4/{endpoint.lstrip("/")}'
    response = _gitlab_request_with_retry(requests.get, url, headers=headers, timeout=GITLAB_API_TIMEOUT)
    return response.json()


def _gitlab_api_get_raw(
    base_url: str, endpoint: str, access_token: Optional[str] = None
) -> str:
    """Make a GET request to the GitLab API v4 returning raw text."""
    headers = {}
    if access_token:
        headers['PRIVATE-TOKEN'] = access_token

    url = f'{base_url}/api/v4/{endpoint.lstrip("/")}'
    response = _gitlab_request_with_retry(requests.get, url, headers=headers, timeout=GITLAB_API_TIMEOUT)
    return response.text


def _gitlab_list_all(
    base_url: str, endpoint: str, access_token: Optional[str] = None, per_page: int = 100
) -> list:
    """List all items from a paginated GitLab API endpoint."""
    items = []
    page = 1
    while True:
        sep = '&' if '?' in endpoint else '?'
        url_endpoint = f'{endpoint}{sep}page={page}&per_page={per_page}'
        result = _gitlab_api_get(base_url, url_endpoint, access_token)
        if not result:
            break
        items.extend(result)
        if len(result) < per_page:
            break
        page += 1
    return items


def _parse_ignored_extensions(ignored_extensions: Optional[str]) -> set[str]:
    """Parse comma-separated extensions string into a set of lowercase extensions without dots."""
    if not ignored_extensions:
        return set()
    return {ext.strip().lstrip('.').lower() for ext in ignored_extensions.split(',') if ext.strip()}


_BINARY_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'svg', 'ico', 'webp', 'bmp', 'tiff', 'avif',
    'mp3', 'mp4', 'wav', 'avi', 'mov', 'mkv', 'flac', 'ogg', 'wmv', 'webm',
    'zip', 'gz', 'tar', 'rar', '7z', 'bz2', 'xz', 'zst', 'jar', 'war', 'ear',
    'woff', 'woff2', 'ttf', 'otf', 'eot',
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'ods', 'odp',
    'sqlite', 'db', 'dll', 'so', 'dylib', 'exe', 'bin', 'obj', 'o', 'a',
    'lock', 'map', 'pyc', 'pyo', 'class', 'wasm',
}


def _fetch_gitlab_repo_files(
    base_url: str, encoded_project: str, branch: Optional[str] = None, access_token: Optional[str] = None, ignored_extensions: Optional[set[str]] = None
) -> list[GitlabFileItem]:
    """Fetch all text files from a GitLab repository.

    Automatically skips hidden files, common binary formats, and any
    user-specified extensions.
    """
    branch_param = f'ref={quote(branch, safe="")}' if branch else ''
    tree_endpoint = f'projects/{encoded_project}/repository/tree?recursive=true'
    if branch_param:
        tree_endpoint += f'&{branch_param}'

    tree = _gitlab_list_all(base_url, tree_endpoint, access_token)
    skip_ext = _BINARY_EXTENSIONS | (ignored_extensions or set())
    files = []
    skipped = 0

    for entry in tree:
        if entry.get('type') != 'blob':
            continue
        file_path = entry.get('path', '')
        file_name = entry.get('name', '')

        if file_name.startswith('.'):
            continue

        ext = file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
        if ext and ext in skip_ext:
            skipped += 1
            continue

        encoded_file_path = quote(file_path, safe='')
        content_endpoint = f'projects/{encoded_project}/repository/files/{encoded_file_path}/raw'
        if branch_param:
            content_endpoint += f'?{branch_param}'

        try:
            content = _gitlab_api_get_raw(base_url, content_endpoint, access_token)
            files.append(GitlabFileItem(filename=file_path, content=content))
        except Exception as e:
            log.debug(f'Failed to fetch {file_path}: {e}')
            continue

    if skipped:
        log.info(f'Skipped {skipped} files with ignored/binary extensions')
    return files


def _fetch_gitlab_wiki_pages(
    base_url: str, encoded_project: str, access_token: Optional[str] = None
) -> list[GitlabFileItem]:
    """Fetch all wiki pages from a GitLab project wiki.

    Strategy:
    1. List pages with ``with_content=true`` (small page sizes to avoid
       timeouts).  Most pages come back with content inline.
    2. For any page whose content was empty/missing, fetch individually
       via ``wikis/{slug}``.
    3. As a safety net, list all pages *without* content and fetch any
       slugs we haven't seen yet (handles rare cases where the list
       endpoint omits pages).
    """
    files = []
    seen_slugs = {}  # slug -> title

    # Phase 1: bulk-fetch with content
    pages = _gitlab_list_all(
        base_url,
        f'projects/{encoded_project}/wikis?with_content=true',
        access_token,
        per_page=20,
    )

    needs_detail = []
    for page in pages:
        slug = page.get('slug', '')
        title = page.get('title', slug)
        content = page.get('content', '')
        seen_slugs[slug] = title

        if content:
            filename = f'{title}.md' if title else f'{slug}.md'
            files.append(GitlabFileItem(filename=filename, content=content))
        else:
            needs_detail.append((slug, title))

    # Phase 2: fetch pages that lacked content one by one
    for slug, title in needs_detail:
        try:
            page_detail = _gitlab_api_get(
                base_url,
                f'projects/{encoded_project}/wikis/{quote(slug, safe="")}',
                access_token,
            )
            content = page_detail.get('content', '')
        except Exception as e:
            log.warning(f'Failed to fetch wiki page {slug}: {e}')
            continue

        if content:
            filename = f'{title}.md' if title else f'{slug}.md'
            files.append(GitlabFileItem(filename=filename, content=content))

    # Phase 3: discover pages that were absent from the with_content listing
    all_pages = _gitlab_list_all(
        base_url,
        f'projects/{encoded_project}/wikis',
        access_token,
        per_page=100,
    )

    for page in all_pages:
        slug = page.get('slug', '')
        if slug in seen_slugs:
            continue
        title = page.get('title', slug)
        seen_slugs[slug] = title

        try:
            page_detail = _gitlab_api_get(
                base_url,
                f'projects/{encoded_project}/wikis/{quote(slug, safe="")}',
                access_token,
            )
            content = page_detail.get('content', '')
        except Exception as e:
            log.warning(f'Failed to fetch wiki page {slug}: {e}')
            continue

        if content:
            filename = f'{title}.md' if title else f'{slug}.md'
            files.append(GitlabFileItem(filename=filename, content=content))

    return files


############################
# File processing
############################


async def _process_gitlab_files(
    request: Request,
    knowledge_id: str,
    files: list[GitlabFileItem],
    user,
    db: AsyncSession,
    progress_callback=None,
) -> list[str]:
    """Process a list of GitlabFileItem: upload, process, and add to knowledge base.

    Returns list of file IDs that were successfully added.

    If progress_callback is provided, it is called after each file with a dict:
        {phase, current, total, filename, success_count, fail_count}
    """
    total = len(files)
    processed_ids = []
    success_count = 0
    fail_count = 0

    for idx, item in enumerate(files, start=1):
        try:
            if progress_callback:
                await progress_callback({
                    'phase': 'processing',
                    'current': idx,
                    'total': total,
                    'filename': item.filename,
                    'success_count': success_count,
                    'fail_count': fail_count,
                })

            content_bytes = item.content.encode('utf-8')
            file_id = str(uuid.uuid4())
            name = item.filename
            storage_name = f'{file_id}_{name.replace("/", "__")}'

            contents, file_path = await asyncio.to_thread(
                Storage.upload_file,
                io.BytesIO(content_bytes),
                storage_name,
                {
                    'OpenWebUI-User-Email': user.email,
                    'OpenWebUI-User-Id': user.id,
                    'OpenWebUI-User-Name': user.name,
                    'OpenWebUI-File-Id': file_id,
                },
            )

            file_item = await Files.insert_new_file(
                user.id,
                FileForm(
                    **{
                        'id': file_id,
                        'filename': name,
                        'path': file_path,
                        'data': {
                            'content': item.content,
                            'status': 'pending',
                        },
                        'meta': {
                            'name': name,
                            'content_type': 'text/plain',
                            'size': len(content_bytes),
                            'source': f'gitlab:{knowledge_id}',
                        },
                    }
                ),
                db=db,
            )

            if not file_item:
                log.warning(f'Failed to create file record for {name}')
                fail_count += 1
                if progress_callback:
                    await progress_callback({
                        'phase': 'processing',
                        'current': idx,
                        'total': total,
                        'filename': item.filename,
                        'success_count': success_count,
                        'fail_count': fail_count,
                    })
                continue

            await process_file(
                request,
                ProcessFileForm(file_id=file_item.id, content=item.content, collection_name=knowledge_id),
                user=user,
                db=db,
            )

            await Knowledges.add_file_to_knowledge_by_id(
                knowledge_id=knowledge_id, file_id=file_item.id, user_id=user.id, db=db
            )

            processed_ids.append(file_item.id)
            success_count += 1

        except HTTPException as e:
            if 'Duplicate content' in str(e.detail):
                log.info(f'Skipping duplicate GitLab file {item.filename}')
                if file_item and file_item.id:
                    try:
                        async with get_async_db() as cleanup_session:
                            await Files.delete_file_by_id(file_item.id, db=cleanup_session)
                    except Exception:
                        pass
                continue
            log.warning(f'Failed to process GitLab file {item.filename}: {e.detail}')
            fail_count += 1
            continue
        except Exception as e:
            log.warning(f'Failed to process GitLab file {item.filename}: {e}')
            fail_count += 1
            continue
        finally:
            gc.collect()
            await asyncio.sleep(0)

    return processed_ids


############################
# Streaming generator
############################


async def _gitlab_stream_generator(request, id, form_data, user, db, source_type):
    knowledge = await Knowledges.get_knowledge_by_id(id=id, db=db)
    if not knowledge:
        yield f'data: {json.dumps(GitlabProgressEvent(phase="error", message="Knowledge base not found").model_dump())}\n\n'
        return

    if (
        knowledge.user_id != user.id
        and not await AccessGrants.has_access(
            user_id=user.id, resource_type='knowledge', resource_id=knowledge.id, permission='write', db=db
        )
        and user.role != 'admin'
    ):
        yield f'data: {json.dumps(GitlabProgressEvent(phase="error", message="Access prohibited").model_dump())}\n\n'
        return

    try:
        base_url, encoded_project, _ = _parse_gitlab_url(form_data.url)

        source_label = 'files' if source_type == 'repo' else 'pages'
        fetching_msg = f"Fetching {source_type} from GitLab..."
        yield f'data: {json.dumps(GitlabProgressEvent(phase="fetching", message=fetching_msg).model_dump())}\n\n'

        if source_type == 'repo':
            ignored_ext = _parse_ignored_extensions(form_data.ignored_extensions)
            files = await asyncio.to_thread(
                _fetch_gitlab_repo_files, base_url, encoded_project, form_data.branch, form_data.access_token, ignored_ext
            )
        else:
            files = await asyncio.to_thread(
                _fetch_gitlab_wiki_pages, base_url, encoded_project, form_data.access_token
            )

        if not files:
            not_found_msg = f"No {'files' if source_type == 'repo' else 'wiki pages'} found"
            yield f'data: {json.dumps(GitlabProgressEvent(phase="error", message=not_found_msg).model_dump())}\n\n'
            return

        total = len(files)
        source_label = 'files' if source_type == 'repo' else 'pages'
        processing_msg = f"Found {total} {source_label}, starting to process..."
        yield f'data: {json.dumps(GitlabProgressEvent(phase="processing", current=0, total=total, message=processing_msg).model_dump())}\n\n'

        progress_queue = asyncio.Queue()

        async def progress_callback(event):
            await progress_queue.put(event)

        async def process_task():
            try:
                result = await _process_gitlab_files(request, id, files, user, db, progress_callback=progress_callback)
                return result
            except Exception as e:
                await progress_queue.put({'phase': 'task_error', 'message': str(e)})
                return []
            finally:
                await progress_queue.put(None)

        task = asyncio.create_task(process_task())

        processed_ids = []
        try:
            while True:
                try:
                    event = await asyncio.wait_for(progress_queue.get(), timeout=60)
                except asyncio.TimeoutError:
                    yield f'data: {json.dumps(GitlabProgressEvent(phase="processing", message="Still processing...").model_dump())}\n\n'
                    continue

                if event is None:
                    break

                if isinstance(event, dict) and event.get('phase') == 'task_error':
                    yield f'data: {json.dumps(GitlabProgressEvent(phase="error", message=event.get("message", "Unknown error")).model_dump())}\n\n'
                    return

                yield f'data: {json.dumps(GitlabProgressEvent(**event).model_dump())}\n\n'
        finally:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        try:
            if not task.cancelled():
                processed_ids = task.result() or []
        except Exception:
            processed_ids = []

        if not processed_ids:
            yield f'data: {json.dumps(GitlabProgressEvent(phase="error", message="Failed to process any files").model_dump())}\n\n'
            return

        file_metadatas = await Knowledges.get_file_metadatas_by_id(knowledge.id, db=db)
        result = KnowledgeFilesResponse(
            **knowledge.model_dump(),
            files=file_metadatas,
        )
        done_data = json.dumps({
            'phase': 'done',
            'success_count': len(processed_ids),
            'fail_count': total - len(processed_ids),
            'total': total,
            'result': result.model_dump(),
        })
        yield f'data: {done_data}\n\n'

    except HTTPException as e:
        yield f'data: {json.dumps(GitlabProgressEvent(phase="error", message=str(e.detail)).model_dump())}\n\n'
    except Exception as e:
        log.error(f'GitLab {source_type} import failed: {e}')
        yield f'data: {json.dumps(GitlabProgressEvent(phase="error", message=str(e)).model_dump())}\n\n'


############################
# Endpoints
############################


@router.post('/{id}/gitlab/repo/stream')
async def add_gitlab_repo_to_knowledge_stream(
    request: Request,
    id: str,
    form_data: GitlabForm,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    return StreamingResponse(
        _gitlab_stream_generator(request, id, form_data, user, db, 'repo'),
        media_type='text/event-stream',
    )


@router.post('/{id}/gitlab/wiki/stream')
async def add_gitlab_wiki_to_knowledge_stream(
    request: Request,
    id: str,
    form_data: GitlabForm,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    return StreamingResponse(
        _gitlab_stream_generator(request, id, form_data, user, db, 'wiki'),
        media_type='text/event-stream',
    )


@router.post('/{id}/gitlab/repo', response_model=Optional[KnowledgeFilesResponse])
async def add_gitlab_repo_to_knowledge(
    request: Request,
    id: str,
    form_data: GitlabForm,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Fetch a GitLab repository and add its files to the knowledge base."""

    knowledge = await Knowledges.get_knowledge_by_id(id=id, db=db)
    if not knowledge:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.NOT_FOUND)

    if (
        knowledge.user_id != user.id
        and not await AccessGrants.has_access(
            user_id=user.id, resource_type='knowledge', resource_id=knowledge.id, permission='write', db=db
        )
        and user.role != 'admin'
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.ACCESS_PROHIBITED)

    try:
        base_url, encoded_project, _ = _parse_gitlab_url(form_data.url)
        ignored_ext = _parse_ignored_extensions(form_data.ignored_extensions)
        files = await asyncio.to_thread(
            _fetch_gitlab_repo_files, base_url, encoded_project, form_data.branch, form_data.access_token, ignored_ext
        )

        if not files:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No files found in repository')

        processed_ids = await _process_gitlab_files(request, id, files, user, db)

        if not processed_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Failed to process any files')

        return KnowledgeFilesResponse(
            **knowledge.model_dump(),
            files=await Knowledges.get_file_metadatas_by_id(knowledge.id, db=db),
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f'GitLab repo import failed: {e}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/{id}/gitlab/wiki', response_model=Optional[KnowledgeFilesResponse])
async def add_gitlab_wiki_to_knowledge(
    request: Request,
    id: str,
    form_data: GitlabForm,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Fetch a GitLab project wiki and add its pages to the knowledge base."""

    knowledge = await Knowledges.get_knowledge_by_id(id=id, db=db)
    if not knowledge:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.NOT_FOUND)

    if (
        knowledge.user_id != user.id
        and not await AccessGrants.has_access(
            user_id=user.id, resource_type='knowledge', resource_id=knowledge.id, permission='write', db=db
        )
        and user.role != 'admin'
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.ACCESS_PROHIBITED)

    try:
        base_url, encoded_project, _ = _parse_gitlab_url(form_data.url)
        files = await asyncio.to_thread(
            _fetch_gitlab_wiki_pages, base_url, encoded_project, form_data.access_token
        )

        if not files:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No wiki pages found')

        processed_ids = await _process_gitlab_files(request, id, files, user, db)

        if not processed_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Failed to process any wiki pages')

        return KnowledgeFilesResponse(
            **knowledge.model_dump(),
            files=await Knowledges.get_file_metadatas_by_id(knowledge.id, db=db),
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f'GitLab wiki import failed: {e}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))