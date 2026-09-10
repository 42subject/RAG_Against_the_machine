from tqdm import tqdm

from src.input_models import AnswerDatasetOptions, QueryOptions
from src.config import MODEL
from src.models import (
    MinimalAnswer,
    RetrievedSource,
    StudentSearchResults,
    StudentSearchResultsAndAnswer,
    UnansweredQuestion,
)
from src.search import searcher

from .function_call_generator import QwenClient


def generate_prompt(
    question: str,
    sources: list[RetrievedSource],
) -> str:
    """質問と取得したソースから回答生成用プロンプトを作る。

    Args:
        question: 回答する質問文。
        sources: 回答の根拠として使用するソース。

    Returns:
        質問とソース本文を含むプロンプト。
    """
    source_sections: list[str] = []

    for index, source in enumerate(sources, start=1):
        source_sections.append(
            f"[Source {index}]\n"
            f"file_path: {source.file_path}\n"
            f"content:\n{source.text}"
        )

    sources_text = "\n\n".join(source_sections)
    return (
        "Answer the question using only the provided sources. "
        "Do not use outside knowledge.\n\n"
        f"Question:\n{question}\n\n"
        f"Sources:\n{sources_text}\n\n"
        "Answer:\n"
    )


def answer(option: QueryOptions) -> MinimalAnswer:
    question = UnansweredQuestion(question=option.question)
    sources = searcher(option)

    llm = QwenClient(MODEL)
    prompt = generate_prompt(question.question, sources)
    return MinimalAnswer(
        question_id=question.question_id,
        question=question.question,
        retrieved_sources=sources,
        answer=llm.generate(prompt),
    )


def answer_dataset(options: AnswerDatasetOptions) -> None:
    """検索結果データセットの各質問に回答してJSONへ保存する。

    Args:
        options: 入力する検索結果と保存先の指定。

    Raises:
        OSError: 入力ファイルの読み込みまたは結果の保存に失敗した場合。
        ValueError: 入力JSONが不正な場合。
    """
    with options.student_search_results_path.open(
        "r",
        encoding="UTF-8",
    ) as file:
        student_search_results = StudentSearchResults.model_validate_json(
            file.read()
        )

    llm = QwenClient(MODEL)
    answers: list[MinimalAnswer] = []

    for search_result in tqdm(
        student_search_results.search_results,
        desc="Generating answers",
    ):
        prompt = generate_prompt(
            search_result.question,
            search_result.retrieved_sources,
        )
        answers.append(
            MinimalAnswer(
                question_id=search_result.question_id,
                question=search_result.question,
                retrieved_sources=search_result.retrieved_sources,
                answer=llm.generate(prompt),
            )
        )

    results_and_answers = StudentSearchResultsAndAnswer(
        search_results=answers,
        k=student_search_results.k,
    )

    options.save_directory.mkdir(parents=True, exist_ok=True)
    output_path = (
        options.save_directory / options.student_search_results_path.name
    )
    with output_path.open("w", encoding="UTF-8") as file:
        file.write(results_and_answers.model_dump_json(indent=2))
