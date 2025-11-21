"""
LLMサービス

OpenAI GPT-4oを使用してコンペティション情報を分析し、
日本語要約とタグを生成します。
"""

import os
import json
from typing import List, Dict, Optional, Any
from openai import OpenAI
import time

from app.config import OPENAI_API_KEY


class LLMService:
    """LLMサービスクラス"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: OpenAI APIキー（省略時は環境変数から取得）
        """
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI APIキーが設定されていません")

        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"  # GPT-4o（高品質版）
        self.max_retries = 3
        self.retry_delay = 2  # 秒

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        """
        汎用的なテキスト生成メソッド

        Args:
            prompt: プロンプト
            temperature: 温度パラメータ（0.0-2.0、デフォルト: 0.3）

        Returns:
            LLMの応答テキスト
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "あなたは優秀なデータサイエンティストです。与えられた情報を正確に抽出・整理してください。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=2000
                )
                return response.choices[0].message.content.strip()

            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"   ⚠️ LLMエラー (リトライ {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    raise

    def extract_evaluation_metric(self, description: str, title: str = "") -> str:
        """
        説明文から評価指標を抽出

        Args:
            description: コンペの説明文（英語）
            title: コンペのタイトル（オプション）

        Returns:
            評価指標の名前（例: "F1 Score", "AUC-ROC", "RMSE"）
            見つからない場合は空文字列
        """
        if not description:
            return ""

        prompt = f"""あなたはKaggleコンペティションの分析専門家です。
以下のコンペティション説明文から、評価指標（Evaluation Metric）に関する情報を抽出してください。

【タイトル】
{title}

【説明文】
{description}

【タスク】
評価指標の名前を簡潔に日本語で返してください。

【出力例】
- F1スコア
- AUC-ROC
- 平均絶対誤差（MAE）
- 二乗平均平方根誤差（RMSE）
- 精度（Accuracy）
- IoU（Intersection over Union）

【重要な注意事項】
- 評価指標の名前のみを返す（説明や前置きは不要）
- 説明文に明示的に記載されている場合のみ抽出
- 評価指標の記載がない、または不明確な場合は空文字列を返す
- 推測はしない
- 30文字以内で簡潔に"""

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "あなたはKaggleコンペティションの分析専門家です。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # 一貫性を重視
                    max_tokens=100
                )

                metric = response.choices[0].message.content.strip()

                # 前置きを除去（「評価指標は」「指標:」など）
                metric = metric.replace("評価指標は", "").replace("指標:", "").replace("評価指標:", "").strip()

                # 30文字以内に制限
                if len(metric) > 30:
                    return ""

                return metric

            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"評価指標抽出エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"評価指標抽出エラー（最終試行失敗）: {e}")
                    return ""

        return ""

    def generate_metric_description(self, metric: str, description: str, title: str = "") -> str:
        """
        評価指標の説明を生成

        Args:
            metric: 評価指標の名前（例: "F1スコア", "AUC-ROC"）
            description: コンペの説明文
            title: コンペのタイトル

        Returns:
            評価指標の説明文（100-150文字程度）
        """
        if not metric or not description:
            return ""

        prompt = f"""あなたはKaggleコンペティションの分析専門家です。
以下のコンペティションで使用される評価指標について、初心者にも分かりやすい説明を作成してください。

【タイトル】
{title}

【評価指標】
{metric}

【説明文】
{description}

【タスク】
この評価指標について、以下の内容を含む100-150文字程度の説明を日本語で作成してください：
- 指標の意味
- この指標が何を測定するか
- なぜこのコンペでこの指標が使われるか

【要件】
- 専門用語は分かりやすく説明
- 簡潔で明確な表現
- 前置きや見出しは不要、説明文のみ
- 100-150文字程度"""

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "あなたはKaggleコンペティションの分析専門家です。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=300
                )

                description_text = response.choices[0].message.content.strip()

                # 150文字以内に制限
                if len(description_text) > 200:
                    description_text = description_text[:197] + "..."

                return description_text

            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"指標説明生成エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"指標説明生成エラー（最終試行失敗）: {e}")
                    return ""

        return ""

    def extract_dataset_info(self, data_text: str, title: str = "") -> Dict[str, Any]:
        """
        Data タブのテキストからデータセット情報を抽出

        Args:
            data_text: Data タブのテキスト
            title: コンペのタイトル

        Returns:
            データセット情報の辞書
            {
                "files": ["train.csv", "test.csv", ...],
                "total_size": "1.2 GB",
                "description": "データの概要説明",
                "features": ["特徴1", "特徴2", ...],
                "columns": [{"name": "column1", "description": "説明1"}, ...]
            }
        """
        if not data_text:
            return {
                "files": [],
                "total_size": "",
                "description": "",
                "features": [],
                "columns": []
            }

        prompt = f"""あなたはKaggleコンペティションのデータ分析専門家です。
以下のDataタブの内容から、データセット情報を抽出してください。

【タイトル】
{title}

【Data タブのテキスト】
{data_text}

【タスク】
以下のJSON形式でデータセット情報を出力してください：

{{
  "files": ["ファイル名1", "ファイル名2", "ファイル名3"],
  "total_size": "データセット全体のサイズ（例: 1.2 GB）",
  "description": "データの概要を日本語で簡潔に（150-200文字程度）",
  "features": ["主要な特徴量・カラム1", "特徴量2", "特徴量3"],
  "columns": [
    {{"name": "カラム名1", "description": "カラムの意味・内容"}},
    {{"name": "カラム名2", "description": "カラムの意味・内容"}}
  ]
}}

【要件】
- files: データファイル名のリスト（主要なファイルのみ、最大10個）
- total_size: データセット全体のサイズ（明記されている場合のみ）
- description: データの内容を詳しく説明（150-200文字程度）
- features: 主要な特徴量やカラム名のリスト（簡潔な名前のみ、最大15個）
- columns: カラム名とその説明の配列（各カラムの意味を日本語で明記、重要なカラムのみ、最大20個）
  - name: カラム名（英語のまま）
  - description: カラムの意味・内容を日本語で（30-50文字程度）
- テキストに明記されている情報のみ抽出
- 不明な項目は空文字列または空配列を返す
- JSON形式のみを出力"""

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "あなたはKaggleコンペティションのデータ分析専門家です。JSON形式で回答してください。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1500,
                    response_format={"type": "json_object"}
                )

                result_text = response.choices[0].message.content.strip()
                result = json.loads(result_text)

                # 結果の検証とデフォルト値設定
                if not isinstance(result.get("files"), list):
                    result["files"] = []
                if not isinstance(result.get("total_size"), str):
                    result["total_size"] = ""
                if not isinstance(result.get("description"), str):
                    result["description"] = ""
                if not isinstance(result.get("features"), list):
                    result["features"] = []
                if not isinstance(result.get("columns"), list):
                    result["columns"] = []

                return result

            except json.JSONDecodeError as e:
                if attempt < self.max_retries - 1:
                    print(f"JSON解析エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"JSON解析エラー（最終試行失敗）: {e}")
                    return {
                        "files": [],
                        "total_size": "",
                        "description": "",
                        "features": []
                    }
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"データセット情報抽出エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"データセット情報抽出エラー（最終試行失敗）: {e}")
                    return {
                        "files": [],
                        "total_size": "",
                        "description": "",
                        "features": []
                    }

    def generate_summary(self, description: str, title: str = "", metric: str = "") -> str:
        """
        英語の説明文から構造化された日本語要約を生成

        Args:
            description: コンペの説明文（英語）
            title: コンペのタイトル（オプション）
            metric: 評価指標（オプション）

        Returns:
            構造化要約のJSON文字列
            {
                "overview": "コンペの概要（1-2文）",
                "objective": "何を予測/分類するか",
                "data": "使用するデータの種類",
                "evaluation": {
                    "metric": "評価指標名",
                    "explanation": "評価指標の説明",
                    "why_important": "なぜこの指標が選ばれたか"
                },
                "business_value": "ビジネス上の価値・目的",
                "key_challenges": ["課題1", "課題2"]
            }
        """
        if not description:
            return ""

        metric_section = f"""
【評価指標】
{metric if metric else "情報なし"}
""" if metric else ""

        prompt = f"""あなたはKaggleコンペティションの分析専門家です。
以下のコンペティション情報を分析し、構造化された日本語要約を作成してください。

【タイトル】
{title}

【説明文】
{description}
{metric_section}
【タスク】
以下のJSON形式で要約を出力してください：

{{
  "overview": "コンペの概要を1-2文で簡潔に（50-100文字）",
  "objective": "何を予測/分類/生成するか（30-50文字）",
  "data": "使用するデータの種類（30-50文字）",
  "evaluation": {{
    "metric": "評価指標の正式名称（例：AUC, RMSE, F1-Score等）",
    "explanation": "この評価指標がどのように計算され、何を測定するかの説明（80-120文字）",
    "why_important": "なぜこの評価指標がこのコンペに適しているか、ビジネス的な意義（60-100文字）"
  }},
  "business_value": "ビジネス上の価値や目的（50-80文字）",
  "key_challenges": ["課題1", "課題2", "課題3"]
}}

【要件】
- 各フィールドは日本語で記述
- overview: コンペの全体像を簡潔に
- objective: 具体的な予測対象や目標
- data: データの種類や特徴
- evaluation: 【最重要】評価指標について詳しく説明
  - metric: 指標名（英語でもOK）
  - explanation: 指標の計算方法と意味を初心者にもわかりやすく
  - why_important: なぜこの指標が重要か、ビジネス的背景を含めて
- business_value: なぜこのコンペが重要か
- key_challenges: 技術的な課題や特徴を3-5個の配列で
- 技術用語は適切に日本語化し、必要に応じて補足説明

【出力フォーマット】
JSON形式のみを出力してください。前置きや説明は不要です。"""

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "あなたはKaggleコンペティションの分析専門家です。JSON形式で回答してください。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000,
                    response_format={"type": "json_object"}
                )

                summary_json = response.choices[0].message.content.strip()

                # JSONの検証
                try:
                    parsed = json.loads(summary_json)
                    # 必須フィールドの確認
                    required_fields = ["overview", "objective", "data", "evaluation", "business_value", "key_challenges"]
                    if all(field in parsed for field in required_fields):
                        # evaluationフィールドの詳細チェック
                        if isinstance(parsed["evaluation"], dict):
                            eval_required = ["metric", "explanation", "why_important"]
                            if all(k in parsed["evaluation"] for k in eval_required):
                                return summary_json
                        raise ValueError("evaluationフィールドの構造が不正です")
                    else:
                        raise ValueError("必須フィールドが不足しています")
                except (json.JSONDecodeError, ValueError) as e:
                    if attempt < self.max_retries - 1:
                        print(f"JSON検証エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return ""

            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"要約生成エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"要約生成エラー（最終試行失敗）: {e}")
                    return ""

    def generate_tags(
        self,
        description: str,
        title: str = "",
        metric: str = "",
        available_tags: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, any]:
        """
        コンペティション情報からタグを自動生成

        Args:
            description: コンペの説明文
            title: コンペのタイトル
            metric: 評価指標
            available_tags: 利用可能なタグのマスタ（カテゴリ別）

        Returns:
            {
                "data_types": ["画像", "テキスト"],
                "tags": ["CNN", "Transformer", "物体検出"],
                "domain": "コンピュータビジョン"
            }
        """
        if not description and not title:
            return {
                "data_types": [],
                "tags": [],
                "domain": ""
            }

        # 利用可能なタグのリストを作成
        if available_tags:
            # model_typeを除外
            filtered_tags = {k: v for k, v in available_tags.items() if k != 'model_type'}
            tag_info = json.dumps(filtered_tags, ensure_ascii=False, indent=2)
        else:
            # デフォルトのタグリスト（model_typeは除外）
            tag_info = json.dumps({
                "task_type": ["分類（二値）", "分類（多クラス）", "回帰", "ランキング", "物体検出", "セグメンテーション", "生成", "クラスタリング"],
                "competition_feature": ["不均衡データ", "欠損値多い", "外れ値対策必要", "大規模データ", "小規模データ", "リーク対策必要", "時系列考慮", "ドメイン知識重要", "データ品質課題"],
                "domain": ["医療", "金融", "Eコマース", "自然言語処理", "コンピュータビジョン", "音声認識", "推薦システム", "時系列予測", "その他"]
            }, ensure_ascii=False, indent=2)

        prompt = f"""あなたはKaggleコンペティションの分析専門家です。
以下のコンペティション情報を分析し、適切なタグを選択してください。

【タイトル】
{title}

【説明文】
{description}

【評価指標】
{metric}

【利用可能なタグ】
{tag_info}

【タスク】
上記のコンペティション情報を分析し、以下の形式でJSONを出力してください：

{{
  "data_types": ["該当するデータ種別1", "該当するデータ種別2"],
  "tags": ["該当するタグ1", "該当するタグ2", "該当するタグ3"],
  "domain": "該当するドメイン1つ"
}}

【選択基準】
- data_types: データの種類（1-2個程度）
- tags: 以下の優先順位で選択（合計3-5個程度）
  1. **task_type（必須）**: 何を予測するか（分類/回帰等）を必ず1-2個選択
  2. competition_feature: データや手法の特徴
  3. domain関連のタグがあれば追加
- domain: 最も関連性の高いドメイン1つ

【重要な注意事項 - 厳守】
- **説明文に明示されている情報のみ選択**: 推測は一切禁止
- **task_type**: 以下の厳密な基準で選択
  - 「分類」: "classify", "classification", "identify", "recognize" のキーワードがある場合
  - 「回帰」: "predict" + 連続値（価格、スコア等）のキーワードがある場合
  - 「物体検出」: "object detection", "detect objects", "bounding box", "localization" がある場合のみ
  - 「セグメンテーション」: "segment", "segmentation", "pixel-level" がある場合のみ
  - ⚠️ "detect behaviors", "detect patterns" は「分類」として扱う（物体検出ではない）
- **data_type**: 説明文に"image", "text", "time-series", "tabular"等が明記されている場合のみ選択
- **domain**: 説明文のキーワード（ECG→医療、market→金融、mice→その他等）から明確な場合のみ選択
- **competition_feature**: 説明文に"large dataset", "imbalanced"等が明記されている場合のみ選択
- **確信が持てない場合は選択しない**: 空配列・空文字列を恐れない
- 必ず利用可能なタグリストから選択
- JSON形式のみを出力し、前置きや説明は不要"""

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "あなたはKaggleコンペティションの分析専門家です。JSON形式で回答してください。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,  # より一貫性のある分類のため低めに設定
                    max_tokens=500,
                    response_format={"type": "json_object"}  # JSON形式を強制
                )

                result_text = response.choices[0].message.content.strip()
                result = json.loads(result_text)

                # 結果の検証
                if not isinstance(result.get("data_types"), list):
                    result["data_types"] = []
                if not isinstance(result.get("tags"), list):
                    result["tags"] = []
                if not isinstance(result.get("domain"), str):
                    result["domain"] = ""

                return result

            except json.JSONDecodeError as e:
                if attempt < self.max_retries - 1:
                    print(f"JSON解析エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"JSON解析エラー（最終試行失敗）: {e}")
                    return {
                        "data_types": [],
                        "tags": [],
                        "domain": ""
                    }
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"タグ生成エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"タグ生成エラー（最終試行失敗）: {e}")
                    return {
                        "data_types": [],
                        "tags": [],
                        "domain": ""
                    }

    def enrich_competition(
        self,
        competition: Dict,
        available_tags: Optional[Dict[str, List[str]]] = None,
        data_tab_text: Optional[str] = None
    ) -> Dict:
        """
        コンペティション情報を充実化（要約、タグ、評価指標、データセット情報の生成）

        Args:
            competition: コンペティション情報の辞書
            available_tags: 利用可能なタグのマスタ
            data_tab_text: Dataタブのテキスト（データセット情報抽出用）

        Returns:
            充実化されたコンペティション情報
        """
        # 要約生成
        if not competition.get("summary") and competition.get("description"):
            print(f"要約生成中: {competition.get('title', 'Unknown')}")
            summary = self.generate_summary(
                description=competition.get("description", ""),
                title=competition.get("title", "")
            )
            competition["summary"] = summary

        # 評価指標抽出
        if not competition.get("metric") and competition.get("description"):
            print(f"評価指標抽出中: {competition.get('title', 'Unknown')}")
            metric = self.extract_evaluation_metric(
                description=competition.get("description", ""),
                title=competition.get("title", "")
            )
            competition["metric"] = metric

        # 評価指標の説明生成
        if competition.get("metric") and not competition.get("metric_description") and competition.get("description"):
            print(f"評価指標説明生成中: {competition.get('title', 'Unknown')}")
            metric_description = self.generate_metric_description(
                metric=competition.get("metric", ""),
                description=competition.get("description", ""),
                title=competition.get("title", "")
            )
            competition["metric_description"] = metric_description

        # タグ生成
        if (not competition.get("tags") or not competition.get("data_types")) and competition.get("description"):
            print(f"タグ生成中: {competition.get('title', 'Unknown')}")
            tag_result = self.generate_tags(
                description=competition.get("description", ""),
                title=competition.get("title", ""),
                metric=competition.get("metric", ""),
                available_tags=available_tags
            )

            if not competition.get("data_types"):
                competition["data_types"] = tag_result.get("data_types", [])
            if not competition.get("tags"):
                competition["tags"] = tag_result.get("tags", [])
            if not competition.get("domain"):
                competition["domain"] = tag_result.get("domain", "")

        # データセット情報抽出
        if data_tab_text and not competition.get("dataset_info"):
            print(f"データセット情報抽出中: {competition.get('title', 'Unknown')}")
            dataset_info = self.extract_dataset_info(
                data_text=data_tab_text,
                title=competition.get("title", "")
            )
            if dataset_info:
                competition["dataset_info"] = json.dumps(dataset_info, ensure_ascii=False)

        return competition

    def summarize_discussion(self, content: str, title: str = "") -> str:
        """
        ディスカッションの内容を要約

        Args:
            content: ディスカッションの本文
            title: ディスカッションのタイトル

        Returns:
            要約文（150-200文字程度の日本語）
        """
        if not content:
            return ""

        # 長すぎる場合は最初の部分のみ使用（トークン制限対策）
        max_content_length = 4000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        prompt = f"""あなたはKaggleディスカッションの要約専門家です。
以下のディスカッションを読み、重要なポイントを簡潔に要約してください。

【タイトル】
{title}

【本文】
{content}

【タスク】
このディスカッションの内容を150-200文字程度の日本語で要約してください。

【要件】
- 主要なポイントや結論を含める
- 技術的な内容は具体的に
- 初心者にも分かりやすく
- 箇条書きではなく文章で
- 前置きや見出しは不要、要約文のみ
- 150-200文字程度

【出力例】
このディスカッションでは、特徴量エンジニアリングの重要性について議論されています。特に、カテゴリ変数のエンコーディング手法と欠損値の扱い方に焦点が当てられており、Target Encodingを用いることでスコアが大幅に向上したという報告があります。また、外れ値の検出と除去についても詳しく説明されています。"""

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # コスト削減のためminiを使用
                    messages=[
                        {"role": "system", "content": "あなたはKaggleディスカッションの要約専門家です。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=400
                )

                summary = response.choices[0].message.content.strip()

                # 250文字以内に制限
                if len(summary) > 250:
                    summary = summary[:247] + "..."

                return summary

            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"ディスカッション要約エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"ディスカッション要約エラー（最終試行失敗）: {e}")
                    return ""

        return ""

    def generate_structured_discussion_summary(self, content: str, title: str = "") -> str:
        """
        ディスカッションの内容から構造化された詳細要約を生成（学習用）

        Args:
            content: ディスカッションの本文
            title: ディスカッションのタイトル

        Returns:
            構造化要約のJSON文字列
            {
                "overview": "概要（2-3文）",
                "main_topic": "主なトピック",
                "key_points": ["重要ポイント1", "重要ポイント2", ...],
                "technical_details": "技術的な詳細説明（専門用語含む）",
                "glossary": [
                    {"term": "用語1", "explanation": "初心者向け説明"},
                    {"term": "用語2", "explanation": "初心者向け説明"}
                ],
                "approaches": ["アプローチ1", "アプローチ2"],
                "code_examples": "コード例の説明（ある場合）",
                "results": "結果や結論",
                "related_links": "言及されているリンクやリソース"
            }
        """
        if not content:
            return "{}"

        # 長すぎる場合は最初の部分のみ使用
        max_content_length = 6000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        prompt = f"""あなたはKaggleディスカッションの学習支援専門家です。
以下のディスカッションを読み、初心者の学習に役立つ詳細で構造化された要約を作成してください。

【タイトル】
{title}

【本文】
{content}

【タスク】
以下のJSON形式で構造化された詳細要約を出力してください：

{{
  "overview": "ディスカッション全体の概要を2-3文で（100-150文字）",
  "main_topic": "主なトピックやテーマ（50文字程度）",
  "key_points": [
    "重要ポイント1（具体的に）",
    "重要ポイント2（具体的に）",
    "重要ポイント3（具体的に）"
  ],
  "technical_details": "技術的な詳細説明。専門用語を使って具体的に説明（200-300文字）",
  "glossary": [
    {{"term": "専門用語1", "explanation": "初心者にも分かる説明（50-80文字）"}},
    {{"term": "専門用語2", "explanation": "初心者にも分かる説明（50-80文字）"}}
  ],
  "approaches": [
    "提案されているアプローチや手法1",
    "提案されているアプローチや手法2"
  ],
  "code_examples": "コード例やスニペットについての説明（ある場合、100-150文字）",
  "results": "議論の結果や結論、推奨事項（100-150文字）",
  "related_links": "言及されているツール、ライブラリ、リソース（50-100文字、ない場合は空文字列）"
}}

【要件】
- 全て日本語で記述（技術用語の固有名詞は英語のまま可）
- overview: ディスカッション全体の要点を簡潔に
- main_topic: 何について議論しているか
- key_points: 特に重要なポイントを3-5個の配列で、具体的に
- technical_details: 技術的な詳細を専門用語を使って説明。初心者が学ぶべき内容を含む
- glossary: 本文に出てくる専門用語を3-5個抽出し、初心者向けに説明
  - term: 専門用語（例: "Target Encoding", "Cross Validation", "Overfitting"）
  - explanation: その用語の意味を分かりやすく説明
- approaches: 提案されている手法やアプローチを1-3個の配列で
- code_examples: コード例がある場合、何をするコードか説明
- results: 議論の結論や推奨される対応
- related_links: 言及されているツールやライブラリ名
- 本文に明記されている情報のみ抽出
- 推測はしない
- JSON形式のみを出力（説明や前置きは不要）

【出力例】
{{
  "overview": "このディスカッションでは、カテゴリ変数のエンコーディング手法について議論されています。特にTarget EncodingとOne-Hot Encodingの使い分けや、過学習を防ぐためのテクニックに焦点が当てられています。",
  "main_topic": "カテゴリ変数のエンコーディング手法と過学習対策",
  "key_points": [
    "Target Encodingは高カーディナリティのカテゴリ変数に有効だが、過学習のリスクがある",
    "K-Fold交差検証を使ったTarget Encodingで過学習を軽減できる",
    "One-Hot Encodingは次元数が増えるが、過学習のリスクは低い",
    "特徴量の数とデータサイズのバランスを考慮して手法を選択すべき"
  ],
  "technical_details": "Target Encodingは、各カテゴリの値を目的変数の平均値で置き換える手法です。高カーディナリティ（多数のユニーク値を持つ）カテゴリ変数に対して、One-Hot Encodingよりもメモリ効率が良く、モデルの精度向上に寄与します。ただし、学習データに対して過度に最適化されてしまう過学習のリスクがあるため、K-Fold交差検証を用いて各Foldごとに異なるエンコーディングを適用することで、汎化性能を保つことができます。",
  "glossary": [
    {{"term": "Target Encoding", "explanation": "カテゴリ変数を目的変数の平均値で数値に変換する手法。例えば、都市名を各都市の平均年収で置き換えるイメージです。"}},
    {{"term": "One-Hot Encoding", "explanation": "カテゴリ変数を0と1のバイナリ列に変換する手法。各カテゴリごとに新しい列を作り、該当する列だけ1にする方法です。"}},
    {{"term": "過学習（Overfitting）", "explanation": "機械学習モデルが学習データに過度に適合してしまい、未知のデータに対する予測精度が低下する現象。訓練データの特徴を暗記してしまうイメージです。"}},
    {{"term": "K-Fold交差検証", "explanation": "データをK個に分割し、K回学習と検証を繰り返す手法。モデルの汎化性能を正確に評価し、過学習を防ぐために使われます。"}}
  ],
  "approaches": [
    "K-Fold交差検証を使ったTarget Encodingで過学習を防ぐ",
    "カーディナリティが低い変数にはOne-Hot Encoding、高い変数にはTarget Encodingを使う",
    "スムージング（平滑化）を適用してTarget Encodingの安定性を向上させる"
  ],
  "code_examples": "Pythonのcategory_encodersライブラリを使ったTarget Encodingの実装例が示されています。K-Foldを組み合わせた実装により、各Foldで異なるエンコーディング値を使用することで過学習を防いでいます。",
  "results": "高カーディナリティのカテゴリ変数にはTarget Encodingが有効だが、必ずK-Fold交差検証と組み合わせて使用すべきです。低カーディナリティの場合はOne-Hot Encodingの方が安全で解釈性も高いため、データの特性に応じて使い分けることが推奨されます。",
  "related_links": "category_encodersライブラリ、scikit-learn"
}}"""

        for attempt in range(self.max_retries):
            try:
                # ディスカッション詳細の要約にはgpt-4oを使用
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # コスト削減のためminiを使用
                    messages=[
                        {"role": "system", "content": "あなたはKaggleディスカッションの学習支援専門家です。JSON形式で回答してください。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                    response_format={"type": "json_object"}
                )

                result_text = response.choices[0].message.content.strip()

                # JSON検証
                try:
                    result = json.loads(result_text)

                    # 必須フィールドの確認とデフォルト値設定
                    if not isinstance(result.get("overview"), str):
                        result["overview"] = ""
                    if not isinstance(result.get("main_topic"), str):
                        result["main_topic"] = ""
                    if not isinstance(result.get("key_points"), list):
                        result["key_points"] = []
                    if not isinstance(result.get("technical_details"), str):
                        result["technical_details"] = ""
                    if not isinstance(result.get("glossary"), list):
                        result["glossary"] = []
                    if not isinstance(result.get("approaches"), list):
                        result["approaches"] = []
                    if not isinstance(result.get("code_examples"), str):
                        result["code_examples"] = ""
                    if not isinstance(result.get("results"), str):
                        result["results"] = ""
                    if not isinstance(result.get("related_links"), str):
                        result["related_links"] = ""

                    return json.dumps(result, ensure_ascii=False)

                except json.JSONDecodeError:
                    if attempt < self.max_retries - 1:
                        print(f"JSON解析エラー（リトライ {attempt + 1}/{self.max_retries}）")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return "{}"

            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"構造化ディスカッション要約生成エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"構造化ディスカッション要約生成エラー（最終試行失敗）: {e}")
                    return "{}"

        return "{}"

    def translate_and_organize_discussion(self, content: str) -> str:
        """
        ディスカッションの原文を構造化して整理（情報を失わずに詳細に）

        Args:
            content: ディスカッションの本文（英語）

        Returns:
            構造化・整理されたテキスト（日本語、詳細版）
        """
        if not content:
            return ""

        # 長すぎる場合は最初の部分のみ使用
        max_content_length = 6000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        prompt = f"""あなたはKaggleディスカッションの構造化・整理専門家です。
以下の英語のディスカッションを読み、実装の詳細を失わずに構造化して整理してください。

【原文】
{content}

【タスク】
この英語のディスカッションを以下の構造に整理して日本語で出力してください。
該当するセクションがない場合は省略してください。

【最重要原則】
⚠️ **実装の具体的内容を省略せず、実際に何をしたのかを明確に記載すること**
⚠️ **抽象的な要約ではなく、具体的な実装ステップ・パラメータ・設定を保持すること**
⚠️ **数値、閾値、ハイパーパラメータ、epoch数などの具体的な値を必ず含めること**

【出力構造】
━━━ 背景・導入 ━━━
（ディスカッションの文脈や前提条件を詳しく。2-4文で）

━━━ 問題点・課題 ━━━
（解決しようとしている問題を具体的に。どういう状況で何が起きたか）
• 問題点1: 具体的な症状や状況の詳細な説明
• 問題点2: 数値やエラーメッセージなどを含めた詳細
• 問題点3: 試して失敗した内容も含める

━━━ 提案手法・アプローチ ━━━
（具体的な解決策の実装内容を詳細に）
• アプローチ1: 何をどのように実装したか（パラメータ、設定値、具体的な処理内容）
• アプローチ2: 使用したモデル・手法・ライブラリと、その設定詳細
• アプローチ3: なぜその設定にしたのか、試行錯誤の過程も含める

━━━ 実装の詳細 ━━━
（実際のコード例と具体的な実装方法を詳細に。ここが最も重要）
• 実装手順1: 具体的な処理内容（関数名、パラメータ、設定値を明記）
  - 使用した関数・メソッド名
  - 設定したパラメータと値（例: learning_rate=0.01, n_estimators=500）
  - 前処理の具体的内容（欠損値処理、スケーリング方法など）
• 実装手順2: データ処理の詳細
  - どのカラムをどう処理したか
  - 特徴量エンジニアリングの具体的な作成方法
  - 変換方法と変換後の形式
• 実装手順3: モデル学習の詳細
  - 使用したモデルと具体的な設定
  - ハイパーパラメータの値
  - 交差検証の分割数や方法

＜コード例がある場合はそのまま記載＞
```
コードブロック（コメントも含めてそのまま保持）
```

コードの処理内容の詳細:
• このコードが何をしているか行ごとに説明
• パラメータの意味と設定理由
• 処理フローの詳細な説明

実装のポイント:
• ポイント1: 何をどう実装したか具体的に
• ポイント2: 設定値やパラメータの根拠
• ポイント3: 試行錯誤で分かったこと

━━━ 結果・考察 ━━━
（実験結果やパフォーマンスについて数値を含めて詳しく）
• 結果1: 具体的なスコア・精度の数値（例: Public LB 0.875 → 0.892に改善）
• 結果2: 各手法の比較結果と数値
• 結果3: 失敗した試みとその数値・原因
• 考察: なぜこの結果になったのか、分析内容

━━━ まとめ・推奨事項 ━━━
（具体的な実装内容と推奨設定を詳しく）
• ポイント1: 具体的に何をすべきか（設定値、パラメータ、手順を明記）
• ポイント2: 推奨する実装方法と理由
• ポイント3: 避けるべきこととその理由

【重要なルール】
1. **実装の具体的内容を最優先**: 抽象的な説明ではなく、実際に何をしたかを詳細に記載
2. **数値・パラメータ・設定値を必ず含める**: learning_rate, epochs, batch_size, n_folds, threshold など
3. **処理ステップを省略しない**: 前処理→特徴量作成→モデル学習→予測の各段階を具体的に
4. **試行錯誤の過程も記載**: 何を試して、どういう結果になったか
5. **コードブロックはそのまま保持**（コメントも翻訳しない）
6. **カラム名、関数名、変数名は英語のまま**
   例: customer_id, feature_importance, train_test_split
7. **技術用語は「日本語（英語）」の形式で表示**
   例: "cross validation" → "交差検証（Cross Validation）"
   例: "overfitting" → "過学習（Overfitting）"
   例: "feature engineering" → "特徴量エンジニアリング（Feature Engineering）"
8. **固有名詞**（XGBoost, LightGBM, Kaggle等）は英語のまま
9. **数値やスコアは全て記載**: Public/Private LB、CV Score、改善幅など
10. **箇条書き**と**入れ子構造**を活用して詳細を整理
11. **各セクション**は━━━で区切る
12. **該当しないセクション**は出力しない
13. **自然で読みやすい日本語**にするが、情報量は削らない
14. **要約厳禁**: 元の情報をできるだけそのまま保持。抽象化・一般化しない

【出力形式】
構造化されたテキストのみを出力してください。前置きや説明は不要です。"""

        for attempt in range(self.max_retries):
            try:
                # ディスカッション詳細の和訳・整理にはgpt-4oを使用
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # コスト削減のためminiを使用
                    messages=[
                        {"role": "system", "content": "あなたはKaggleディスカッションの構造化・整理専門家です。情報を失わずに詳細に整理してください。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=4000  # 詳細な出力のためトークン数を増やす
                )

                organized_text = response.choices[0].message.content.strip()
                return organized_text

            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"構造化エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"構造化エラー（最終試行失敗）: {e}")
                    return ""

        return ""

    def extract_solution_techniques(self, content: str, title: str = "") -> str:
        """
        解法の本文から使用技術を抽出

        Args:
            content: 解法の本文
            title: 解法のタイトル

        Returns:
            技術のJSON文字列（配列形式）
            例: ["XGBoost", "特徴量エンジニアリング", "Target Encoding", "アンサンブル学習"]
        """
        if not content:
            return "[]"

        # 長すぎる場合は最初の部分のみ使用（トークン制限対策）
        max_content_length = 4000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        prompt = f"""あなたはKaggle解法の技術分析専門家です。
以下の解法を読み、使用されている技術・手法を抽出してください。

【タイトル】
{title}

【本文】
{content}

【タスク】
この解法で使用されている技術・手法を、名前・英語表記・説明を含むJSON配列形式で出力してください。

【抽出対象】
1. **機械学習モデル**: XGBoost, LightGBM, CatBoost, Random Forest, Neural Networks, Transformer, CNN, RNN, LSTM など
2. **前処理・特徴量エンジニアリング**: Target Encoding, One-Hot Encoding, 特徴量選択, 欠損値補完, 正規化, 標準化 など
3. **学習テクニック**: アンサンブル学習, スタッキング, K-Fold交差検証, Stratified K-Fold, ハイパーパラメータチューニング など
4. **データ拡張**: Data Augmentation, Mixup, CutMix など
5. **その他の重要な技術**: Transfer Learning, Fine-tuning, Attention機構, 事前学習モデル など

【要件】
- 本文に明示的に記載されている技術のみ抽出
- 各技術に対して以下を含める：
  - name: 日本語の技術名（固有名詞はそのまま）
  - english: 英語の技術名
  - description: その技術の簡潔な説明（50文字程度）
- 重要度の高い順に並べる
- 5-10個程度に絞る
- 推測は禁止、本文に書かれていない技術は含めない
- JSON配列形式のみを出力（説明や前置きは不要）

【出力例】
[
  {{"name": "XGBoost", "english": "XGBoost", "description": "勾配ブースティングの高速実装。表形式データで高精度を実現"}},
  {{"name": "特徴量エンジニアリング", "english": "Feature Engineering", "description": "データから有用な特徴を作成・選択する手法"}},
  {{"name": "Target Encoding", "english": "Target Encoding", "description": "カテゴリ変数を目的変数の統計量で数値化する手法"}},
  {{"name": "K-Fold交差検証", "english": "K-Fold Cross Validation", "description": "データをK個に分割して汎化性能を評価する手法"}}
]"""

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # コスト削減のためminiを使用
                    messages=[
                        {"role": "system", "content": "あなたはKaggle解法の技術分析専門家です。JSON形式で回答してください。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=300,
                    response_format={"type": "json_object"}
                )

                result_text = response.choices[0].message.content.strip()

                # JSON配列が直接返される場合と、{"techniques": [...]}の形式の場合に対応
                try:
                    result = json.loads(result_text)

                    # {"techniques": [...]} 形式の場合
                    if isinstance(result, dict) and "techniques" in result:
                        techniques = result["techniques"]
                    # 直接配列の場合（本来はこれが期待される形式）
                    elif isinstance(result, list):
                        techniques = result
                    # その他の場合は空配列
                    else:
                        techniques = []

                    # 配列であることを確認
                    if not isinstance(techniques, list):
                        techniques = []

                    return json.dumps(techniques, ensure_ascii=False)

                except json.JSONDecodeError:
                    if attempt < self.max_retries - 1:
                        print(f"JSON解析エラー（リトライ {attempt + 1}/{self.max_retries}）")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return "[]"

            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"技術抽出エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"技術抽出エラー（最終試行失敗）: {e}")
                    return "[]"

        return "[]"

    def generate_structured_solution_summary(self, content: str, title: str = "") -> str:
        """
        解法の本文から構造化された要約を生成

        Args:
            content: 解法の本文
            title: 解法のタイトル

        Returns:
            構造化要約のJSON文字列
            {
                "overview": "概要（2-3文）",
                "approach": "アプローチ・手法",
                "key_points": ["ポイント1", "ポイント2", ...],
                "results": "結果・スコア",
                "techniques": ["技術1", "技術2", ...]
            }
        """
        if not content:
            return "{}"

        # 長すぎる場合は最初の部分のみ使用
        max_content_length = 5000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        prompt = f"""あなたはKaggle解法の分析専門家です。
以下の解法を読み、構造化された要約を作成してください。

【タイトル】
{title}

【本文】
{content}

【タスク】
以下のJSON形式で構造化された要約を出力してください：

{{
  "overview": "解法の概要を2-3文で簡潔に（100-150文字）",
  "approach": "アプローチや手法の説明（100-200文字）",
  "key_points": [
    "重要なポイント1",
    "重要なポイント2",
    "重要なポイント3"
  ],
  "results": "結果やスコア、順位などの成果（50-100文字、記載がない場合は空文字列）",
  "techniques": [
    {{"name": "使用技術1（日本語）", "english": "English Term 1", "description": "技術の簡潔な説明"}},
    {{"name": "使用技術2（日本語）", "english": "English Term 2", "description": "技術の簡潔な説明"}}
  ]
}}

【要件】
- 全て日本語で記述（技術名の固有名詞はそのまま）
- overview: 解法の全体像を簡潔に、専門用語には英語表記を併記
- approach: どのような手法・アプローチを取ったか、専門用語には英語表記を併記
- key_points: 特に重要なポイントを3-5個の配列で、専門用語には英語表記を併記
- results: 達成したスコアや順位（明記されている場合のみ）
- techniques: 各技術にname（日本語）、english（英語）、description（説明50文字程度）を含める
- 本文に明記されている情報のみ抽出
- 推測はしない
- JSON形式のみを出力（説明や前置きは不要）

【出力例】
{{
  "overview": "この解法では、XGBoost (Extreme Gradient Boosting) とLightGBM (Light Gradient Boosting Machine) のアンサンブル (Ensemble) を使用し、特徴量エンジニアリング (Feature Engineering) に重点を置いています。5-Fold交差検証 (5-Fold Cross Validation) により安定したモデルを構築しました。",
  "approach": "まず、データの前処理として欠損値補完 (Missing Value Imputation) と外れ値除去 (Outlier Removal) を実施。次に、Target EncodingとOne-Hot Encodingを組み合わせた特徴量エンジニアリングを行いました。",
  "key_points": [
    "Target Encodingによるカテゴリ変数 (Categorical Variables) の効果的な変換",
    "5-Fold Stratified交差検証 (Stratified K-Fold Cross Validation) による過学習防止 (Overfitting Prevention)",
    "XGBoostとLightGBMの重み付きアンサンブル (Weighted Ensemble)"
  ],
  "results": "Public LB: 0.875, Private LB: 0.872で5位を獲得",
  "techniques": [
    {{"name": "XGBoost", "english": "XGBoost", "description": "勾配ブースティングの高速実装。表形式データで高精度を実現"}},
    {{"name": "LightGBM", "english": "LightGBM", "description": "Microsoft製の軽量で高速な勾配ブースティングフレームワーク"}},
    {{"name": "Target Encoding", "english": "Target Encoding", "description": "カテゴリ変数を目的変数の統計量で数値化する手法"}},
    {{"name": "5-Fold交差検証", "english": "5-Fold Cross Validation", "description": "データを5分割して汎化性能を評価する手法"}}
  ]
}}"""

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # コスト削減のためminiを使用
                    messages=[
                        {"role": "system", "content": "あなたはKaggle解法の分析専門家です。JSON形式で回答してください。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1200,
                    response_format={"type": "json_object"}
                )

                result_text = response.choices[0].message.content.strip()

                # JSON検証
                try:
                    result = json.loads(result_text)

                    # 必須フィールドの確認とデフォルト値設定
                    if not isinstance(result.get("overview"), str):
                        result["overview"] = ""
                    if not isinstance(result.get("approach"), str):
                        result["approach"] = ""
                    if not isinstance(result.get("key_points"), list):
                        result["key_points"] = []
                    if not isinstance(result.get("results"), str):
                        result["results"] = ""
                    if not isinstance(result.get("techniques"), list):
                        result["techniques"] = []

                    return json.dumps(result, ensure_ascii=False)

                except json.JSONDecodeError:
                    if attempt < self.max_retries - 1:
                        print(f"JSON解析エラー（リトライ {attempt + 1}/{self.max_retries}）")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return "{}"

            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"構造化要約生成エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"構造化要約生成エラー（最終試行失敗）: {e}")
                    return "{}"

        return "{}"

    def summarize_notebook(self, content: str, title: str = "") -> str:
        """
        ノートブックの内容を簡潔に要約（コードの詳細は不要、全体像を把握）

        Args:
            content: ノートブックの本文（コード+マークダウン）
            title: ノートブックのタイトル

        Returns:
            構造化要約のJSON文字列
            {
                "purpose": "このノートブックの目的（50-80文字）",
                "data_overview": "使用データの概要（50-80文字）",
                "input_data": {
                    "format": "データ形式",
                    "columns": ["カラム1", "カラム2"],
                    "size": "データサイズ"
                },
                "output_data": {
                    "type": "出力タイプ",
                    "description": "出力の説明"
                },
                "approach": "アプローチ・手法（100-150文字）",
                "processing_steps": [
                    "ステップ1の説明",
                    "ステップ2の説明"
                ],
                "key_techniques": [
                    {"name": "手法1", "explanation": "手法1の説明"},
                    {"name": "手法2", "explanation": "手法2の説明"}
                ],
                "models_used": [
                    {"name": "モデル1", "explanation": "モデル1の説明"},
                    {"name": "モデル2", "explanation": "モデル2の説明"}
                ],
                "glossary": [
                    {"term": "専門用語1", "explanation": "用語1の説明"},
                    {"term": "専門用語2", "explanation": "用語2の説明"}
                ],
                "results": "結果やスコア（あれば、50-100文字）",
                "useful_for": "どんな人に役立つか（50-80文字）"
            }
        """
        if not content:
            return "{}"
        
        # 長すぎる場合は制限
        max_content_length = 8000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        prompt = f"""あなたはKaggleノートブックの概要分析専門家です。
以下のノートブックを読み、「何のために」「何をしているか」「インプット・アウトプット」「処理フロー」を明確に要約してください。
コードの詳細な実装は不要ですが、具体的な処理の流れは必須です。

【タイトル】
{title}

【本文（コード+マークダウン）】
{content}

【タスク】
以下のJSON形式で詳細な要約を出力してください：

{{
  "purpose": "このノートブックの目的・ゴールを1文で（50-80文字）",
  "data_overview": "どのようなデータを使っているか（50-80文字）",
  "input_data": {{
    "format": "データ形式（例: CSV, JSON, 画像ファイル等）",
    "columns": ["主要なカラム名1", "カラム名2", "カラム名3"],
    "size": "データサイズや件数（例: 100万行、画像10万枚等）"
  }},
  "output_data": {{
    "type": "出力タイプ（例: 予測結果CSV, 提出ファイル, 可視化グラフ等）",
    "description": "出力の内容説明（50-80文字）"
  }},
  "processing_steps": [
    "具体的な処理ステップ1（例: データ読み込みと欠損値確認）",
    "処理ステップ2（例: カテゴリ変数をOne-Hot Encoding）",
    "処理ステップ3（例: XGBoostでモデル学習）",
    "処理ステップ4（例: テストデータで予測して提出ファイル作成）"
  ],
  "approach": "どのようなアプローチ・手法で問題を解決しているか（100-150文字）",
  "key_techniques": [
    {{
      "name": "使用している主要な手法1（例: 探索的データ分析（EDA））",
      "explanation": "その手法が何をするものか、初心者向けに簡潔に説明（30-50文字）"
    }},
    {{
      "name": "使用している主要な手法2",
      "explanation": "手法2の説明（30-50文字）"
    }}
  ],
  "models_used": [
    {{
      "name": "使用しているモデル1（例: XGBoost）",
      "explanation": "そのモデルが何をするものか、初心者向けに簡潔に説明（30-50文字）"
    }},
    {{
      "name": "使用しているモデル2",
      "explanation": "モデル2の説明（30-50文字）"
    }}
  ],
  "glossary": [
    {{
      "term": "本文に出てくる重要な専門用語1（例: 特徴量エンジニアリング）",
      "explanation": "その用語の意味を初心者向けに分かりやすく説明（40-60文字）"
    }},
    {{
      "term": "重要な専門用語2",
      "explanation": "用語2の説明（40-60文字）"
    }}
  ],
  "results": "達成した結果やスコア（明記されている場合のみ、50-100文字、なければ空文字列）",
  "useful_for": "このノートブックはどんな人に役立つか（50-80文字）"
}}

【要件】
- **処理フローを明確に**: 何を入力して、どう処理して、何を出力するかを具体的に
- **インプット/アウトプットは必須**: 必ずinput_dataとoutput_dataを記載
- **処理ステップは時系列順**: processing_stepsは実際の処理順序で記載（4-6ステップ程度）
- **コードの詳細実装は不要**: パラメータや具体的なコード内容は省略
- **用語の説明を必ず含める**: 初心者が理解できるように各技術・モデル・用語に説明を追加

【各フィールドの詳細】
- purpose: EDA（探索的データ分析）、ベースライン作成、高精度モデル構築、など
- data_overview: データの種類や規模を簡潔に（例: 顧客購買履歴、画像データ10万枚）
- input_data: **必須** 入力データの詳細
  - format: CSV、JSON、画像ファイル、テキストファイル等の形式
  - columns: 主要なカラム名を3-5個程度リストアップ（カラムがない場合は空配列）
  - size: データサイズや件数（例: "100万行", "画像10万枚", "テキスト5000件"）
- output_data: **必須** 出力の詳細
  - type: 予測結果CSV、提出ファイル、可視化グラフ、分析レポート等
  - description: 出力の内容を具体的に説明（50-80文字）
- processing_steps: **必須** 処理の流れを時系列順に4-6ステップで記載
  - 各ステップは「何をしているか」が明確にわかるように（30-60文字）
  - 例: "trainデータとtestデータを読み込み、基本統計量を確認"
- approach: 全体的なアプローチを説明（例: まずEDAで傾向把握→特徴量作成→XGBoostで予測）
- key_techniques: 3-5個程度の主要な手法（各手法にname/explanationを含める）
  - name: 手法名（日本語と英語を併記、例: "探索的データ分析（EDA）"）
  - explanation: その手法が何をするものか、初心者向けに30-50文字で説明
- models_used: 使用しているモデル名（1-3個、EDAのみの場合は空配列、各モデルにname/explanationを含める）
  - name: モデル名（例: "XGBoost", "LightGBM"）
  - explanation: そのモデルが何をするものか、初心者向けに30-50文字で説明
- glossary: 本文に出てくる重要な専門用語を3-5個抽出し、初心者向けに説明（各用語にterm/explanationを含める）
  - term: 専門用語（例: "特徴量エンジニアリング", "交差検証", "過学習"）
  - explanation: その用語の意味を初心者向けに40-60文字で説明
- results: Public LB、CV Scoreなどの数値（明記されている場合のみ）
- useful_for: 初心者向けEDA、特徴量作成の参考、アンサンブル手法の学習、など
- 推測は禁止、本文に書かれている内容のみ
- JSON形式のみを出力（説明や前置きは不要）

【出力例】
{{
  "purpose": "初心者向けに基本的な探索的データ分析（EDA）とベースライン予測モデルを構築",
  "data_overview": "顧客の購買履歴（10万件）とアイテムのメタデータを使用",
  "input_data": {{
    "format": "CSV",
    "columns": ["customer_id", "item_id", "purchase_date", "price", "quantity"],
    "size": "trainデータ: 10万行、testデータ: 3万行"
  }},
  "output_data": {{
    "type": "予測結果CSV（submission.csv）",
    "description": "各顧客の次回購入商品を予測し、提出形式に整形したファイル"
  }},
  "processing_steps": [
    "trainデータとtestデータを読み込み、基本統計量とデータ型を確認",
    "欠損値を補完し、purchase_dateから曜日・月の特徴量を作成",
    "顧客ごとのリピート購入率と人気商品ランキングを集計",
    "カテゴリ変数をOne-Hot Encodingで数値化",
    "LightGBMで5-Fold交差検証を実施しながらモデルを学習",
    "testデータで予測を実行し、submission.csvとして保存"
  ],
  "approach": "まず、購買データの時系列傾向と顧客セグメント分析を実施。次に、リピート購入率や人気商品を特徴量として作成し、LightGBMで予測モデルを構築。最後にCV検証で汎化性能を確認。",
  "key_techniques": [
    {{
      "name": "探索的データ分析（EDA）",
      "explanation": "データの特徴や傾向を可視化・分析して理解する手法"
    }},
    {{
      "name": "時系列データの可視化",
      "explanation": "時間経過に伴うデータの変化をグラフで表現する手法"
    }},
    {{
      "name": "特徴量エンジニアリング（Feature Engineering）",
      "explanation": "予測精度を高めるためにデータから有用な特徴を作成する手法"
    }},
    {{
      "name": "K-Fold交差検証（K-Fold Cross Validation）",
      "explanation": "データを分割して複数回学習・評価し、モデルの性能を正確に測る手法"
    }}
  ],
  "models_used": [
    {{
      "name": "LightGBM",
      "explanation": "高速で高精度な機械学習モデル。表形式データの予測に強い"
    }}
  ],
  "glossary": [
    {{
      "term": "リピート購入率",
      "explanation": "同じ顧客が繰り返し購入する割合。顧客ロイヤリティの指標"
    }},
    {{
      "term": "CV検証（Cross Validation）",
      "explanation": "モデルの汎化性能を評価するためにデータを分割して検証する手法"
    }},
    {{
      "term": "ベースラインモデル",
      "explanation": "最初に作る単純なモデル。これを基準に改善を重ねる"
    }}
  ],
  "results": "Public LB: 0.021、CV Score: 0.0205",
  "useful_for": "Kaggle初心者がEDAの基本とベースラインモデルの作り方を学ぶのに最適"
}}

【重要な原則】
1. **簡潔さを最優先**: 具体的なパラメータ値やコードの詳細は不要
2. **全体像の把握**: 「このノートブックを読むと何が分かるか」を明確に
3. **技術名は正確に**: モデル名、手法名は正確に記載（ただし説明は簡潔に）
4. **初心者目線**: 全ての技術・モデル・用語に分かりやすい説明を追加
5. **役立ち度を明示**: useful_forで対象者を明確に（初心者向け、中級者向け、特定手法の学習用など）
6. **用語説明は必須**: glossaryフィールドで重要な専門用語を3-5個抽出し、初心者向けに説明

【出力フォーマット】
JSON形式のみを出力してください。前置きや説明は不要です。"""

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # コスト削減のためminiを使用
                    messages=[
                        {"role": "system", "content": "あなたはKaggleノートブックの概要分析専門家です。JSON形式で回答してください。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1500,  # 用語説明が増えるのでトークン数を増やす
                    response_format={"type": "json_object"}
                )

                result_text = response.choices[0].message.content.strip()

                # JSON検証
                try:
                    result = json.loads(result_text)

                    # 必須フィールドの確認とデフォルト値設定
                    if not isinstance(result.get("purpose"), str):
                        result["purpose"] = ""
                    if not isinstance(result.get("data_overview"), str):
                        result["data_overview"] = ""
                    if not isinstance(result.get("approach"), str):
                        result["approach"] = ""
                    if not isinstance(result.get("key_techniques"), list):
                        result["key_techniques"] = []
                    if not isinstance(result.get("models_used"), list):
                        result["models_used"] = []
                    if not isinstance(result.get("glossary"), list):
                        result["glossary"] = []
                    if not isinstance(result.get("results"), str):
                        result["results"] = ""
                    if not isinstance(result.get("useful_for"), str):
                        result["useful_for"] = ""

                    return json.dumps(result, ensure_ascii=False)

                except json.JSONDecodeError:
                    if attempt < self.max_retries - 1:
                        print(f"JSON解析エラー（リトライ {attempt + 1}/{self.max_retries}）")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return "{}"

            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"ノートブック要約生成エラー（リトライ {attempt + 1}/{self.max_retries}）: {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"ノートブック要約生成エラー（最終試行失敗）: {e}")
                    return "{}"

        return "{}"


# グローバルインスタンス（シングルトンパターン）
_llm_service_instance = None


def get_llm_service() -> LLMService:
    """LLMサービスのインスタンスを取得（シングルトン）"""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance
