from datetime import datetime, timedelta, timezone

from sqlalchemy import update

from app.db.models import Document as DocumentModel
import uuid

import pytest

from app.db.models import User
from app.db.repository import (
    create_document,
    get_latest_document,
    get_or_create_user,
    save_chunks,
    search_similar_chunks,
)


FAKE_EMBEDDING_DIM = 768

def _fake_vector(seed: float) -> list[float]:
    return [seed] * FAKE_EMBEDDING_DIM

async def test_get_or_create_user_creates_new_user(session):
    telegram_id = 123123
    user = await get_or_create_user(session, telegram_id)

    assert user.id == telegram_id
    assert isinstance(user, User)


async def test_get_or_create_user_returns_existing_user(session):
    telegram_id = 123123

    first_call = await get_or_create_user(session, telegram_id)
    second_call = await get_or_create_user(session, telegram_id)

    assert first_call == second_call


async def test_create_document_links_to_user(session):
    user = await get_or_create_user(session, 123123)

    document = await create_document(session, user.id, "Document.pdf")

    assert document.user_id == user.id
    assert document.file_name == "Document.pdf"
    assert isinstance(document.id, uuid.UUID)


async def test_save_chunks_persists_all_chunks(session):
    user = await get_or_create_user(session, 123123)
    document = await create_document(session, user.id, "Document.pdf")

    text = ["first chunk", "second chunk", "third chunk"]

    embeddings = [_fake_vector(0.1), _fake_vector(0.2), _fake_vector(0.3)]
    chunks = await save_chunks(session, document.id, text, embeddings)

    assert len(chunks) == 3
    assert chunks[0].chunk_index == 0
    assert chunks[2].chunk_text == "third chunk"

async def test_save_chunks_raises_on_mismatched_lengths(session):
    user = await get_or_create_user(session, 555555)
    document = await create_document(session, user.id, "test.pdf")

    with pytest.raises(ValueError):
        await save_chunks(session, document.id, ["text"],[])


async def test_search_similar_chunks_return_closest_by_cosine_distance(session):
    user = await get_or_create_user(session, 123123)
    document = await create_document(session, user.id, "Document.pdf")

    await save_chunks(
        session,
        document.id,
        ["close chunk", "far chunk"],
        [_fake_vector(0.1), _fake_vector(0.2)]
    )
    results = await search_similar_chunks(session, document.id, _fake_vector(1.0), limit=1)

    assert len(results) == 1
    assert results[0].chunk_text == "close chunk"


async def test_search_similar_chunks_respects_document_boundary(session):
    user = await get_or_create_user(session, 123123)
    doc_a = await create_document(session, user.id, "Document.pdf.a")
    doc_b = await create_document(session, user.id, "Document.pdf.b")

    await save_chunks(session, doc_a.id, ["chunk 1"], [_fake_vector(0.1)])
    await save_chunks(session, doc_b.id, ["chunk 2"], [_fake_vector(0.2)])

    results = await search_similar_chunks(session, doc_a.id, _fake_vector(1.0))

    assert len(results) == 1
    assert results[0].chunk_text == "chunk 1"

async def test_get_latest_document_returns_most_recent(session):
    user = await get_or_create_user(session, 888888)

    old = await create_document(session, user.id, "old.pdf")
    newest = await create_document(session, user.id, "new.pdf")

    await session.execute(
        update(DocumentModel)
        .where(DocumentModel.id == old.id)
        .values(created_at=datetime.now(timezone.utc) - timedelta(minutes=1))
    )
    await session.flush()

    result = await get_latest_document(session, user.id)

    assert result.id == newest.id