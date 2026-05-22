from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import StreamingResponse

import asyncio
import gc
import io
import json
import logging
import time
import uuid
import zipfile
from urllib.parse import quote, urlparse
import requests

from sqlalchemy.ext.asyncio import AsyncSession
from open_webui.internal.db import get_async_session, get_async_db
from open_webui.models.groups import Groups
from open_webui.models.knowledge import (
    KnowledgeFileListResponse,
    Knowledges,
    KnowledgeForm,
    KnowledgeResponse,
    KnowledgeUserResponse,
)
from open_webui.models.files import Files, FileForm, FileModel, FileMetadataResponse
from open_webui.retrieval.vector.async_client import ASYNC_VECTOR_DB_CLIENT
from open_webui.routers.retrieval import (
    process_file,
    ProcessFileForm,
    process_files_batch,
    BatchProcessFilesForm,
)
from open_webui.storage.provider import Storage

from open_webui.constants import ERROR_MESSAGES
from open_webui.utils.auth import get_verified_user, get_admin_user
from open_webui.utils.access_control import has_permission, filter_allowed_access_grants
from open_webui.utils.access_control.files import has_access_to_file
from open_webui.models.access_grants import AccessGrants


from open_webui.config import BYPASS_ADMIN_ACCESS_CONTROL
from open_webui.models.models import Models, ModelForm

log = logging.getLogger(__name__)

router = APIRouter()

############################
# getKnowledgeBases
############################

PAGE_ITEM_COUNT = 30

############################
# Knowledge Base Embedding
############################

# Knowledge that sits unread serves no one. Let what is
# stored here find the ones who need it.
KNOWLEDGE_BASES_COLLECTION = 'knowledge-bases'


async def embed_knowledge_base_metadata(
    request: Request,
    knowledge_base_id: str,
    name: str,
    description: str,
) -> bool:
    """Generate and store embedding for knowledge base."""
    try:
        content = f'{name}\n\n{description}' if description else name
        embedding = await request.app.state.EMBEDDING_FUNCTION(content)
        await ASYNC_VECTOR_DB_CLIENT.upsert(
            collection_name=KNOWLEDGE_BASES_COLLECTION,
            items=[
                {
                    'id': knowledge_base_id,
                    'text': content,
                    'vector': embedding,
                    'metadata': {
                        'knowledge_base_id': knowledge_base_id,
                    },
                }
            ],
        )
        return True
    except Exception as e:
        log.error(f'Failed to embed knowledge base {knowledge_base_id}: {e}')
        return False


async def remove_knowledge_base_metadata_embedding(knowledge_base_id: str) -> bool:
    """Remove knowledge base embedding."""
    try:
        await ASYNC_VECTOR_DB_CLIENT.delete(
            collection_name=KNOWLEDGE_BASES_COLLECTION,
            ids=[knowledge_base_id],
        )
        return True
    except Exception as e:
        log.debug(f'Failed to remove embedding for {knowledge_base_id}: {e}')
        return False


class KnowledgeAccessResponse(KnowledgeUserResponse):
    write_access: Optional[bool] = False


class KnowledgeAccessListResponse(BaseModel):
    items: list[KnowledgeAccessResponse]
    total: int


@router.get('/', response_model=KnowledgeAccessListResponse)
async def get_knowledge_bases(
    page: Optional[int] = 1,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    page = max(page, 1)
    limit = PAGE_ITEM_COUNT
    skip = (page - 1) * limit

    filter = {}
    groups = await Groups.get_groups_by_member_id(user.id, db=db)
    user_group_ids = {group.id for group in groups}

    if not user.role == 'admin' or not BYPASS_ADMIN_ACCESS_CONTROL:
        if groups:
            filter['group_ids'] = [group.id for group in groups]

        filter['user_id'] = user.id

    result = await Knowledges.search_knowledge_bases(user.id, filter=filter, skip=skip, limit=limit, db=db)

    # Batch-fetch writable knowledge IDs in a single query instead of N has_access calls
    knowledge_base_ids = [knowledge_base.id for knowledge_base in result.items]
    writable_knowledge_base_ids = await AccessGrants.get_accessible_resource_ids(
        user_id=user.id,
        resource_type='knowledge',
        resource_ids=knowledge_base_ids,
        permission='write',
        user_group_ids=user_group_ids,
        db=db,
    )

    return KnowledgeAccessListResponse(
        items=[
            KnowledgeAccessResponse(
                **knowledge_base.model_dump(),
                write_access=(
                    user.id == knowledge_base.user_id
                    or (user.role == 'admin' and BYPASS_ADMIN_ACCESS_CONTROL)
                    or knowledge_base.id in writable_knowledge_base_ids
                ),
            )
            for knowledge_base in result.items
        ],
        total=result.total,
    )


@router.get('/search', response_model=KnowledgeAccessListResponse)
async def search_knowledge_bases(
    query: Optional[str] = None,
    view_option: Optional[str] = None,
    page: Optional[int] = 1,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    page = max(page, 1)
    limit = PAGE_ITEM_COUNT
    skip = (page - 1) * limit

    filter = {}
    if query:
        filter['query'] = query
    if view_option:
        filter['view_option'] = view_option

    groups = await Groups.get_groups_by_member_id(user.id, db=db)
    user_group_ids = {group.id for group in groups}

    if not user.role == 'admin' or not BYPASS_ADMIN_ACCESS_CONTROL:
        if groups:
            filter['group_ids'] = [group.id for group in groups]

        filter['user_id'] = user.id

    result = await Knowledges.search_knowledge_bases(user.id, filter=filter, skip=skip, limit=limit, db=db)

    # Batch-fetch writable knowledge IDs in a single query instead of N has_access calls
    knowledge_base_ids = [knowledge_base.id for knowledge_base in result.items]
    writable_knowledge_base_ids = await AccessGrants.get_accessible_resource_ids(
        user_id=user.id,
        resource_type='knowledge',
        resource_ids=knowledge_base_ids,
        permission='write',
        user_group_ids=user_group_ids,
        db=db,
    )

    return KnowledgeAccessListResponse(
        items=[
            KnowledgeAccessResponse(
                **knowledge_base.model_dump(),
                write_access=(
                    user.id == knowledge_base.user_id
                    or (user.role == 'admin' and BYPASS_ADMIN_ACCESS_CONTROL)
                    or knowledge_base.id in writable_knowledge_base_ids
                ),
            )
            for knowledge_base in result.items
        ],
        total=result.total,
    )


@router.get('/search/files', response_model=KnowledgeFileListResponse)
async def search_knowledge_files(
    query: Optional[str] = None,
    page: Optional[int] = 1,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    page = max(page, 1)
    limit = PAGE_ITEM_COUNT
    skip = (page - 1) * limit

    filter = {}
    if query:
        filter['query'] = query

    groups = await Groups.get_groups_by_member_id(user.id, db=db)
    if groups:
        filter['group_ids'] = [group.id for group in groups]

    filter['user_id'] = user.id

    return await Knowledges.search_knowledge_files(filter=filter, skip=skip, limit=limit, db=db)


############################
# CreateNewKnowledge
############################


@router.post('/create', response_model=Optional[KnowledgeResponse])
async def create_new_knowledge(
    request: Request,
    form_data: KnowledgeForm,
    user=Depends(get_verified_user),
):
    # NOTE: We intentionally do NOT use Depends(get_async_session) here.
    # Database operations (has_permission, filter_allowed_access_grants, insert_new_knowledge) manage their own sessions.
    # This prevents holding a connection during embed_knowledge_base_metadata()
    # which makes external embedding API calls (1-5+ seconds).
    if user.role != 'admin' and not await has_permission(
        user.id, 'workspace.knowledge', request.app.state.config.USER_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    form_data.access_grants = await filter_allowed_access_grants(
        request.app.state.config.USER_PERMISSIONS,
        user.id,
        user.role,
        form_data.access_grants,
        'sharing.public_knowledge',
    )

    knowledge = await Knowledges.insert_new_knowledge(user.id, form_data)

    if knowledge:
        # Embed knowledge base for semantic search
        await embed_knowledge_base_metadata(
            request,
            knowledge.id,
            knowledge.name,
            knowledge.description,
        )
        return knowledge
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.FILE_EXISTS,
        )


############################
# ReindexKnowledgeFiles
############################


@router.post('/reindex', response_model=bool)
async def reindex_knowledge_files(
    request: Request,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    knowledge_bases = await Knowledges.get_knowledge_bases(db=db)

    log.info(f'Starting reindexing for {len(knowledge_bases)} knowledge bases')

    for knowledge_base in knowledge_bases:
        try:
            files = await Knowledges.get_files_by_id(knowledge_base.id, db=db)
            try:
                if await ASYNC_VECTOR_DB_CLIENT.has_collection(collection_name=knowledge_base.id):
                    await ASYNC_VECTOR_DB_CLIENT.delete_collection(collection_name=knowledge_base.id)
            except Exception as e:
                log.error(f'Error deleting collection {knowledge_base.id}: {str(e)}')
                continue  # Skip, don't raise

            failed_files = []
            for file in files:
                try:
                    await process_file(
                        request,
                        ProcessFileForm(file_id=file.id, collection_name=knowledge_base.id),
                        user=user,
                        db=db,
                    )
                except Exception as e:
                    log.error(f'Error processing file {file.filename} (ID: {file.id}): {str(e)}')
                    failed_files.append({'file_id': file.id, 'error': str(e)})
                    continue

        except Exception as e:
            log.error(f'Error processing knowledge base {knowledge_base.id}: {str(e)}')
            # Don't raise, just continue
            continue

        if failed_files:
            log.warning(f'Failed to process {len(failed_files)} files in knowledge base {knowledge_base.id}')
            for failed in failed_files:
                log.warning(f'File ID: {failed["file_id"]}, Error: {failed["error"]}')

    log.info(f'Reindexing completed.')
    return True


############################
# ReindexKnowledgeBases
############################


@router.post('/metadata/reindex', response_model=dict)
async def reindex_knowledge_base_metadata_embeddings(
    request: Request,
    user=Depends(get_admin_user),
):
    """Batch embed all existing knowledge bases. Admin only.

    NOTE: We intentionally do NOT use Depends(get_async_session) here.
    This endpoint loops through ALL knowledge bases and calls embed_knowledge_base_metadata()
    for each one, making N external embedding API calls. Holding a session during
    this entire operation would exhaust the connection pool.
    """
    knowledge_bases = await Knowledges.get_knowledge_bases()
    log.info(f'Reindexing embeddings for {len(knowledge_bases)} knowledge bases')

    success_count = 0
    for kb in knowledge_bases:
        if await embed_knowledge_base_metadata(request, kb.id, kb.name, kb.description):
            success_count += 1

    log.info(f'Embedding reindex complete: {success_count}/{len(knowledge_bases)}')
    return {'total': len(knowledge_bases), 'success': success_count}


############################
# GetKnowledgeById
############################


class KnowledgeFilesResponse(KnowledgeResponse):
    files: Optional[list[FileMetadataResponse]] = None
    write_access: Optional[bool] = False


@router.get('/{id}', response_model=Optional[KnowledgeFilesResponse])
async def get_knowledge_by_id(id: str, user=Depends(get_verified_user), db: AsyncSession = Depends(get_async_session)):
    knowledge = await Knowledges.get_knowledge_by_id(id=id, db=db)

    if knowledge:
        if (
            user.role == 'admin'
            or knowledge.user_id == user.id
            or await AccessGrants.has_access(
                user_id=user.id,
                resource_type='knowledge',
                resource_id=knowledge.id,
                permission='read',
                db=db,
            )
        ):
            return KnowledgeFilesResponse(
                **knowledge.model_dump(),
                write_access=(
                    user.id == knowledge.user_id
                    or (user.role == 'admin' and BYPASS_ADMIN_ACCESS_CONTROL)
                    or await AccessGrants.has_access(
                        user_id=user.id,
                        resource_type='knowledge',
                        resource_id=knowledge.id,
                        permission='write',
                        db=db,
                    )
                ),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# UpdateKnowledgeById
############################


@router.post('/{id}/update', response_model=Optional[KnowledgeFilesResponse])
async def update_knowledge_by_id(
    request: Request,
    id: str,
    form_data: KnowledgeForm,
    user=Depends(get_verified_user),
):
    # NOTE: We intentionally do NOT use Depends(get_async_session) here.
    # Database operations manage their own short-lived sessions internally.
    # This prevents holding a connection during embed_knowledge_base_metadata()
    # which makes external embedding API calls (1-5+ seconds).
    knowledge = await Knowledges.get_knowledge_by_id(id=id)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
    # Is the user the original creator, in a group with write access, or an admin
    if (
        knowledge.user_id != user.id
        and not await AccessGrants.has_access(
            user_id=user.id,
            resource_type='knowledge',
            resource_id=knowledge.id,
            permission='write',
        )
        and user.role != 'admin'
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    form_data.access_grants = await filter_allowed_access_grants(
        request.app.state.config.USER_PERMISSIONS,
        user.id,
        user.role,
        form_data.access_grants,
        'sharing.public_knowledge',
    )

    knowledge = await Knowledges.update_knowledge_by_id(id=id, form_data=form_data)
    if knowledge:
        # Re-embed knowledge base for semantic search
        await embed_knowledge_base_metadata(
            request,
            knowledge.id,
            knowledge.name,
            knowledge.description,
        )
        return KnowledgeFilesResponse(
            **knowledge.model_dump(),
            files=await Knowledges.get_file_metadatas_by_id(knowledge.id),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ID_TAKEN,
        )


############################
# UpdateKnowledgeAccessById
############################


class KnowledgeAccessGrantsForm(BaseModel):
    access_grants: list[dict]


@router.post('/{id}/access/update', response_model=Optional[KnowledgeFilesResponse])
async def update_knowledge_access_by_id(
    request: Request,
    id: str,
    form_data: KnowledgeAccessGrantsForm,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    knowledge = await Knowledges.get_knowledge_by_id(id=id, db=db)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if (
        knowledge.user_id != user.id
        and not await AccessGrants.has_access(
            user_id=user.id,
            resource_type='knowledge',
            resource_id=knowledge.id,
            permission='write',
            db=db,
        )
        and user.role != 'admin'
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    form_data.access_grants = await filter_allowed_access_grants(
        request.app.state.config.USER_PERMISSIONS,
        user.id,
        user.role,
        form_data.access_grants,
        'sharing.public_knowledge',
    )

    knowledge.access_grants = await AccessGrants.set_access_grants('knowledge', id, form_data.access_grants, db=db)

    return KnowledgeFilesResponse(
        **knowledge.model_dump(),
        files=await Knowledges.get_file_metadatas_by_id(id, db=db),
    )


############################
# GetKnowledgeFilesById
############################


@router.get('/{id}/files', response_model=KnowledgeFileListResponse)
async def get_knowledge_files_by_id(
    id: str,
    query: Optional[str] = None,
    view_option: Optional[str] = None,
    order_by: Optional[str] = None,
    direction: Optional[str] = None,
    page: Optional[int] = 1,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    knowledge = await Knowledges.get_knowledge_by_id(id=id, db=db)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if not (
        user.role == 'admin'
        or knowledge.user_id == user.id
        or await AccessGrants.has_access(
            user_id=user.id,
            resource_type='knowledge',
            resource_id=knowledge.id,
            permission='read',
            db=db,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    page = max(page, 1)

    limit = 30
    skip = (page - 1) * limit

    filter = {}
    if query:
        filter['query'] = query
    if view_option:
        filter['view_option'] = view_option
    if order_by:
        filter['order_by'] = order_by
    if direction:
        filter['direction'] = direction

    return await Knowledges.search_files_by_id(id, user.id, filter=filter, skip=skip, limit=limit, db=db)


############################
# AddFileToKnowledge
############################


class KnowledgeFileIdForm(BaseModel):
    file_id: str


@router.post('/{id}/file/add', response_model=Optional[KnowledgeFilesResponse])
async def add_file_to_knowledge_by_id(
    request: Request,
    id: str,
    form_data: KnowledgeFileIdForm,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    knowledge = await Knowledges.get_knowledge_by_id(id=id, db=db)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if (
        knowledge.user_id != user.id
        and not await AccessGrants.has_access(
            user_id=user.id,
            resource_type='knowledge',
            resource_id=knowledge.id,
            permission='write',
            db=db,
        )
        and user.role != 'admin'
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    file = await Files.get_file_by_id(form_data.file_id, db=db)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
    if not file.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.FILE_NOT_PROCESSED,
        )

    # KB write-access alone is not enough — caller must also be able to read the file.
    if file.user_id != user.id and user.role != 'admin':
        if not await has_access_to_file(file.id, 'read', user, db=db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
            )

    # Add content to the vector database
    try:
        await process_file(
            request,
            ProcessFileForm(file_id=form_data.file_id, collection_name=id),
            user=user,
            db=db,
        )

        # Add file to knowledge base
        await Knowledges.add_file_to_knowledge_by_id(knowledge_id=id, file_id=form_data.file_id, user_id=user.id, db=db)
    except Exception as e:
        log.debug(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if knowledge:
        return KnowledgeFilesResponse(
            **knowledge.model_dump(),
            files=await Knowledges.get_file_metadatas_by_id(knowledge.id, db=db),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


@router.post('/{id}/file/update', response_model=Optional[KnowledgeFilesResponse])
async def update_file_from_knowledge_by_id(
    request: Request,
    id: str,
    form_data: KnowledgeFileIdForm,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    knowledge = await Knowledges.get_knowledge_by_id(id=id, db=db)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if (
        knowledge.user_id != user.id
        and not await AccessGrants.has_access(
            user_id=user.id,
            resource_type='knowledge',
            resource_id=knowledge.id,
            permission='write',
            db=db,
        )
        and user.role != 'admin'
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    file = await Files.get_file_by_id(form_data.file_id, db=db)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    # Validate the file actually belongs to this knowledge base
    if not await Knowledges.has_file(knowledge_id=id, file_id=form_data.file_id, db=db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    # Remove content from the vector database
    await ASYNC_VECTOR_DB_CLIENT.delete(collection_name=knowledge.id, filter={'file_id': form_data.file_id})

    # Add content to the vector database
    try:
        await process_file(
            request,
            ProcessFileForm(file_id=form_data.file_id, collection_name=id),
            user=user,
            db=db,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if knowledge:
        return KnowledgeFilesResponse(
            **knowledge.model_dump(),
            files=await Knowledges.get_file_metadatas_by_id(knowledge.id, db=db),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# RemoveFileFromKnowledge
############################


@router.post('/{id}/file/remove', response_model=Optional[KnowledgeFilesResponse])
async def remove_file_from_knowledge_by_id(
    id: str,
    form_data: KnowledgeFileIdForm,
    delete_file: bool = Query(True),
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    knowledge = await Knowledges.get_knowledge_by_id(id=id, db=db)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if (
        knowledge.user_id != user.id
        and not await AccessGrants.has_access(
            user_id=user.id,
            resource_type='knowledge',
            resource_id=knowledge.id,
            permission='write',
            db=db,
        )
        and user.role != 'admin'
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    file = await Files.get_file_by_id(form_data.file_id, db=db)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    # Validate the file actually belongs to this knowledge base
    if not await Knowledges.has_file(knowledge_id=id, file_id=form_data.file_id, db=db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    await Knowledges.remove_file_from_knowledge_by_id(knowledge_id=id, file_id=form_data.file_id, db=db)

    # Remove content from the vector database
    try:
        await ASYNC_VECTOR_DB_CLIENT.delete(
            collection_name=knowledge.id, filter={'file_id': form_data.file_id}
        )  # Remove by file_id first

        await ASYNC_VECTOR_DB_CLIENT.delete(
            collection_name=knowledge.id, filter={'hash': file.hash}
        )  # Remove by hash as well in case of duplicates
    except Exception as e:
        log.debug('This was most likely caused by bypassing embedding processing')
        log.debug(e)
        pass

    # Only the file owner or an admin may permanently delete the underlying
    # file.  Collaborators with KB write access can unlink a file from the
    # knowledge base but must not be able to destroy files they do not own,
    # as the same file may be referenced by other KBs and chats.
    if delete_file and (file.user_id == user.id or user.role == 'admin'):
        try:
            # Remove the file's collection from vector database
            file_collection = f'file-{form_data.file_id}'
            if await ASYNC_VECTOR_DB_CLIENT.has_collection(collection_name=file_collection):
                await ASYNC_VECTOR_DB_CLIENT.delete_collection(collection_name=file_collection)
        except Exception as e:
            log.debug('This was most likely caused by bypassing embedding processing')
            log.debug(e)
            pass

        # Delete file from database
        await Files.delete_file_by_id(form_data.file_id, db=db)

    if knowledge:
        return KnowledgeFilesResponse(
            **knowledge.model_dump(),
            files=await Knowledges.get_file_metadatas_by_id(knowledge.id, db=db),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# DeleteKnowledgeById
############################


@router.delete('/{id}/delete', response_model=bool)
async def delete_knowledge_by_id(
    id: str, user=Depends(get_verified_user), db: AsyncSession = Depends(get_async_session)
):
    knowledge = await Knowledges.get_knowledge_by_id(id=id, db=db)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if (
        knowledge.user_id != user.id
        and not await AccessGrants.has_access(
            user_id=user.id,
            resource_type='knowledge',
            resource_id=knowledge.id,
            permission='write',
            db=db,
        )
        and user.role != 'admin'
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    log.info(f'Deleting knowledge base: {id} (name: {knowledge.name})')

    # Get all models
    models = await Models.get_all_models(db=db)
    log.info(f'Found {len(models)} models to check for knowledge base {id}')

    # Update models that reference this knowledge base
    for model in models:
        if model.meta and hasattr(model.meta, 'knowledge'):
            knowledge_list = model.meta.knowledge or []
            # Filter out the deleted knowledge base
            updated_knowledge = [k for k in knowledge_list if k.get('id') != id]

            # If the knowledge list changed, update the model
            if len(updated_knowledge) != len(knowledge_list):
                log.info(f'Updating model {model.id} to remove knowledge base {id}')
                model.meta.knowledge = updated_knowledge
                model_form = ModelForm(**model.model_dump())
                await Models.update_model_by_id(model.id, model_form, db=db)

    # Clean up vector DB
    try:
        await ASYNC_VECTOR_DB_CLIENT.delete_collection(collection_name=id)
    except Exception as e:
        log.debug(e)
        pass

    # Remove knowledge base embedding
    await remove_knowledge_base_metadata_embedding(id)

    result = await Knowledges.delete_knowledge_by_id(id=id, db=db)
    return result


############################
# ResetKnowledgeById
############################


@router.post('/{id}/reset', response_model=Optional[KnowledgeResponse])
async def reset_knowledge_by_id(
    id: str, user=Depends(get_verified_user), db: AsyncSession = Depends(get_async_session)
):
    knowledge = await Knowledges.get_knowledge_by_id(id=id, db=db)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if (
        knowledge.user_id != user.id
        and not await AccessGrants.has_access(
            user_id=user.id,
            resource_type='knowledge',
            resource_id=knowledge.id,
            permission='write',
            db=db,
        )
        and user.role != 'admin'
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    try:
        await ASYNC_VECTOR_DB_CLIENT.delete_collection(collection_name=id)
    except Exception as e:
        log.debug(e)
        pass

    knowledge = await Knowledges.reset_knowledge_by_id(id=id, db=db)
    return knowledge


############################
# AddFilesToKnowledge
############################


@router.post('/{id}/files/batch/add', response_model=Optional[KnowledgeFilesResponse])
async def add_files_to_knowledge_batch(
    request: Request,
    id: str,
    form_data: list[KnowledgeFileIdForm],
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Add multiple files to a knowledge base
    """
    knowledge = await Knowledges.get_knowledge_by_id(id=id, db=db)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if (
        knowledge.user_id != user.id
        and not await AccessGrants.has_access(
            user_id=user.id,
            resource_type='knowledge',
            resource_id=knowledge.id,
            permission='write',
            db=db,
        )
        and user.role != 'admin'
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    # Batch-fetch all files to avoid N+1 queries
    log.info(f'files/batch/add - {len(form_data)} files')
    file_ids = [form.file_id for form in form_data]
    files = await Files.get_files_by_ids(file_ids, db=db)

    # Verify all requested files were found
    found_ids = {file.id for file in files}
    missing_ids = [fid for fid in file_ids if fid not in found_ids]
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'File {missing_ids[0]} not found',
        )

    # Per-file read-access check — same gate as the single-file endpoint.
    if user.role != 'admin':
        for file in files:
            if file.user_id != user.id and not await has_access_to_file(file.id, 'read', user, db=db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
                )

    # Process files
    try:
        result = await process_files_batch(
            request=request,
            form_data=BatchProcessFilesForm(files=files, collection_name=id),
            user=user,
            db=db,
        )
    except Exception as e:
        log.error(f'add_files_to_knowledge_batch: Exception occurred: {e}', exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Only add files that were successfully processed
    successful_file_ids = [r.file_id for r in result.results if r.status == 'completed']
    for file_id in successful_file_ids:
        await Knowledges.add_file_to_knowledge_by_id(knowledge_id=id, file_id=file_id, user_id=user.id, db=db)

    # If there were any errors, include them in the response
    if result.errors:
        error_details = [f'{err.file_id}: {err.error}' for err in result.errors]
        return KnowledgeFilesResponse(
            **knowledge.model_dump(),
            files=await Knowledges.get_file_metadatas_by_id(knowledge.id, db=db),
            warnings={
                'message': 'Some files failed to process',
                'errors': error_details,
            },
        )

    return KnowledgeFilesResponse(
        **knowledge.model_dump(),
        files=await Knowledges.get_file_metadatas_by_id(knowledge.id, db=db),
    )


############################
# GitLab Integration
############################


class GitlabForm(BaseModel):
    url: str
    access_token: Optional[str] = None
    branch: Optional[str] = None
    ignored_extensions: Optional[str] = None


class GitlabFileItem(BaseModel):
    filename: str
    content: str


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


class GitlabProgressEvent(BaseModel):
    phase: str  # 'fetching' | 'processing' | 'done' | 'error'
    current: int = 0
    total: int = 0
    filename: str = ''
    success_count: int = 0
    fail_count: int = 0
    message: str = ''


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


############################
# ExportKnowledgeById
############################


@router.get('/{id}/export')
async def export_knowledge_by_id(id: str, user=Depends(get_admin_user), db: AsyncSession = Depends(get_async_session)):
    """
    Export a knowledge base as a zip file containing .txt files.
    Admin only.
    """

    knowledge = await Knowledges.get_knowledge_by_id(id=id, db=db)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    files = await Knowledges.get_files_by_id(id, db=db)

    # Create zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            content = file.data.get('content', '') if file.data else ''
            if content:
                # Use original filename with .txt extension
                filename = file.filename
                if not filename.endswith('.txt'):
                    filename = f'{filename}.txt'
                zf.writestr(filename, content)

    zip_buffer.seek(0)

    # Sanitize knowledge name for filename
    # ASCII-safe fallback for the basic filename parameter (latin-1 safe)
    safe_name = ''.join(c if c.isascii() and (c.isalnum() or c in ' -_') else '_' for c in knowledge.name)
    zip_filename = f'{safe_name}.zip'

    # Use RFC 5987 filename* for non-ASCII names so the browser gets the real name
    quoted_name = quote(f'{knowledge.name}.zip')
    content_disposition = f'attachment; filename="{zip_filename}"; filename*=UTF-8\'\'{quoted_name}'

    return StreamingResponse(
        zip_buffer,
        media_type='application/zip',
        headers={'Content-Disposition': content_disposition},
    )
