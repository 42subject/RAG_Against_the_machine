from src.config import MAX_NEW_TOKENS, TOKEN_LIMIT
from src.llm_sdk.llm_sdk import Small_LLM_Model

from .visualizer import Visualizer


class QwenClient:
    """表示可能なテキストをQwenモデルで生成する。"""

    def __init__(self, model_name: str) -> None:
        """モデルと生成状況の表示機能を初期化する。

        Args:
            model_name: 使用するQwenモデル名。
        """
        self.model = Small_LLM_Model(model_name)
        self.visualizer = Visualizer()

    def _select_displayable_token_id(
        self,
        ranked_token_ids: list[int],
    ) -> int:
        """表示可能なトークンまたはEOSが見つかるまで候補を制約する。

        Args:
            ranked_token_ids: スコアの高い順に並べたトークンID。

        Returns:
            表示可能な文字列へ復号できるトークンID、またはEOSトークンID。

        Raises:
            RuntimeError: 表示可能なトークンもEOSも存在しない場合。
        """
        for token_id in ranked_token_ids:
            if token_id == self.model.eos_token_id:
                return token_id

            token_text = self.model.decode([token_id])
            if token_text.isprintable():
                return token_id

            self.visualizer.show_rejected_token(token_text)

        raise RuntimeError("No displayable token or EOS token found")

    def _get_sentence_completion(
        self,
        token_text: str,
        generated_text: str,
    ) -> str | None:
        """文末の改行をEOS相当として扱う文字列を返す。

        Args:
            token_text: 最高スコアの次トークンを復号した文字列。
            generated_text: 生成済みの文字列。

        Returns:
            生成を終了する場合は最後に追加する文字列、それ以外はNone。
        """
        if ".\n" in token_text:
            return token_text.split("\n", maxsplit=1)[0]
        if generated_text.endswith(".") and token_text.startswith("\n"):
            return ""
        return None

    def _select_displayable_token(
        self,
        ranked_token_ids: list[int],
        generated_text: str,
    ) -> tuple[int | None, str]:
        """表示可能な次トークンを選択する。

        Args:
            ranked_token_ids: スコアの高い順に並べたトークンID。
            generated_text: 生成済みの文字列。

        Returns:
            継続時のトークンIDと、出力する表示可能文字列。
            EOSの場合だけIDをNoneにする。
        """
        top_tokens = [
            (token_id, self.model.decode([token_id]))
            for token_id in ranked_token_ids[:self.visualizer.TOP_TOKEN_LIMIT]
        ]
        self.visualizer.show_top_tokens(top_tokens)

        sentence_completion = self._get_sentence_completion(
            top_tokens[0][1],
            generated_text,
        )
        if sentence_completion is not None:
            return None, sentence_completion

        next_token_id = self._select_displayable_token_id(ranked_token_ids)
        if next_token_id == self.model.eos_token_id:
            return None, ""

        next_text = self.model.decode([next_token_id])
        return next_token_id, next_text

    def is_token_limit(self, text: str) -> bool:
        """入力文字列が設定されたトークン上限を超えるか判定する。

        Args:
            text: トークン数を確認する文字列。

        Returns:
            トークン数がTOKEN_LIMIT - MAX_NEW_TOKENSを超える場合はTrue。
        """
        return len(self.model.encode(text)[0]) > TOKEN_LIMIT - MAX_NEW_TOKENS

    def generate(self, prompt: str) -> str:
        """プロンプトから表示可能なテキストだけを生成する。

        Args:
            prompt: モデルへ入力する文字列。

        Returns:
            生成された文字列。
        """
        input_ids = [int(id) for id in self.model.encode(prompt)[0]]
        generated_text = ""

        self.visualizer.initialize()
        for _ in range(MAX_NEW_TOKENS):
            logits = self.model.get_logits_from_input_ids(input_ids)
            ranked_token_ids = sorted(
                range(len(logits)),
                key=lambda token_id: logits[token_id],
                reverse=True,
            )
            next_token_id, next_text = self._select_displayable_token(
                ranked_token_ids,
                generated_text,
            )
            generated_text += next_text
            if next_text:
                self.visualizer.show_generated_text(generated_text)
            if next_token_id is None:
                break

            input_ids.append(next_token_id)

        self.visualizer.finish()
        return generated_text
