from pydantic import BaseModel
from tqdm import tqdm

from pathlib import Path
from collections import defaultdict, Counter
from math import log

from src.config import BM25_B, BM25_K1, PROJECT_ROOT
from src.tokenizer import tokenizer


class Chunk(BaseModel):
    """索引化する本文と元ファイル上の位置を保持する。

    Attributes:
        text: チャンクの本文。
        word_count: 本文を空白で分割した語数。
        file_path: プロジェクトルートからの相対ファイルパス。
        first_character_index: 元ファイル上の開始文字位置。
        last_character_index: 元ファイル上の終了文字位置。
    """

    text: str
    word_count: int
    file_path: str
    first_character_index: int
    last_character_index: int


class ChunkBuffer:
    """連続する本文を蓄積し、位置情報付きチャンクへ変換する。"""

    def __init__(self, file_path: Path) -> None:
        """空のバッファを初期化する。

        Args:
            file_path: チャンク元のファイルパス。
        """
        self._file_path = file_path
        self._current_text = ""
        self._current_character_index = 0

    def append_text(self, text: str) -> None:
        """本文を現在のバッファ末尾へ追加する。

        Args:
            text: 追加する本文。
        """
        self._current_text += text

    def has_text(self) -> bool:
        """バッファに本文があるか返す。

        Returns:
            本文が1文字以上あればTrue。
        """
        return self._current_text != ""

    def text_length(self) -> int:
        """現在の本文の文字数を返す。

        Returns:
            バッファに蓄積した文字数。
        """
        return len(self._current_text)

    def flush(self) -> Chunk:
        """現在の本文を位置情報付きチャンクとして取り出す。

        Returns:
            バッファの本文から生成したチャンク。

        Raises:
            RuntimeError: バッファが空の場合。
        """
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
    """ファイル形式に応じて検索用チャンクを構築する。"""

    def __init__(self, file_path: Path, max_chunk_size: int) -> None:
        """チャンク生成対象と最大文字数を設定する。

        Args:
            file_path: 読み込むファイルのパス。
            max_chunk_size: 1チャンクに含める最大文字数。
        """
        self._file_path = file_path
        self._max_chunk_size = max_chunk_size
        self._buffer = ChunkBuffer(file_path)

    def _would_exceed(self, text: str) -> bool:
        """本文を追加すると最大文字数を超えるか判定する。

        Args:
            text: 追加候補の本文。

        Returns:
            追加後の文字数が上限を超える場合はTrue。
        """
        return self._buffer.text_length() + len(text) > self._max_chunk_size

    def _from_py_file(self) -> list[Chunk]:
        """Pythonファイルをクラス境界と文字数上限で分割する。

        Returns:
            元ファイル順のチャンク一覧。

        Raises:
            OSError: ファイルを読み込めない場合。
        """
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
        """テキストファイルを空行と文字数上限で分割する。

        Returns:
            元ファイル順のチャンク一覧。

        Raises:
            OSError: ファイルを読み込めない場合。
        """
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
        """Markdownファイルを見出しと文字数上限で分割する。

        Returns:
            元ファイル順のチャンク一覧。

        Raises:
            OSError: ファイルを読み込めない場合。
        """
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
        """拡張子に対応する方法でファイルをチャンク化する。

        Returns:
            元ファイル順のチャンク一覧。

        Raises:
            RuntimeError: ファイルの読み込みまたは形式の判定に失敗した場合。
        """
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
    """チャンクと語ごとのBM25スコアを保持する検索索引。"""

    def __init__(
        self,
        chunks: list[Chunk],
        scores: dict[str, list[tuple[int, float]]],
    ) -> None:
        """計算済みのチャンクと転置スコアを設定する。

        Args:
            chunks: 索引対象のチャンク一覧。
            scores: 語ごとのチャンクIDとBM25スコア。
        """
        self.chunks = chunks
        self.scores = scores

    @classmethod
    def from_directory(
        cls,
        directory_path: Path,
        max_chunk_size: int,
    ) -> "Index":
        """指定ディレクトリを読み込み、検索索引を構築する。

        Args:
            directory_path: 索引対象ファイルを含むディレクトリ。
            max_chunk_size: 1チャンクに含める最大文字数。

        Returns:
            構築済みの検索索引。
        """
        chunks = cls._create_chunks(directory_path, max_chunk_size)
        scores = cls._calculate_scores(chunks)
        return cls(chunks, scores)

    @staticmethod
    def _create_chunks(
        directory_path: Path,
        max_chunk_size: int,
    ) -> list[Chunk]:
        """対応ファイルを再帰的に探索してチャンク化する。

        Args:
            directory_path: 探索を開始するディレクトリ。
            max_chunk_size: 1チャンクに含める最大文字数。

        Returns:
            対応する全ファイルから生成したチャンク一覧。
        """
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
        """全チャンクから語ごとのBM25スコアを計算する。

        Args:
            chunks: スコア計算対象のチャンク一覧。

        Returns:
            語をキー、チャンクIDとスコアの組を値とする転置索引。

        Raises:
            RuntimeError: チャンク一覧が空の場合。
        """
        if not chunks:
            raise RuntimeError("Cannot calculate BM25 scores without chunks")

        word_frequencies: dict[
            str, list[tuple[int, int]]
        ] = defaultdict(list)
        for chunk_id, chunk in enumerate(chunks):
            chunk_word_frequencies = Counter(tokenizer(chunk.text))
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
