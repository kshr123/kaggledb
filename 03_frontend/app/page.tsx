'use client'

import { useState } from 'react'
import useSWR from 'swr'
import { fetcher, buildApiUrl } from '@/lib/api'
import type { CompetitionListResponse } from '@/types/competition'
import type { TagsByCategory } from '@/types/tag'

export default function Home() {
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<string>('all')
  const [page, setPage] = useState(1)
  const [selectedTags, setSelectedTags] = useState<Record<string, string[]>>({})

  // Fetch tags grouped by category
  const { data: tagsData } = useSWR<TagsByCategory>(
    buildApiUrl('/api/tags', { group_by_category: true }),
    fetcher
  )

  // Fetch competitions
  const { data: competitionsData, error, isLoading } = useSWR<CompetitionListResponse>(
    buildApiUrl('/api/competitions', {
      page,
      limit: 20,
      ...(status !== 'all' && { status }),
      ...(search && { search }),
    }),
    fetcher
  )

  const handleTagToggle = (category: string, tagName: string) => {
    setSelectedTags((prev) => {
      const categoryTags = prev[category] || []
      const newCategoryTags = categoryTags.includes(tagName)
        ? categoryTags.filter((t) => t !== tagName)
        : [...categoryTags, tagName]

      return {
        ...prev,
        [category]: newCategoryTags,
      }
    })
    setPage(1) // Reset to first page when filtering
  }

  const clearAllFilters = () => {
    setSelectedTags({})
    setSearch('')
    setStatus('all')
    setPage(1)
  }

  return (
    <div className="flex gap-8">
      {/* Sidebar - Tag Filters */}
      <aside className="w-64 shrink-0">
        <div className="bg-white rounded-lg shadow p-4 sticky top-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">フィルター</h2>
            <button
              onClick={clearAllFilters}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              クリア
            </button>
          </div>

          {/* Search */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              検索
            </label>
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
              placeholder="コンペ名で検索..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Status Filter */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ステータス
            </label>
            <select
              value={status}
              onChange={(e) => {
                setStatus(e.target.value)
                setPage(1)
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">すべて</option>
              <option value="active">開催中</option>
              <option value="completed">終了済み</option>
            </select>
          </div>

          {/* Tag Categories */}
          {tagsData && Object.entries(tagsData).map(([category, tags]) => (
            <div key={category} className="mb-4">
              <h3 className="text-sm font-medium text-gray-700 mb-2">
                {getCategoryLabel(category)}
                {selectedTags[category]?.length > 0 && (
                  <span className="ml-2 text-xs text-blue-600">
                    ({selectedTags[category].length})
                  </span>
                )}
              </h3>
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {tags.map((tag) => (
                  <label
                    key={tag.id}
                    className="flex items-center cursor-pointer hover:bg-gray-50 px-2 py-1 rounded"
                  >
                    <input
                      type="checkbox"
                      checked={selectedTags[category]?.includes(tag.name) || false}
                      onChange={() => handleTagToggle(category, tag.name)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">{tag.name}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Content - Competition List */}
      <div className="flex-1">
        <div className="bg-white rounded-lg shadow">
          {/* Header */}
          <div className="px-6 py-4 border-b">
            <h2 className="text-xl font-semibold">コンペティション一覧</h2>
            {competitionsData && (
              <p className="text-sm text-gray-600 mt-1">
                全 {competitionsData.total} 件
              </p>
            )}
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="px-6 py-12 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">読み込み中...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="px-6 py-12 text-center">
              <p className="text-red-600">データの取得に失敗しました</p>
            </div>
          )}

          {/* Competition List */}
          {competitionsData && competitionsData.items.length > 0 && (
            <>
              <div className="divide-y">
                {competitionsData.items.map((competition) => (
                  <div key={competition.id} className="px-6 py-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-medium text-gray-900 mb-1">
                          {competition.title}
                        </h3>
                        <p className="text-sm text-gray-600 mb-2">
                          {competition.summary}
                        </p>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span className="flex items-center gap-1">
                            <StatusBadge status={competition.status} />
                          </span>
                          <span>📊 {competition.metric}</span>
                          <span>🏷️ {competition.domain}</span>
                          <span>📅 {new Date(competition.end_date).toLocaleDateString('ja-JP')}</span>
                        </div>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {competition.tags.map((tag, idx) => (
                            <span
                              key={idx}
                              className="inline-block px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                      <a
                        href={competition.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-4 px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 border border-blue-600 rounded-md hover:bg-blue-50"
                      >
                        Kaggle で見る →
                      </a>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {competitionsData.total_pages > 1 && (
                <div className="px-6 py-4 border-t flex items-center justify-between">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    ← 前へ
                  </button>
                  <span className="text-sm text-gray-600">
                    ページ {page} / {competitionsData.total_pages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(competitionsData.total_pages, p + 1))}
                    disabled={page === competitionsData.total_pages}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    次へ →
                  </button>
                </div>
              )}
            </>
          )}

          {/* Empty State */}
          {competitionsData && competitionsData.items.length === 0 && (
            <div className="px-6 py-12 text-center">
              <p className="text-gray-600">条件に一致するコンペがありません</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Helper component for status badge
function StatusBadge({ status }: { status: string }) {
  if (status === 'active') {
    return <span className="text-green-600 font-medium">🟢 開催中</span>
  }
  return <span className="text-gray-600">🔴 終了済み</span>
}

// Helper function to get category label in Japanese
function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    data_type: 'データ種別',
    task_type: 'タスク種別',
    model_type: 'モデル種別',
    solution_method: '解法種別',
    competition_feature: 'コンペ特徴',
    domain: 'ドメイン',
  }
  return labels[category] || category
}
