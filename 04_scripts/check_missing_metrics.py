"""
評価指標のマスターデータチェックスクリプト

データベース内の評価指標とフロントエンドのMETRIC_GROUPSを比較し、
未分類の指標を検出します。

Usage:
    python check_missing_metrics.py
"""

import sys
import sqlite3
from pathlib import Path

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "02_backend"))

from app.config import DATABASE_PATH

# フロントエンドのMETRIC_GROUPSマスターデータ（同期が必要）
METRIC_GROUPS = {
    '分類': {
        'AUC系': ['ROC AUC', 'PR-AUC', 'AUC', 'pAUC'],
        'F-Score系': ['F1', 'Macro F1', 'Micro F1', 'F2', 'F-beta', 'Micro F-beta', 'F0.5', 'pF1'],
        'Log Loss系': ['Log Loss', 'Weighted Log Loss', 'GLL'],
        'Accuracy系': ['Accuracy', 'Weighted Accuracy', 'MAA', 'mAA', 'Balanced Accuracy'],
        'その他': ['Dice', 'Quadratic Weighted Kappa', 'Matthews Correlation Coefficient', 'Cohen Kappa Score', 'IoU', 'Surface Dice', 'Surface Dice, TopoScore, VOI', 'Jaccard score', 'word-level Jaccard score', 'Brier score', 'Average Brier Bracket Score']
    },
    '回帰': {
        'RMSE系': ['RMSE', 'RMSPE', 'RMSLE', 'RMSSE', 'MCRMSE', 'MRRMSE'],
        'MAE系': ['MAE', 'Weighted MAE', 'Mean Angular Error', 'MCMAE'],
        '相関系': ['Pearson Correlation', 'Spearman Correlation', 'Kendall Tau Correlation', 'Mean Pearson'],
        'その他': ['R²', 'Mean Cosine Similarity', 'SMAPE', 'Normalized Gini Coefficient']
    },
    'ランキング': {
        'MAP系': ['MAP', 'MAP@3', 'MAP@5', 'MAP@12', 'MAP@25', 'MAP@50', 'MAP@100'],
        'その他': ['Padded cMAP', 'Average Precision', 'Global Average Precision', 'mean Average Precision @ 100', 'mean Precision @ 5', 'Weighted Label Ranking Average Precision', 'Recall@20', 'top-3 error rate']
    },
    'その他': {
        'カスタム': ['Custom', 'Skill Rating', 'Sharpe Ratio'],
        '距離・誤差系': ['mean position error', 'mean distance error', 'distance error', 'Sharpened Cosine Similarity'],
        '文字列類似度': ['normalized total levenshtein distance', 'Levenshtein Mean', 'Word Error Rate'],
        '確率・統計': ['Perplexity', 'Negative Log-Likelihood', 'Laplace Log Likelihood', 'Kullback Leibler divergence', 'Continuous Ranked Probability Score', 'Weighted Scaled Pinball Loss', 'Stratified Concordance Index'],
        '画像・構造評価': ['TM-score', 'MiFID', 'SVG Image Fidelity Score', 'SNR'],
        'ゲーム・シミュレーション': ['utility score', 'penalty cost', 'moves', 'halite'],
        'その他カスタム': ['gini stability', 'Cumulative Score', 'Average Agreement', 'length']
    }
}


def get_all_metrics_from_db() -> dict:
    """データベースから全評価指標を取得（件数付き）"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT metric, COUNT(*) as count
        FROM competitions
        WHERE metric IS NOT NULL
        GROUP BY metric
        ORDER BY count DESC
    """)

    metrics = {}
    for row in cursor.fetchall():
        metrics[row[0]] = row[1]

    conn.close()
    return metrics


def get_all_metrics_from_master() -> set:
    """METRIC_GROUPSマスターデータから全評価指標を取得"""
    metrics = set()
    for category, subcategories in METRIC_GROUPS.items():
        for subcategory, metric_list in subcategories.items():
            metrics.update(metric_list)
    return metrics


def main():
    print("=" * 80)
    print("評価指標マスターデータチェック")
    print("=" * 80)
    print()

    # データベースから取得
    db_metrics = get_all_metrics_from_db()
    print(f"📊 データベース内の指標数: {len(db_metrics)}種類")
    print(f"📊 データベース内の総コンペ数: {sum(db_metrics.values())}件")
    print()

    # マスターデータから取得
    master_metrics = get_all_metrics_from_master()
    print(f"📋 METRIC_GROUPS内の指標数: {len(master_metrics)}種類")
    print()

    # 差分チェック
    missing_metrics = set(db_metrics.keys()) - master_metrics
    extra_metrics = master_metrics - set(db_metrics.keys())

    if missing_metrics:
        print("⚠️  未分類の評価指標が見つかりました:")
        print("-" * 80)
        for metric in sorted(missing_metrics):
            count = db_metrics[metric]
            print(f"  - {metric:50s} ({count}件)")
        print()
        print(f"合計 {len(missing_metrics)} 種類の未分類指標があります。")
        print()
        print("👉 対応方法:")
        print("   1. 03_frontend/app/page.tsx の METRIC_GROUPS に追加")
        print("   2. このスクリプト (04_scripts/check_missing_metrics.py) の METRIC_GROUPS も同期")
        print()
    else:
        print("✅ すべての評価指標が分類されています！")
        print()

    if extra_metrics:
        print("ℹ️  データベースに存在しない指標がマスターに定義されています:")
        print("-" * 80)
        for metric in sorted(extra_metrics):
            print(f"  - {metric}")
        print()
        print(f"合計 {len(extra_metrics)} 種類")
        print("（将来的に使用される可能性があるため、削除は不要です）")
        print()

    # サマリー
    print("=" * 80)
    print("サマリー")
    print("=" * 80)
    print(f"データベース内の指標: {len(db_metrics)}種類")
    print(f"マスターデータの指標: {len(master_metrics)}種類")
    print(f"未分類の指標:         {len(missing_metrics)}種類")
    print(f"余剰の指標:           {len(extra_metrics)}種類")
    print("=" * 80)

    # 終了コード
    if missing_metrics:
        sys.exit(1)  # 未分類指標がある場合はエラーコードで終了
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
