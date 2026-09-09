from typing import ClassVar


class Visualizer:
    """生成中のテキストや候補トークンをターミナルに表示する。"""

    TOTAL_LINES: ClassVar[int] = 7
    GENERATED_LINE: ClassVar[int] = 0
    REJECTED_LINE: ClassVar[int] = 1
    TOP_TOKEN_START_LINE: ClassVar[int] = 2
    TOP_TOKEN_LIMIT: ClassVar[int] = 5

    def initialize(self) -> None:
        """表示用の行を確保する。"""
        print("\n" * (self.TOTAL_LINES + 1), end="")

    def show_generated_text(self, generated_text: str) -> None:
        """現在までに生成されたテキストを表示する。"""
        self._write_line(
            self.GENERATED_LINE,
            f"generated_text: {generated_text[-50:]!r}",
        )

    def show_rejected_token(self, rejected_token: str) -> None:
        """表示不可能なため拒否したトークンを表示する。"""
        self._write_line(
            self.REJECTED_LINE,
            f"rejected_token: {rejected_token!r}",
        )

    def show_top_tokens(
        self,
        top_tokens: list[tuple[int, str]],
    ) -> None:
        """次トークン候補の上位を表示する。"""
        lines = [
            f"top_token[{index}]: {token_id} {text!r}"
            for index, (token_id, text) in enumerate(
                top_tokens,
                start=1,
            )
        ]

        for index in range(self.TOP_TOKEN_LIMIT):
            line = lines[index] if index < len(lines) else ""
            self._write_line(self.TOP_TOKEN_START_LINE + index, line)

    def finish(self) -> None:
        """生成状況の表示を終了する。"""
        print()

    def _write_line(self, line_index: int, text: str) -> None:
        """表示ブロック内の指定行を上書きする。"""
        move_up_count = self.TOTAL_LINES - line_index
        print(f"\033[{move_up_count}F", end="")
        print(f"\033[K{text}", end="")
        print(f"\033[{move_up_count}E", end="", flush=True)
