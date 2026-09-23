"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document

_HEADER_RE = re.compile(r"(?m)^#{1,6}\s+.*$")


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _split_into_sections(text: str) -> list[str]:
    """Cut a document at its markdown headers, keeping each heading with the
    text that follows it until the next header."""
    matches = list(_HEADER_RE.finditer(text))
    if not matches:
        return [text.strip()] if text.strip() else []

    sections = []
    if matches[0].start() > 0:
        lead = text[: matches[0].start()].strip()
        if lead:
            sections.append(lead)

    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = text[start:end].strip()
        if section:
            sections.append(section)

    return sections


def _split_oversized_section(section: str, chunk_size: int, overlap: int) -> list[str]:
    """A section too long for one chunk: split on paragraph breaks first, then
    fall back to a character window with overlap for any paragraph that's
    still too long on its own."""
    paragraphs = [p.strip() for p in section.split("\n\n") if p.strip()]
    pieces: list[str] = []
    current = ""

    for para in paragraphs:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            pieces.append(current)
        if len(para) <= chunk_size:
            current = para
        else:
            start = 0
            while start < len(para):
                pieces.append(para[start : start + chunk_size].strip())
                start += chunk_size - overlap
            current = ""

    if current:
        pieces.append(current)

    return [p for p in pieces if p]


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Splits on `#`/`##` headers instead of a fixed character count.

    Each guide here is short and already broken into sections ("Getting
    there", "Eat and drink", ...) that are 150-500 chars each — a fixed
    800-char window kept cutting mid-section. One chunk per section fixes
    that. Oversized sections fall back to paragraph/char splitting.
    """
    chunk_size = config.CHUNK_SIZE
    overlap = config.CHUNK_OVERLAP

    chunks: list[Chunk] = []
    for doc in documents:
        index = 0
        for section in _split_into_sections(doc.text):
            pieces = (
                [section]
                if len(section) <= chunk_size
                else _split_oversized_section(section, chunk_size, overlap)
            )
            for piece in pieces:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
