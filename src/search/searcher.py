from tqdm import tqdm

import pickle
from collections import defaultdict

from src.config import INDEX_FILE
from src.input_models import QueryOptions, SearchDatasetOptions
from src.index import Index
from src.models import (
    MinimalSearchResults,
    RetrievedSource,
    RagDataset,
    StudentSearchResults,
)
from src.tokenizer import tokenizer


def _get_index() -> Index:
    """永続化された検索索引を読み込む。

    Returns:
        読み込んだ検索索引。

    Raises:
        OSError: 索引ファイルを読み込めない場合。
        TypeError: 保存内容がIndexでない場合。
    """
    with INDEX_FILE.open("rb") as file:
        index = pickle.load(file)
    if not isinstance(index, Index):
        raise TypeError("Loaded object is not an Index")
    return index


def _search(
    index: Index,
    question: str,
    k: int,
) -> list[RetrievedSource]:
    """質問のBM25スコアを集計して上位ソースを返す。

    Args:
        index: 検索に使用する索引。
        question: 検索する質問文。
        k: 返すソースの最大件数。

    Returns:
        BM25スコアの降順に並べたソース一覧。
    """
    chunk_scores: dict[int, float] = defaultdict(float)
    for word in tokenizer(question):
        for chunk_id, score in index.scores[word]:
            chunk_scores[chunk_id] += score
    top_chunks = sorted(
        chunk_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:k]

    return [
        RetrievedSource(
            text=index.chunks[chunk_id].text,
            file_path=index.chunks[chunk_id].file_path,
            first_character_index=(
                index.chunks[chunk_id].first_character_index
            ),
            last_character_index=(
                index.chunks[chunk_id].last_character_index
            ),
        )
        for chunk_id, _ in top_chunks
    ]


def searcher(option: QueryOptions) -> list[RetrievedSource]:
    """保存済み索引から1件の質問を検索する。

    Args:
        option: 質問文と取得件数。

    Returns:
        関連度の高いソース一覧。
    """
    return _search(
        _get_index(),
        option.question,
        option.k,
    )


def dataset_searcher(options: SearchDatasetOptions) -> None:
    """質問データセットを検索し、構造化JSONへ保存する。

    Args:
        options: データセット、取得件数、保存先の指定。

    Raises:
        OSError: 入出力ファイルを処理できない場合。
        ValueError: 入力JSONがデータモデルに適合しない場合。
    """
    with options.dataset_path.open("r", encoding="UTF-8") as file:
        dataset = RagDataset.model_validate_json(file.read())

    search_results: list[MinimalSearchResults] = []
    index = _get_index()

    for unanswered in tqdm(
        dataset.rag_questions,
        desc="Searching",
        unit="searched"
    ):
        question, question_id = unanswered.question, unanswered.question_id

        sources = _search(
            index,
            question,
            options.k,
        )
        search_results.append(MinimalSearchResults(
            question_id=question_id,
            question=question,
            retrieved_sources=sources
        ))

    student_search_results = StudentSearchResults(
        search_results=search_results,
        k=options.k,
    )

    options.save_directory.mkdir(parents=True, exist_ok=True)
    output_path = options.save_directory / options.dataset_path.name

    with output_path.open("w", encoding="UTF-8") as file:
        file.write(student_search_results.model_dump_json(indent=2))
