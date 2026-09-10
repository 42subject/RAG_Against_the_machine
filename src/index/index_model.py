from pydantic import BaseModel
from tqdm import tqdm

from pathlib import Path
from collections import defaultdict, Counter
from math import log

from src.config import BM25_B, BM25_K1, PROJECT_ROOT


class Chunk(BaseModel):
    text: str
    word_count: int
    file_path: str
    first_character_index: int
    last_character_index: int


class ChunkBuffer:
    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self._current_text = ""
        self._current_character_index = 0

    def append_text(self, text: str) -> None:
        self._current_text += text

    def has_text(self) -> bool:
        return self._current_text != ""

    def text_length(self) -> int:
        return len(self._current_text)

    def flush(self) -> Chunk:
        if not self.has_text():
            raise RuntimeError("Cannot create a chunk from empty text")

        first_character_index = self._current_character_index + 1
        self._current_character_index += len(self._current_text)

        chunk = Chunk(
            text=self._current_text,
            word_count=len(self._current_text.split()),
            file_path=str(self._file_path.relative_to(PROJECT_ROOT)),
            first_character_index=first_character_index,
            last_character_index=self._current_character_index,
        )
        self._current_text = ""

        return chunk


class ChunkBuilder:
    def __init__(self, file_path: Path, max_chunk_size: int) -> None:
        self._file_path = file_path
        self._max_chunk_size = max_chunk_size
        self._buffer = ChunkBuffer(file_path)

    def _would_exceed(self, text: str) -> bool:
        return self._buffer.text_length() + len(text) > self._max_chunk_size

    def _from_py_file(self) -> list[Chunk]:
        chunks: list[Chunk] = []
        line_len: int

        with self._file_path.open("r", encoding="UTF-8") as file:
            raw_text = file.read()

        for line in raw_text.splitlines(keepends=True):
            line_len = len(line)

            while line_len > self._max_chunk_size:
                if self._buffer.has_text():
                    chunks.append(self._buffer.flush())
                self._buffer.append_text(line[:self._max_chunk_size])
                chunks.append(self._buffer.flush())
                line = line[self._max_chunk_size:]
                line_len = len(line)

            if self._buffer.has_text() and (
                line.startswith("class")
                or self._would_exceed(line)
            ):
                chunks.append(self._buffer.flush())
            self._buffer.append_text(line)

        if self._buffer.has_text():
            chunks.append(self._buffer.flush())
        return chunks

    def _from_txt_file(self) -> list[Chunk]:
        chunks: list[Chunk] = []
        line_len: int

        with self._file_path.open("r", encoding="UTF-8") as file:
            raw_text = file.read()

        for line in raw_text.splitlines(keepends=True):
            line_len = len(line)

            while line_len > self._max_chunk_size:
                if self._buffer.has_text():
                    chunks.append(self._buffer.flush())
                self._buffer.append_text(line[:self._max_chunk_size])
                chunks.append(self._buffer.flush())
                line = line[self._max_chunk_size:]
                line_len = len(line)

            if self._buffer.has_text() and (
                line.startswith("\n")
                or self._would_exceed(line)
            ):
                chunks.append(self._buffer.flush())
            self._buffer.append_text(line)

        if self._buffer.has_text():
            chunks.append(self._buffer.flush())
        return chunks

    def _from_md_file(self) -> list[Chunk]:
        chunks: list[Chunk] = []
        line_len: int

        with self._file_path.open("r", encoding="UTF-8") as file:
            raw_text = file.read()

        for line in raw_text.splitlines(keepends=True):
            line_len = len(line)

            while line_len > self._max_chunk_size:
                if self._buffer.has_text():
                    chunks.append(self._buffer.flush())
                self._buffer.append_text(line[:self._max_chunk_size])
                chunks.append(self._buffer.flush())
                line = line[self._max_chunk_size:]
                line_len = len(line)

            if self._buffer.has_text() and (
                line.startswith("#")
                or self._would_exceed(line)
            ):
                chunks.append(self._buffer.flush())
            self._buffer.append_text(line)

        if self._buffer.has_text():
            chunks.append(self._buffer.flush())
        return chunks

    def create_chunks(self) -> list[Chunk]:
        try:
            if self._file_path.suffix == ".py":
                return self._from_py_file()
            if self._file_path.suffix == ".txt":
                return self._from_txt_file()
            if self._file_path.suffix == ".md":
                return self._from_md_file()
            else:
                raise ValueError(
                    f"Unsupported file type: {self._file_path.suffix}"
                )
        except (OSError, ValueError) as error:
            raise RuntimeError(f"Error: {error}")


class Index:
    def __init__(
        self,
        chunks: list[Chunk],
        scores: dict[str, list[tuple[int, float]]],
    ) -> None:
        self.chunks = chunks
        self.scores = scores

    @classmethod
    def from_directory(
        cls,
        directory_path: Path,
        max_chunk_size: int,
    ) -> "Index":
        chunks = cls._create_chunks(directory_path, max_chunk_size)
        scores = cls._calculate_scores(chunks)
        return cls(chunks, scores)

    @staticmethod
    def _create_chunks(
        directory_path: Path,
        max_chunk_size: int,
    ) -> list[Chunk]:
        chunks: list[Chunk] = []
        supported_suffixes = {".py", ".txt", ".md"}

        file_paths = [
            file_path
            for file_path in directory_path.rglob("*")
            if file_path.is_file() and file_path.suffix in supported_suffixes
        ]

        for file_path in tqdm(
            file_paths,
            desc="Creating chunks",
            unit="file"
        ):
            builder = ChunkBuilder(file_path, max_chunk_size)
            chunks.extend(builder.create_chunks())

        return chunks

    @staticmethod
    def _calculate_scores(
        chunks: list[Chunk],
    ) -> dict[str, list[tuple[int, float]]]:
        if not chunks:
            raise RuntimeError("Cannot calculate BM25 scores without chunks")

        word_frequencies: dict[
            str, list[tuple[int, int]]
        ] = defaultdict(list)
        for chunk_id, chunk in enumerate(chunks):
            chunk_word_frequencies = Counter(chunk.text.split())
            for word, frequencies in chunk_word_frequencies.items():
                word_frequencies[word].append((chunk_id, frequencies))

        total_chunk_num = len(chunks)
        average_num_terms_per_chunk = (
            sum(chunk.word_count for chunk in chunks) /
            total_chunk_num
        )

        scores: dict[str, list[tuple[int, float]]] = defaultdict(list)
        for word, positions in word_frequencies.items():
            document_frequency = len(positions)
            inverse_document_frequency = log(
                1
                + (
                    total_chunk_num - document_frequency + 0.5
                ) / (document_frequency + 0.5)
            )
            for chunk_id, frequency in positions:
                document_length = chunks[chunk_id].word_count
                score = inverse_document_frequency * (
                    frequency * (BM25_K1 + 1)
                ) / (
                    frequency
                    + BM25_K1
                    * (
                        1
                        - BM25_B
                        + BM25_B
                        * document_length
                        / average_num_terms_per_chunk
                    )
                )
                scores[word].append((chunk_id, score))

        return scores
