#!/usr/bin/env python3
"""
評価指標の表記揺れを統一するスクリプト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from app.config import DATABASE_PATH

# 評価指標の正規化マッピング（略称優先）
METRIC_NORMALIZATION = {
    # Log Loss
    'LogLoss': 'Log Loss',
    'log loss': 'Log Loss',
    'weighted log loss': 'Weighted Log Loss',
    'sample weighted log loss': 'Weighted Log Loss',
    'Weighted Mean Columnwise Log Loss': 'Weighted Log Loss',

    # F1
    'F1-score': 'F1',
    'F1-Score': 'F1',
    'F1 score': 'F1',
    'F1-measure': 'F1',
    'F-measure': 'F1',
    'F-Score': 'F1',
    'macro F1': 'Macro F1',
    'macro F1 score': 'Macro F1',
    'micro F1': 'Micro F1',
    'micro F1 score': 'Micro F1',
    'micro Fβ': 'Micro F-beta',

    # F2
    'F2 Score': 'F2',

    # F-beta
    'Fβ-score': 'F-beta',
    'FBeta': 'F-beta',

    # MAP (Mean Average Precision)
    'mAP': 'MAP',
    'mean average precision': 'MAP',
    'Mean Average Precision': 'MAP',
    'mean Average Precision': 'MAP',
    'mAP@50': 'MAP@50',
    'mAP@100': 'MAP@100',
    'MAP@25': 'MAP@25',
    'MAP@12': 'MAP@12',

    # MAE
    'Mean Absolute Error': 'MAE',
    'Weighted Mean Absolute Error': 'Weighted MAE',
    'wMAE': 'Weighted MAE',
    'MeanAngularError': 'Mean Angular Error',

    # RMSE系（そのまま）
    # RMSE, RMSPE, RMSLE, RMSSE, MCRMSE は略称なのでそのまま

    # Dice
    'Dice coefficient': 'Dice',

    # AUC/ROC
    # 注意: ROC-AUC と AUC は分けて管理（PR-AUC, pAUC なども存在するため）
    'ROC-AUC': 'ROC AUC',

    # Accuracy
    'Categorization Accuracy': 'Accuracy',
    'weighted accuracy': 'Weighted Accuracy',
    'Weighted Categorization Accuracy': 'Weighted Accuracy',
    'mean Average Accuracy': 'MAA',
    'mean Average Accuracy (mAA)': 'MAA',

    # Sharpe Ratio
    'Sharpe ratio': 'Sharpe Ratio',

    # Custom
    'custom': 'Custom',
    'Custom Metric': 'Custom',

    # Skill Rating
    'skill rating': 'Skill Rating',

    # Correlation
    'Pearson correlation coefficient': 'Pearson Correlation',
    "Spearman's correlation": 'Spearman Correlation',
    "Spearman's correlation coefficient": 'Spearman Correlation',

    # R²
    'R^2': 'R²',
    'R2 Score': 'R²',

    # Kappa
    'quadratic weighted kappa': 'Quadratic Weighted Kappa',
    'QuadraticWeightedKappa': 'Quadratic Weighted Kappa',

    # その他の統一
    'padded cmAP': 'Padded cMAP',
    'MeanCosineSimilarity': 'Mean Cosine Similarity',
    '平均精度': 'Average Precision',
}


def normalize_metrics(dry_run=True):
    """評価指標を正規化"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    print("=" * 60)
    print("評価指標の正規化")
    print("=" * 60)

    updates = []

    for old_metric, new_metric in METRIC_NORMALIZATION.items():
        cursor.execute(
            "SELECT id, title, metric FROM competitions WHERE metric = ?",
            (old_metric,)
        )
        results = cursor.fetchall()

        if results:
            print(f"\n'{old_metric}' → '{new_metric}': {len(results)}件")
            for comp_id, title, metric in results:
                print(f"  - {comp_id}: {title}")
                updates.append((new_metric, comp_id))

    print("\n" + "=" * 60)
    print(f"合計: {len(updates)}件を更新")
    print("=" * 60)

    if not dry_run:
        print("\n更新を実行中...")
        for new_metric, comp_id in updates:
            cursor.execute(
                "UPDATE competitions SET metric = ? WHERE id = ?",
                (new_metric, comp_id)
            )

        conn.commit()
        print("✅ 更新完了")
    else:
        print("\n⚠️  ドライラン（実際には更新されません）")
        print("実際に更新する場合は --apply オプションを付けてください")

    conn.close()

    return len(updates)


def show_current_metrics():
    """現在の評価指標の分布を表示"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT metric, COUNT(*) as count
        FROM competitions
        WHERE metric IS NOT NULL AND metric != ''
        GROUP BY metric
        ORDER BY count DESC
        LIMIT 30
    """)

    print("\n現在の評価指標 TOP 30:")
    print("-" * 60)
    for metric, count in cursor.fetchall():
        print(f"{metric:40s} : {count:3d}件")

    conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='評価指標の表記揺れを統一')
    parser.add_argument('--apply', action='store_true', help='実際に更新を実行')
    parser.add_argument('--show', action='store_true', help='現在の分布を表示')

    args = parser.parse_args()

    if args.show:
        show_current_metrics()
    else:
        count = normalize_metrics(dry_run=not args.apply)

        if args.apply:
            print("\n更新後の分布:")
            show_current_metrics()
