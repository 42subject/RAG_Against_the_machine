*このプロジェクトは、42カリキュラムの一環としてsmiyataによって作成されました。*

# RAG Against the Machine

## 概要

RAG Against the Machineは、vLLMのソースツリーに関する質問へ回答するローカルな
Retrieval-Augmented Generation（RAG）システムです。Python、Markdown、テキスト
ファイルを索引化し、BM25によって関連性の高いソース断片を検索します。その断片を
`Qwen/Qwen3-0.6B`へ渡すことで、外部知識による根拠のない回答ではなく、
リポジトリ内の証拠に基づく回答を生成します。

JSONデータセットを使った一括検索と一括回答生成にも対応しています。返された
ファイルパスおよび文字範囲を正解ソースと比較し、Recall@kによって検索品質を
測定できます。

## システム構成

```text
data/raw/vllm-0.10.1
          |
          v
 ファイル種別ごとのチャンク分割
  (.py / .md / .txt)
          |
          v
 BM25転置インデックス -----> data/processed/index.pkl
          |
          v
 質問 -> tokenizer -> 上位k件のソースチャンク
                          |
              +-----------+-----------+
              |                       |
              v                       v
          検索結果JSON             根拠付きprompt
                                          |
                                          v
                                 Qwen/Qwen3-0.6B
                                          |
                                          v
                                      回答JSON
```

主な構成要素は次のとおりです。

- `src/index`: コーパスの読み込み、チャンク生成、BM25スコア仮計算、indexの保存
- `src/search`: 質問のtokenize、質問ごとのBM25スコア集計、上位k件の返却
- `src/answer`: 検索テキストをモデル用contextへ整形し、ローカルQwenで回答を生成
- `src/evaluate`: 正解データからRecall@kを計算
- `src/models`: 各pipeline間で共有するPydanticモデル
- `src/__main__.py`: Python FireによるCLI

## チャンク分割戦略

チャンクサイズは`--max_chunk_size`で指定できます。デフォルトは2,000文字で、
2,000文字を超える値は指定できません。

indexerはファイル形式ごとに異なる方法を使用します。

- Pythonは行単位で蓄積し、トップレベルの`class`宣言前、または追加する行により
  上限を超える場合に分割します。
- Markdownは行単位で蓄積し、見出しの前、またはサイズ上限で分割します。
- テキストは行単位で蓄積し、空行、またはサイズ上限で分割します。
- 設定された上限より長い1行は、上限内の複数部分に分割します。

各チャンクは、プロジェクトルートからの正確な`file_path`と、元ファイルにおける
1始まり・両端を含む`first_character_index`および`last_character_index`を保持します。

## 検索方式

このプロジェクトはBM25による語彙検索を使用します。索引作成時に各tokenを、
チャンクIDとBM25スコアを持つpostingへ対応付けます。検索時は質問のtokenに対応する
postingを直接取得し、チャンクごとにスコアを加算して、合計スコアの降順で並べます。

tokenizerは英数字を抽出し、`casefold()`によって大文字と小文字を区別せず照合します。

BM25のparameterには標準的な`k1 = 1.5`と`b = 0.75`を使用します。

## 必要環境

- Python 3.12以上
- [uv](https://docs.astral.sh/uv/)
- vLLM
- dataset

## インストールと実行方法

リポジトリルートで依存関係をインストールします。

```bash
make install
```

indexを構築します。デフォルトの最大チャンクサイズは2,000文字です。

```bash
uv run python -m src index --max_chunk_size 2000
```

1件の質問を検索します。

```bash
uv run python -m src search \
  --question="What is PagedAttention?" \
  --k=5
```

dataset内の全質問を検索します。

```bash
uv run python -m src search_dataset \
  --dataset_path=data/datasets/UnansweredQuestions/dataset_docs_public.json \
  --save_directory=data/output/search_results/UnansweredQuestions \
  --k=5
```

1件の質問に回答します。

```bash
uv run python -m src answer \
  --question="What is PagedAttention?" \
  --k=5
```

保存済みの検索結果から回答を一括生成します。

```bash
uv run python -m src answer_dataset \
  --student_search_results_path=data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  --save_directory=data/output/search_results_and_answer/UnansweredQuestions
```

プロジェクト内のRecall@k評価を実行します。

```bash
uv run python -m src evaluate \
  --student_search_results_path=data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  --dataset_path=data/datasets/AnsweredQuestions/dataset_docs_public.json
```

```bash
make lint
```

以下の補助targetも利用できます。

```bash
make run-docs
make run-code
make run-answer-docs
make run-answer-code
```

## データの流れと出力

`search_dataset`は`RagDataset`形式のJSONを読み、`StudentSearchResults`形式のJSONを
書き出します。各検索結果には元の質問ID、質問文、順位付けされたソースが含まれます。
ソースには正確なpath、文字範囲、回答生成で使用する検索テキストが記録されます。

`answer_dataset`は検索結果を保持したまま質問ごとの生成回答を追加し、
`StudentSearchResultsAndAnswer`形式のJSONを生成します。各段階で受け渡すデータは
Pydanticによって検証されます。

## 性能分析

課題の制限と合格基準は次のとおりです。

- コーパス全体のindex作成を5分以内に完了する
- 200問の検索を90秒以内に完了する
- docs問題で80%以上のRecall@5を達成する
- code問題で50%以上のRecall@5を達成する

ローカル開発時、大文字と小文字を区別するBM25実装は、公開docs 100問に対して
Recall@5 `0.78`でした。同じ条件で大文字と小文字を区別しないtokenizerを比較した
結果は`0.83`でした。

## 設計上の判断

- 可変のチャンク長の違いによって出る差を最小化するため、平均文書長を補正するBM25を採用。
- ソースコードと文章では有効な構造境界が異なるため、別のチャンク規則を使用。

## 直面した課題

### 表記揺れを丸めるトーカナイズ手法

str.split()のみを使用する元のtokenizerでは`LLM`と`llm`といった大文字小文字の違いや、前後の記号による表記揺れによって、同じ意味であろう単語が別単語として扱われるという課題がありました。その課題を解決するため、コーパス本文と質問の両方へ同じ`casefold()`正規化を適用し、本文や文字offsetを変更せず語彙照合を改善しました。

## 参考資料


- [Qwen3-0.6B model card](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [Python Fire documentation](https://google.github.io/python-fire/)
- [tqdm documentation](https://tqdm.github.io/)

AIは、課題要件の確認、実装上の契約の調査、検索改善案の比較、この文書の下書きに
使用しました。
