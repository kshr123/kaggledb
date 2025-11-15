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

export interface Competition {
  id: string;
  title: string;
  url: string;
  start_date: string;
  end_date: string;
  status: 'active' | 'completed';
  metric: string;
  description?: string;
  summary: string; // JSON文字列（StructuredSummaryをパースする）
  tags: string[];
  data_types: string[];
  domain: string;
  discussion_count: number;
  solution_status: '未着手' | 'ディスカッションのみ' | '解法分析済み';
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
