/**
 * コンペティション関連の型定義
 */

/**
 * 評価指標の型
 */
export interface EvaluationMetric {
  metric: string;
  explanation: string;
  why_important: string;
}

/**
 * 構造化要約の型
 */
export interface StructuredSummary {
  overview: string;
  objective: string;
  data: string;
  evaluation: EvaluationMetric;
  business_value: string;
  key_challenges: string[];
}

/**
 * データセットのカラム情報
 */
export interface DatasetColumn {
  name: string;
  description: string;
}

/**
 * データセット情報の型
 */
export interface DatasetInfo {
  files: string[];
  total_size: string;
  description: string;
  features: string[];
  columns: DatasetColumn[];
}

export interface Competition {
  id: string;
  title: string;
  url: string;
  start_date: string | null;
  end_date: string | null;
  status: 'active' | 'completed';
  metric: string | null;
  metric_description?: string | null;
  description?: string;
  summary: string | null; // 日本語要約テキスト
  tags: string[]; // JSON配列
  data_types: string[]; // JSON配列
  competition_features: string[]; // JSON配列
  task_types: string[]; // JSON配列
  domain: string | null;
  dataset_info?: string | null;
  discussion_count: number;
  solution_status: '未着手' | 'ディスカッションのみ' | '解法分析済み';
  is_favorite: boolean;
  days_until_deadline?: number | null; // 終了日までの日数（開催中のみ）
  created_at: string;
}

export interface CompetitionListResponse {
  items: Competition[];
  total: number;
  active_count: number;
  completed_count: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface CompetitionQueryParams {
  page?: number;
  limit?: number;
  status?: string;
  search?: string;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

/**
 * ディスカッション情報の型
 */
export interface Discussion {
  id: number;
  competition_id: string;
  title: string;
  author: string | null;
  author_tier: string | null;
  tier_color: string | null;
  url: string;
  vote_count: number;
  comment_count: number;
  view_count: number;
  kaggle_created_at: string | null;
  category: string | null;
  is_pinned: boolean;
  content: string | null;
  summary: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * 解法情報の型
 */
export interface Solution {
  id: number;
  competition_id: string;
  title: string;
  author: string | null;
  author_tier: string | null;
  tier_color: string | null;
  url: string;
  type: 'notebook' | 'discussion';
  medal: 'gold' | 'silver' | 'bronze' | null;
  rank: number | null;
  vote_count: number;
  comment_count: number;
  content: string | null;
  summary: string | null;
  techniques: string | null;
  created_at: string;
  updated_at: string;
}
