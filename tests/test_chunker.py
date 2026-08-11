from app.core.chunker import split_into_chunks

def test_empy_text_returns_empty_list():
    assert split_into_chunks("") == []

def test_whitespace_only_returns_empty_list():
    assert split_into_chunks(" \n ") == []

def short_text_return_single_chunk():
    text = "Hello, world!"
    chunks = split_into_chunks(text, chunk_size=500, overlap=50)
    assert len(chunks) == 1
    assert split_into_chunks(text) == [text]

def test_long_text_is_spit_into_multiple_chunks():
    text = "a" * 1200
    chunks = split_into_chunks(text, chunk_size=500, overlap=50)
    assert len(chunks) == 3


def test_chunks_respect_max_size():
    text = "word" * 500
    chunks = split_into_chunks(text, chunk_size=100, overlap=20)
    assert all(len(chunk) <= 100 for chunk in chunks)


def test_paragraph_boundaries_are_preserved_when_possible():
    text = "First text with a space.\n\nSecond text with a space."
    chunks = split_into_chunks(text, chunk_size=100, overlap=10)
    assert len(chunks) == 1

