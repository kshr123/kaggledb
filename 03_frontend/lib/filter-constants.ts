/**
 * フィルター用のマスターデータ定義
 */

/**
 * 評価指標の階層構造（3階層）
 */
export const METRIC_GROUPS = {
  分類: {
    'AUC系': ['ROC AUC', 'PR-AUC', 'AUC', 'pAUC'],
    'F-Score系': [
      'F1',
      'Macro F1',
      'Micro F1',
      'F2',
      'F-beta',
      'Micro F-beta',
      'F0.5',
      'pF1',
    ],
    'Log Loss系': ['Log Loss', 'Weighted Log Loss', 'GLL'],
    'Accuracy系': [
      'Accuracy',
      'Weighted Accuracy',
      'MAA',
      'mAA',
      'Balanced Accuracy',
    ],
    その他分類指標: [
      'Dice',
      'Quadratic Weighted Kappa',
      'Matthews Correlation Coefficient',
      'Cohen Kappa Score',
      'IoU',
      'Surface Dice',
      'Surface Dice, TopoScore, VOI',
      'Jaccard score',
      'word-level Jaccard score',
      'Brier score',
      'Average Brier Bracket Score',
    ],
  },
  回帰: {
    'RMSE系': ['RMSE', 'RMSPE', 'RMSLE', 'RMSSE', 'MCRMSE', 'MRRMSE'],
    'MAE系': ['MAE', 'Weighted MAE', 'Mean Angular Error', 'MCMAE'],
    相関系: [
      'Pearson Correlation',
      'Spearman Correlation',
      'Kendall Tau Correlation',
      'Mean Pearson',
    ],
    その他回帰指標: [
      'R²',
      'Mean Cosine Similarity',
      'SMAPE',
      'Normalized Gini Coefficient',
      'Sharpened Cosine Similarity',
    ],
  },
  'ランキング・レコメンド': {
    'MAP系': [
      'MAP',
      'MAP@3',
      'MAP@5',
      'MAP@12',
      'MAP@25',
      'MAP@50',
      'MAP@100',
      'mean Average Precision @ 100',
    ],
    その他ランキング指標: [
      'Padded cMAP',
      'Average Precision',
      'Global Average Precision',
      'mean Precision @ 5',
      'Weighted Label Ranking Average Precision',
      'Recall@20',
      'top-3 error rate',
    ],
  },
  その他: {
    '距離・誤差': [
      'mean position error',
      'mean distance error',
      'distance error',
      'normalized total levenshtein distance',
      'Levenshtein Mean',
      'Word Error Rate',
    ],
    '確率・統計': [
      'Perplexity',
      'Negative Log-Likelihood',
      'Laplace Log Likelihood',
      'Kullback Leibler divergence',
      'Continuous Ranked Probability Score',
      'Weighted Scaled Pinball Loss',
      'Stratified Concordance Index',
    ],
    '画像・構造評価': ['TM-score', 'MiFID', 'SVG Image Fidelity Score', 'SNR'],
    'ゲーム・シミュレーション': ['utility score', 'penalty cost', 'moves'],
    カスタム: ['Custom', 'Skill Rating', 'Sharpe Ratio'],
  },
} as const

/**
 * データタイプの定義（英語値と日本語表示）
 */
export const DATA_TYPES = [
  { value: 'Tabular', label: 'テーブル' },
  { value: 'Image', label: '画像' },
  { value: 'Text', label: 'テキスト' },
  { value: 'Time Series', label: '時系列' },
  { value: 'Audio', label: '音声' },
  { value: 'Video', label: '動画' },
  { value: '3D', label: '3D' },
  { value: 'Graph', label: 'グラフ' },
  { value: 'Geospatial', label: '地理空間' },
  { value: 'Code', label: 'コード' },
  { value: 'Structured', label: '構造化' },
  { value: 'Unstructured', label: '非構造化' },
  { value: 'Mixed', label: '混合' },
]

/**
 * 並び替え項目の定義
 */
export const SORT_OPTIONS = [
  { value: 'created_at', label: '新着順（開始日）', order: 'desc' as const },
  { value: 'deadline', label: '終了日が近い順', order: 'asc' as const },
  { value: 'created_at_asc', label: '開始日が古い順', order: 'asc' as const },
]

/**
 * 型定義
 */
export type MetricCategory = keyof typeof METRIC_GROUPS
export type MetricSubCategory<T extends MetricCategory> = keyof typeof METRIC_GROUPS[T]
export type MetricName = string

export type DataType = string
export type SortValue = 'created_at' | 'deadline' | 'created_at_asc'
export type SortOrder = 'asc' | 'desc'
