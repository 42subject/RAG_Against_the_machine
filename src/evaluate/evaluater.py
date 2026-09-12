"""検索結果のRecallを計算する。"""

from tqdm import tqdm

from src.config import IOU_BORDER
from src.input_models import EvaluateOptions
from src.models import (
    AnsweredQuestion,
    MinimalSearchResults,
    RagDataset,
    MinimalSource,
    StudentSearchResults,
)


def _calculate_iou(
    ground_truth: MinimalSource,
    retrieved_source: MinimalSource,
) -> float:
    """同じファイルにある2つの文字範囲のIoUを計算する。

    Args:
        ground_truth: 正解として指定されたソース位置。
        retrieved_source: 検索によって取得したソース位置。

    Returns:
        文字範囲のIoU。同じファイルでなければ0.0。

    Raises:
        ValueError: いずれかの文字範囲が不正な場合。
    """
    if ground_truth.file_path != retrieved_source.file_path:
        return 0.0

    if ground_truth.last_character_index < ground_truth.first_character_index:
        raise ValueError(
            "Invalid ground-truth source range: "
            f"{ground_truth.first_character_index}-"
            f"{ground_truth.last_character_index}"
        )
    if retrieved_source.last_character_index < (
        retrieved_source.first_character_index
    ):
        raise ValueError(
            "Invalid retrieved source range: "
            f"{retrieved_source.first_character_index}-"
            f"{retrieved_source.last_character_index}"
        )

    intersection_length = max(
        0,
        min(
            ground_truth.last_character_index,
            retrieved_source.last_character_index,
        )
        - max(
            ground_truth.first_character_index,
            retrieved_source.first_character_index,
        )
        + 1,
    )
    union_length = (
        max(
            ground_truth.last_character_index,
            retrieved_source.last_character_index,
        )
        - min(
            ground_truth.first_character_index,
            retrieved_source.first_character_index,
        )
        + 1
    )
    return intersection_length / union_length


def _calculate_recall(
    ground_truth: list[MinimalSource],
    student_result: MinimalSearchResults,
    k: int,
) -> float:
    """1件の質問について上位k件に対するRecallを計算する。

    Args:
        ground_truth: 質問に対する正解ソース一覧。
        student_result: 学生実装が返した検索結果。
        k: 評価に使用する上位件数。

    Returns:
        発見できた正解ソースの割合。

    Raises:
        ValueError: 正解ソースが空の場合。
    """
    if not ground_truth:
        raise ValueError(
            f"No ground-truth sources: {student_result.question_id}"
        )

    retrieved_sources = student_result.retrieved_sources[:k]
    hit_count = sum(
        any(
            _calculate_iou(truth, retrieved_source) >= IOU_BORDER
            for retrieved_source in retrieved_sources
        )
        for truth in ground_truth
    )
    return hit_count / len(ground_truth)


def _set_ground_truth_dict(
    dataset: RagDataset,
) -> dict[str, AnsweredQuestion]:
    """正解付き質問をquestion_idで検索できる辞書に変換する。

    Args:
        dataset: 正解付き質問を含むデータセット。

    Returns:
        question_idをキーとする正解付き質問の辞書。

    Raises:
        TypeError: 正解なしの質問が含まれる場合。
        ValueError: question_idが重複する場合。
    """
    ground_truth_by_id: dict[str, AnsweredQuestion] = {}

    for ground_truth in dataset.rag_questions:
        if not isinstance(ground_truth, AnsweredQuestion):
            raise TypeError("Expected an AnsweredQuestion")
        if ground_truth.question_id in ground_truth_by_id:
            raise ValueError(
                "Duplicate ground-truth question_id: "
                f"{ground_truth.question_id}"
            )
        ground_truth_by_id[ground_truth.question_id] = ground_truth

    return ground_truth_by_id


def evaluater(option: EvaluateOptions) -> tuple[float, int]:
    """検索結果と正解データを読み込み、質問ごとのRecallを平均する。

    Args:
        option: 検索結果と正解データセットのパス。

    Returns:
        全質問の平均Recall@k

    Raises:
        OSError: 入力ファイルを読み込めない場合。
        TypeError: 正解データセットに未回答質問が含まれる場合。
        ValueError: 入力内容または評価設定が不正な場合。
    """
    if not 0.0 <= IOU_BORDER <= 1.0:
        raise ValueError(f"IOU_BORDER must be between 0 and 1: {IOU_BORDER}")

    with option.dataset_path.open("r", encoding="UTF-8") as file:
        dataset = RagDataset.model_validate_json(file.read())
    with option.student_search_results_path.open(
        "r",
        encoding="UTF-8",
    ) as file:
        student_results = StudentSearchResults.model_validate_json(file.read())

    if student_results.k < 1:
        raise ValueError(f"k must be at least 1: {student_results.k}")
    if not student_results.search_results:
        raise ValueError("Student search results must not be empty")

    ground_truth_by_id = _set_ground_truth_dict(dataset)
    student_question_ids: set[str] = set()
    recalls: list[float] = []

    for student_result in tqdm(
        student_results.search_results,
        desc="Evaluating",
        unit="question",
    ):
        if student_result.question_id in student_question_ids:
            raise ValueError(
                f"Duplicate student question_id: {student_result.question_id}"
            )
        student_question_ids.add(student_result.question_id)

        ground_truth = ground_truth_by_id.get(student_result.question_id)
        if ground_truth is None:
            raise ValueError(
                f"Unknown question_id: {student_result.question_id}"
            )

        recalls.append(
            _calculate_recall(
                ground_truth.sources,
                student_result,
                student_results.k,
            )
        )

    missing_question_ids = ground_truth_by_id.keys() - student_question_ids
    if missing_question_ids:
        raise ValueError(
            "Missing student question_id: "
            f"{sorted(missing_question_ids)[0]}"
        )

    return (sum(recalls) / len(recalls), student_results.k)
