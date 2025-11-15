"""
LLMサービス

OpenAI GPT-4oを使用してコンペティション情報を分析し、
日本語要約とタグを生成します。
"""

import os
import json
from typing import List, Dict, Optional
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
        self.model = "gpt-4o"  # GPT-4o（miniではない）
        self.max_retries = 3
        self.retry_delay = 2  # 秒

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

    def generate_summary(self, description: str, title: str = "") -> str:
        """
        英語の説明文から構造化された日本語要約を生成

        Args:
            description: コンペの説明文（英語）
            title: コンペのタイトル（オプション）

        Returns:
            構造化要約のJSON文字列
            {
                "overview": "コンペの概要（1-2文）",
                "objective": "何を予測/分類するか",
                "data": "使用するデータの種類",
                "business_value": "ビジネス上の価値・目的",
                "key_challenges": ["課題1", "課題2"]
            }
        """
        if not description:
            return ""

        prompt = f"""あなたはKaggleコンペティションの分析専門家です。
以下のコンペティション情報を分析し、構造化された日本語要約を作成してください。

【タイトル】
{title}

【説明文】
{description}

【タスク】
以下のJSON形式で要約を出力してください：

{{
  "overview": "コンペの概要を1-2文で簡潔に（50-100文字）",
  "objective": "何を予測/分類/生成するか（30-50文字）",
  "data": "使用するデータの種類（30-50文字）",
  "business_value": "ビジネス上の価値や目的（50-80文字）",
  "key_challenges": ["課題1", "課題2", "課題3"]
}}

【要件】
- 各フィールドは日本語で記述
- overview: コンペの全体像を簡潔に
- objective: 具体的な予測対象や目標
- data: データの種類や特徴
- business_value: なぜこのコンペが重要か
- key_challenges: 技術的な課題や特徴を3-5個の配列で
- 技術用語は適切に日本語化

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
                    required_fields = ["overview", "objective", "data", "business_value", "key_challenges"]
                    if all(field in parsed for field in required_fields):
                        return summary_json
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
        available_tags: Optional[Dict[str, List[str]]] = None
    ) -> Dict:
        """
        コンペティション情報を充実化（要約とタグ生成）

        Args:
            competition: コンペティション情報の辞書
            available_tags: 利用可能なタグのマスタ

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

        return competition


# グローバルインスタンス（シングルトンパターン）
_llm_service_instance = None


def get_llm_service() -> LLMService:
    """LLMサービスのインスタンスを取得（シングルトン）"""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance
