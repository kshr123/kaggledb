/**
 * API クライアント
 * バックエンドAPIとの通信を担当
 */

import type {
  Competition,
  CompetitionListResponse,
  CompetitionQueryParams,
} from '@/types/competition';
import type { Tag, TagsByCategory } from '@/types/tag';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Generic fetcher for SWR
export const fetcher = async (url: string) => {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error('API request failed');
  }

  return response.json();
};

/**
 * コンペティション一覧を取得
 */
export async function getCompetitions(
  params: CompetitionQueryParams = {}
): Promise<CompetitionListResponse> {
  const queryParams = new URLSearchParams();

  if (params.page) queryParams.append('page', params.page.toString());
  if (params.limit) queryParams.append('limit', params.limit.toString());
  if (params.status) queryParams.append('status', params.status);
  if (params.search) queryParams.append('search', params.search);
  if (params.sort_by) queryParams.append('sort_by', params.sort_by);
  if (params.order) queryParams.append('order', params.order);

  const url = `${API_URL}/api/competitions?${queryParams.toString()}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error('Failed to fetch competitions');
  }

  return response.json();
}

/**
 * コンペティション詳細を取得
 */
export async function getCompetitionById(id: string): Promise<Competition> {
  const response = await fetch(`${API_URL}/api/competitions/${id}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Competition not found');
    }
    throw new Error('Failed to fetch competition');
  }

  return response.json();
}

/**
 * 新規コンペティションを取得
 */
export async function getNewCompetitions(
  days: number = 30,
  limit?: number
): Promise<Competition[]> {
  const queryParams = new URLSearchParams({ days: days.toString() });
  if (limit) queryParams.append('limit', limit.toString());

  const url = `${API_URL}/api/competitions/new?${queryParams.toString()}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error('Failed to fetch new competitions');
  }

  return response.json();
}

/**
 * タグ一覧を取得
 */
export async function getTags(
  category?: string,
  groupByCategory: boolean = false
): Promise<Tag[] | TagsByCategory> {
  const queryParams = new URLSearchParams();
  if (category) queryParams.append('category', category);
  if (groupByCategory) queryParams.append('group_by_category', 'true');

  const url = `${API_URL}/api/tags?${queryParams.toString()}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error('Failed to fetch tags');
  }

  return response.json();
}

/**
 * SWR用のAPIエンドポイント構築ヘルパー
 */
export function buildApiUrl(
  endpoint: string,
  params?: Record<string, string | number | boolean | undefined>
): string {
  if (!params) return `${API_URL}${endpoint}`;

  const queryParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      queryParams.append(key, value.toString());
    }
  });

  const queryString = queryParams.toString();
  return queryString ? `${API_URL}${endpoint}?${queryString}` : `${API_URL}${endpoint}`;
}
