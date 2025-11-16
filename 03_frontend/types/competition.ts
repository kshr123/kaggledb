/**
 * コンペティション関連の型定義
 */

/**
 * 構造化要約の型
 */
export interface StructuredSummary {
  overview: string;
  objective: string;
  data: string;
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
  start_date: string;
  end_date: string;
  status: 'active' | 'completed';
  metric: string;
  metric_description?: string;
  description?: string;
  summary: string; // JSON文字列（StructuredSummaryをパースする）
  tags: string[];
  data_types: string[];
  domain: string;
  dataset_info?: string; // JSON文字列（DatasetInfoをパースする）
  discussion_count: number;
  solution_status: '未着手' | 'ディスカッションのみ' | '解法分析済み';
  is_favorite: boolean;
  created_at: string;
  updated_at: string;
}

export interface CompetitionListResponse {
  items: Competition[];
  total: number;
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
