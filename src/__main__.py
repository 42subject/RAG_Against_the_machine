from fire import Fire
from fire.core import FireError
from pydantic import ValidationError

import pickle
from pathlib import Path

from .input_models import (
    IndexOptions, QueryOptions,
    SearchDatasetOptions, AnswerDatasetOptions, EvaluateOptions
)
from .index import indexer
from .search import searcher, dataset_searcher
from .answer import answer, answer_dataset
from .evaluate import evaluater


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

        indexer(options)

    def search(self, question: str, k: int = 10) -> None:
        """質問に対して関連度の高いチャンクをk件返す。

        Args:
            question (str): 質問文
            k (int, optional): 返答数. Defaults to 10.

        Raises:
            FireError: 質問または取得件数が不正な場合。
        """
        try:
            options = QueryOptions(
                question=question,
                k=k
            )
        except ValidationError as error:
            raise FireError(error.errors()[0]["msg"])

        sources = searcher(options)
        print(sources)

    def search_dataset(
            self, dataset_path: Path, save_directory: Path, k: int = 10
            ) -> None:
        """dataset_pathのjsonファイルに入ってる質問全てに対してサーチをする。

        Args:
            dataset_path (Path): datasetのパス
            save_directory (Path): 結果の保存先
            k (int, optional): 返答数. Defaults to 10.

        Raises:
            FireError: 入力オプションが不正な場合。
        """
        try:
            options = SearchDatasetOptions(
                dataset_path=dataset_path,
                save_directory=save_directory,
                k=k
            )
        except ValidationError as error:
            raise FireError(error.errors()[0]["msg"])

        dataset_searcher(options)

    def answer(self, question: str, k: int = 10) -> None:
        """質問に対して回答をする。

        Args:
            question (str): 質問文
            k (int, optional): 回答生成時に参照する検索結果の最大件数. Defaults to 10.

        Raises:
            FireError: 質問または取得件数が不正な場合。
        """
        try:
            options = QueryOptions(
                question=question,
                k=k
            )
        except ValidationError as error:
            raise FireError(error.errors()[0]["msg"])

        print(answer(options))

    def answer_dataset(
            self, student_search_results_path: Path, save_directory: Path
            ) -> None:
        """検索結果データセットの各質問に対して回答を生成する。

        Args:
            student_search_results_path (Path):
                serch_datasetの検索結果JSONファイルのパス
            save_directory (Path):
                結果の保存先

        Raises:
            FireError: 入力オプションが不正な場合。
        """

        try:
            options = AnswerDatasetOptions(
                student_search_results_path=student_search_results_path,
                save_directory=save_directory
            )
        except ValidationError as error:
            raise FireError(error.errors()[0]["msg"])

        answer_dataset(options)

    def evaluate(
            self, student_search_results_path: Path, dataset_path: Path
            ) -> None:
        """出力を評価する。

        Args:
            student_search_results_path (Path): 出力
            dataset_path (Path): 答え

        Raises:
            FireError: 入力オプションが不正な場合。
        """

        try:
            options = EvaluateOptions(
                student_search_results_path=student_search_results_path,
                dataset_path=dataset_path
            )
        except ValidationError as error:
            raise FireError(error.errors()[0]["msg"])

        print(evaluater(options))


def main() -> None:
    """CLIを起動し、利用者入力や外部ファイルのエラーを表示する。

    Raises:
        SystemExit: CLI入力または外部データを処理できなかった場合。
    """
    try:
        Fire(CLI)
    except (
        EOFError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        ValidationError,
        pickle.UnpicklingError,
    ) as error:
        raise SystemExit(f"ERROR: {error}") from None


if __name__ == "__main__":
    main()
