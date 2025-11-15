'use client'

import { useState } from 'react'
import useSWR from 'swr'
import { fetcher, buildApiUrl } from '@/lib/api'
import type { CompetitionListResponse, StructuredSummary } from '@/types/competition'
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
    <div className="min-h-screen bg-slate-100">
      {/* Header Stats Bar */}
      <div className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-[1800px] mx-auto px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Kaggle Competition Database</h1>
              <p className="text-sm text-slate-600 mt-0.5">コンペティション分析ダッシュボード</p>
            </div>
            {competitionsData && (
              <div className="flex items-center gap-6">
                <div className="text-center px-4 py-2 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="text-2xl font-bold text-slate-900">{competitionsData.total}</div>
                  <div className="text-xs text-slate-600 font-medium">総コンペ数</div>
                </div>
                <div className="text-center px-4 py-2 bg-emerald-50 rounded-lg border border-emerald-200">
                  <div className="text-2xl font-bold text-emerald-700">
                    {competitionsData.items.filter(c => c.status === 'active').length}
                  </div>
                  <div className="text-xs text-emerald-700 font-medium">開催中</div>
                </div>
                <div className="text-center px-4 py-2 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="text-2xl font-bold text-slate-700">
                    {competitionsData.items.filter(c => c.status === 'completed').length}
                  </div>
                  <div className="text-xs text-slate-600 font-medium">終了済み</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="flex gap-6 max-w-[1800px] mx-auto px-8 py-6">
        {/* Sidebar - Tag Filters */}
        <aside className="w-72 shrink-0">
          <div className="bg-white rounded-xl shadow-md p-6 sticky top-6 border border-slate-200">
            <div className="flex items-center justify-between mb-5 pb-3 border-b border-slate-200">
              <div className="flex items-center gap-2">
                <div className="w-1 h-5 bg-blue-600 rounded-full"></div>
                <h2 className="text-base font-bold text-slate-900">絞り込み</h2>
              </div>
              <button
                onClick={clearAllFilters}
                className="px-3 py-1 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
              >
                リセット
              </button>
            </div>

          {/* Search */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-slate-700 mb-2.5">
              🔍 検索
            </label>
            <div className="relative">
              <input
                type="text"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value)
                  setPage(1)
                }}
                placeholder="コンペ名で検索..."
                className="w-full pl-4 pr-4 py-2.5 text-sm border-2 border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all placeholder:text-slate-400 bg-slate-50 hover:bg-white"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-slate-700 mb-2.5">
              📊 ステータス
            </label>
            <select
              value={status}
              onChange={(e) => {
                setStatus(e.target.value)
                setPage(1)
              }}
              className="w-full px-4 py-2.5 text-sm border-2 border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all bg-slate-50 hover:bg-white cursor-pointer font-medium"
            >
              <option value="all">すべて</option>
              <option value="active">🟢 開催中</option>
              <option value="completed">🔴 終了済み</option>
            </select>
          </div>

          {/* Tag Categories */}
          {tagsData && Object.entries(tagsData).map(([category, tags]) => (
            <div key={category} className="mb-6">
              <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center justify-between">
                <span>{getCategoryLabel(category)}</span>
                {selectedTags[category]?.length > 0 && (
                  <span className="px-2 py-0.5 text-xs font-bold bg-blue-600 text-white rounded-full">
                    {selectedTags[category].length}
                  </span>
                )}
              </h3>
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {tags.map((tag) => (
                  <label
                    key={tag.id}
                    className="flex items-center cursor-pointer hover:bg-blue-50 px-3 py-2 rounded-lg transition-colors group"
                  >
                    <input
                      type="checkbox"
                      checked={selectedTags[category]?.includes(tag.name) || false}
                      onChange={() => handleTagToggle(category, tag.name)}
                      className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-2 focus:ring-blue-500"
                    />
                    <span className="ml-3 text-sm text-slate-700 group-hover:text-slate-900 font-medium">{tag.name}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Content - Competition List */}
      <div className="flex-1">
        <div className="bg-white rounded-xl shadow-md border border-slate-200">
          {/* Header */}
          <div className="px-8 py-6 border-b-2 border-slate-200 bg-gradient-to-r from-slate-50 to-white">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-slate-900 flex items-center gap-3">
                  <div className="w-1.5 h-6 bg-blue-600 rounded-full"></div>
                  コンペティション一覧
                </h2>
                {competitionsData && (
                  <p className="text-sm text-slate-600 mt-2 ml-6">
                    全 <span className="text-blue-600 font-bold">{competitionsData.total}</span> 件中 <span className="font-semibold">{competitionsData.items.length}</span> 件を表示
                  </p>
                )}
              </div>
            </div>
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
              <div className="divide-y-2 divide-slate-100">
                {competitionsData.items.map((competition) => (
                  <div key={competition.id} className="px-8 py-6 hover:bg-slate-50/50 transition-all group relative">
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-blue-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <div className="flex items-start justify-between gap-8">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-bold text-slate-900 mb-4 group-hover:text-blue-700 transition-colors">
                          {competition.title}
                        </h3>

                        {/* 最優先情報: 評価指標とタスクタイプ */}
                        <div className="flex flex-wrap items-center gap-2.5 mb-4">
                          <StatusBadge status={competition.status} />
                          {competition.metric && isDisplayableMetric(competition.metric) && (
                            <span className="inline-flex items-center gap-2 px-4 py-1.5 text-xs font-bold bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg shadow-sm">
                              📊 {competition.metric}
                            </span>
                          )}
                          {competition.tags.filter(tag =>
                            tag.includes('分類') || tag.includes('回帰') || tag.includes('物体検出') ||
                            tag.includes('セグメンテーション') || tag.includes('生成') || tag.includes('ランキング')
                          ).map((tag, idx) => (
                            <span
                              key={idx}
                              className="inline-flex items-center gap-2 px-4 py-1.5 text-xs font-bold bg-gradient-to-r from-emerald-500 to-green-600 text-white rounded-lg shadow-sm"
                            >
                              🎯 {tag}
                            </span>
                          ))}
                        </div>

                        {/* 構造化要約 */}
                        <StructuredSummaryDisplay summary={competition.summary} />

                        {/* 補助情報 */}
                        <div className="flex items-center gap-5 text-sm text-slate-600 mb-4 font-medium">
                          <span className="flex items-center gap-1.5">
                            <span className="text-blue-600">🏷️</span>
                            {competition.domain}
                          </span>
                          <span className="flex items-center gap-1.5">
                            <span className="text-blue-600">📅</span>
                            {new Date(competition.end_date).toLocaleDateString('ja-JP')}
                          </span>
                        </div>

                        {/* その他のタグ（タスクタイプ以外） */}
                        <div className="flex flex-wrap gap-2">
                          {competition.tags.filter(tag =>
                            !tag.includes('分類') && !tag.includes('回帰') && !tag.includes('物体検出') &&
                            !tag.includes('セグメンテーション') && !tag.includes('生成') && !tag.includes('ランキング')
                          ).map((tag, idx) => (
                            <span
                              key={idx}
                              className="inline-block px-3 py-1 text-xs font-semibold bg-slate-100 text-slate-700 rounded-md border border-slate-200 hover:bg-slate-200 hover:border-slate-300 transition-all"
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
                        className="shrink-0 px-6 py-3 text-sm font-bold text-white bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 rounded-lg shadow-md hover:shadow-lg transition-all flex items-center gap-2 group"
                      >
                        <span>Kaggle で見る</span>
                        <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </a>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {competitionsData.total_pages > 1 && (
                <div className="px-8 py-5 border-t-2 border-slate-200 bg-slate-50 flex items-center justify-between rounded-b-xl">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-5 py-2.5 text-sm font-semibold text-slate-700 bg-white border-2 border-slate-300 rounded-lg hover:bg-slate-50 hover:border-blue-400 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-white disabled:hover:border-slate-300 transition-all flex items-center gap-2 shadow-sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    <span>前へ</span>
                  </button>
                  <span className="text-sm text-slate-700 font-medium">
                    ページ <span className="px-3 py-1 bg-blue-600 text-white font-bold rounded-md">{page}</span> / {competitionsData.total_pages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(competitionsData.total_pages, p + 1))}
                    disabled={page === competitionsData.total_pages}
                    className="px-5 py-2.5 text-sm font-semibold text-slate-700 bg-white border-2 border-slate-300 rounded-lg hover:bg-slate-50 hover:border-blue-400 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-white disabled:hover:border-slate-300 transition-all flex items-center gap-2 shadow-sm"
                  >
                    <span>次へ</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
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
    </div>
  )
}

// Helper component for structured summary display
function StructuredSummaryDisplay({ summary }: { summary: string }) {
  try {
    const parsed: StructuredSummary = JSON.parse(summary)

    return (
      <div className="text-sm text-gray-700 mb-3 space-y-2">
        {/* Overview */}
        <p className="text-gray-800">{parsed.overview}</p>

        {/* Details */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="font-medium text-gray-600">予測対象:</span>{' '}
            <span className="text-gray-800">{parsed.objective}</span>
          </div>
          <div>
            <span className="font-medium text-gray-600">データ:</span>{' '}
            <span className="text-gray-800">{parsed.data}</span>
          </div>
        </div>

        <div className="text-xs">
          <span className="font-medium text-gray-600">価値:</span>{' '}
          <span className="text-gray-800">{parsed.business_value}</span>
        </div>

        {/* Key Challenges */}
        {parsed.key_challenges && parsed.key_challenges.length > 0 && (
          <div className="text-xs">
            <span className="font-medium text-gray-600">主な課題:</span>
            <ul className="ml-4 mt-1 list-disc text-gray-700">
              {parsed.key_challenges.map((challenge, idx) => (
                <li key={idx}>{challenge}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    )
  } catch {
    // JSON parsing failed, display as plain text
    return <p className="text-sm text-gray-600 mb-2">{summary}</p>
  }
}

// Helper component for status badge
function StatusBadge({ status }: { status: string }) {
  if (status === 'active') {
    return (
      <span className="inline-flex items-center gap-2 px-4 py-1.5 text-xs font-bold bg-gradient-to-r from-emerald-100 to-green-100 text-emerald-800 rounded-lg border-2 border-emerald-300 shadow-sm">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
        </span>
        開催中
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-2 px-4 py-1.5 text-xs font-bold bg-slate-100 text-slate-600 rounded-lg border-2 border-slate-300">
      <span className="w-2 h-2 bg-slate-400 rounded-full"></span>
      終了済み
    </span>
  )
}

// Helper function to determine if metric should be displayed
// 内部コード名（アンダースコア+スペースなし）はユーザーに表示しない
function isDisplayableMetric(metric: string): boolean {
  if (!metric) return false

  const hasSpace = / /.test(metric)
  const hasUnderscore = /_/.test(metric)

  // アンダースコアを含み、スペースがない場合は内部コード名
  // 例: "nfl_2025", "cafa6_metric_final", "NFL_2025"
  if (hasUnderscore && !hasSpace) {
    return false
  }

  return true
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
