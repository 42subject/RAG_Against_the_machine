from src.config import MAX_NEW_TOKENS
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

    def _select_displayable_token(
        self,
        logits: list[float],
    ) -> tuple[int | None, str]:
        """表示可能な次トークンを選択する。

        Args:
            logits: 次トークンごとのスコア。

        Returns:
            継続時のトークンIDと、出力する表示可能文字列。
            EOSまたは非表示文字を含むトークンではIDをNoneにする。
        """
        next_token_id = max(
            range(len(logits)),
            key=lambda token_id: logits[token_id],
        )
        top_token_ids = sorted(
            range(len(logits)),
            key=lambda token_id: logits[token_id],
            reverse=True,
        )[:self.visualizer.TOP_TOKEN_LIMIT]
        top_tokens = [
            (token_id, self.model.decode([token_id]))
            for token_id in top_token_ids
        ]
        self.visualizer.show_top_tokens(top_tokens)

        if next_token_id == self.model.eos_token_id:
            return None, ""

        next_text = self.model.decode([next_token_id])
        if next_text and next_text.isprintable():
            return next_token_id, next_text

        displayable_prefix = ""
        for character in next_text:
            if not character.isprintable():
                break
            displayable_prefix += character

        self.visualizer.show_rejected_token(next_text)
        return None, displayable_prefix

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
            next_token_id, next_text = self._select_displayable_token(logits)
            generated_text += next_text
            if next_text:
                self.visualizer.show_generated_text(generated_text)
            if next_token_id is None:
                break

            input_ids.append(next_token_id)

        self.visualizer.finish()
        return generated_text
