from fire import Fire
from fire.core import FireError
from pydantic import BaseModel, Field, ValidationError

from enum import StrEnum
from pathlib import Path


class InputCommand(StrEnum):
    INDEX = "index"
    SEARCH = "search"
    SEARCH_DATASET = "search_dataset"
    ANSWER = "answer"
    ANSWER_DATASET = "answer_dataset"
    EVALUATE = "evaluate"


class QueryOptions(BaseModel):
    """クエリ作成オプション"""

    question: str
    k: int = Field(ge=1)


class SearchDatasetOptions(BaseModel):
    """サーチデータセット作成オプション"""

    dataset_path: Path
    save_directory: Path
    k: int = Field(ge=1)


class IndexOptions(BaseModel):
    """インデックス作成オプション"""

    max_chunk_size: int = Field(default=2000, gt=0, le=2000)


class AnswerDatasetOptions(BaseModel):
    """アンサーデータセット作成オプション"""

    student_search_results_path: Path
    save_directory: Path


class EvaluateOptions(BaseModel):
    """evaluateオプション"""

    student_search_results_path: Path
    dataset_path: Path


class CLI:
    """Python Fireで公開するコマンドライン操作を提供する。"""

    def index(
        self,
        max_chunk_size: int = 2000,
    ) -> None:
        """rawにあるデータをチャンク分割し、検索用データをprocessedに格納する。

        Args:
            max_chunk_size: チャンクに含める最大文字数。

        Raises:
            FireError: 最大文字数が課題仕様の範囲外である場合。
        """
        try:
            options = IndexOptions(
                max_chunk_size=max_chunk_size
            )
        except ValidationError as error:
            raise FireError(error.errors()[0]["msg"])

        print(options)

    def search(self, question: str, k: int = 10) -> None:
        """質問に対して関連度の高いチャンクをk件返す。

        Args:
            question (str): 質問文
            k (int, optional): 返答数. Defaults to 10.
        """
        try:
            options = QueryOptions(
                question=question,
                k=k
            )
        except ValidationError as error:
            raise FireError(error.errors()[0]["msg"])

        print(options)

    def search_dataset(
            self, dataset_path: Path, save_directory: Path, k: int = 10
            ) -> None:
        """dataset_pathのjsonファイルに入ってる質問全てに対してサーチをする。

        Args:
            dataset_path (Path): datasetのパス
            save_directory (Path): 結果の保存先
            k (int, optional): 返答数. Defaults to 10.
        """
        try:
            options = SearchDatasetOptions(
                dataset_path=dataset_path,
                save_directory=save_directory,
                k=k
            )
        except ValidationError as error:
            raise FireError(error.errors()[0]["msg"])

        print(options)

    def answer(self, question: str, k: int = 10) -> None:
        """質問に対して回答をする。

        Args:
            question (str): 質問文
            k (int, optional): 回答生成時に参照する検索結果の最大件数. Defaults to 10.
        """
        try:
            options = QueryOptions(
                question=question,
                k=k
            )
        except ValidationError as error:
            raise FireError(error.errors()[0]["msg"])

        print(options)

    def answer_dataset(
            self, student_search_results_path: Path, save_directory: Path
            ) -> None:
        """検索結果データセットの各質問に対して回答を生成する。

        Args:
            student_search_results_path (Path):
                serch_datasetの検索結果JSONファイルのパス
            save_directory (Path):
                結果の保存先
        """

        try:
            options = AnswerDatasetOptions(
                student_search_results_path=student_search_results_path,
                save_directory=save_directory
            )
        except ValidationError as error:
            raise FireError(error.errors()[0]["msg"])

        print(options)

    def evaluate(
            self, student_search_results_path: Path, dataset_path: Path
            ) -> None:
        """出力を評価する。

        Args:
            student_search_results_path (Path): 出力
            dataset_path (Path): 答え
        """

        try:
            options = EvaluateOptions(
                student_search_results_path=student_search_results_path,
                dataset_path=dataset_path
            )
        except ValidationError as error:
            raise FireError(error.errors()[0]["msg"])

        print(options)


def main() -> None:
    """main"""
    Fire(CLI)


if __name__ == "__main__":
    main()
