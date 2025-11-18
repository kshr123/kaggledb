'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import useSWR from 'swr'
import { fetcher, buildApiUrl } from '@/lib/api'
import type { CompetitionListResponse, StructuredSummary, DatasetInfo } from '@/types/competition'
import type { TagsByCategory } from '@/types/tag'
import { METRIC_GROUPS, DATA_TYPES, SORT_OPTIONS } from '@/lib/filter-constants'
import type { MetricCategory, MetricSubCategory } from '@/lib/filter-constants'

export default function Home() {
  const router = useRouter()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<string>('all')
  const [page, setPage] = useState(1)
  const [selectedTags, setSelectedTags] = useState<Record<string, string[]>>({})

  // 新しいフィルター状態
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([])
  const [selectedDataTypes, setSelectedDataTypes] = useState<string[]>([])
  const [isFavorite, setIsFavorite] = useState<boolean | null>(null)
  const [sortBy, setSortBy] = useState('created_at')
  const [order, setOrder] = useState<'asc' | 'desc'>('desc')

  // 展開状態の管理
  const [expandedMetricCategories, setExpandedMetricCategories] = useState<Set<string>>(new Set())
  const [expandedMetricSubCategories, setExpandedMetricSubCategories] = useState<Set<string>>(new Set())

  // Fetch tags grouped by category
  const { data: tagsData } = useSWR<TagsByCategory>(
    buildApiUrl('/api/tags', { group_by_category: true }),
    fetcher
  )

  // Fetch total statistics (without filters)
  const { data: totalStatsData } = useSWR<CompetitionListResponse>(
    buildApiUrl('/api/competitions', { limit: 1 }),
    fetcher
  )

  // Fetch competitions with all filters
  const { data: competitionsData, error, isLoading } = useSWR<CompetitionListResponse>(
    buildApiUrl('/api/competitions', {
      page,
      limit: 20,
      ...(status !== 'all' && { status }),
      ...(search && { search }),
      ...(selectedMetrics.length > 0 && { metrics: selectedMetrics }),
      ...(selectedDataTypes.length > 0 && { data_types: selectedDataTypes }),
      ...(isFavorite !== null && { is_favorite: isFavorite }),
      sort_by: sortBy,
      order,
    }),
    fetcher
  )

  // タグフィルターのトグル
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
    setPage(1)
  }

  // 評価指標フィルターのトグル
  const handleMetricToggle = (metricName: string) => {
    setSelectedMetrics((prev) =>
      prev.includes(metricName)
        ? prev.filter((m) => m !== metricName)
        : [...prev, metricName]
    )
    setPage(1)
  }

  // カテゴリ内の全指標を取得
  const getAllMetricsInCategory = (category: string): string[] => {
    const subCategories = METRIC_GROUPS[category as MetricCategory]
    const allMetrics: string[] = []
    Object.values(subCategories).forEach((metrics) => {
      allMetrics.push(...metrics)
    })
    return allMetrics
  }

  // サブカテゴリ内の全指標を取得
  const getAllMetricsInSubCategory = (category: string, subCategory: string): string[] => {
    return METRIC_GROUPS[category as MetricCategory][subCategory as any] || []
  }

  // カテゴリ全選択のトグル
  const handleCategorySelectAll = (category: string) => {
    const allMetrics = getAllMetricsInCategory(category)
    const allSelected = allMetrics.every((m) => selectedMetrics.includes(m))

    if (allSelected) {
      // 全て選択されている場合は解除
      setSelectedMetrics((prev) => prev.filter((m) => !allMetrics.includes(m)))
    } else {
      // 一部または全て未選択の場合は全選択
      setSelectedMetrics((prev) => {
        const newMetrics = [...prev]
        allMetrics.forEach((m) => {
          if (!newMetrics.includes(m)) {
            newMetrics.push(m)
          }
        })
        return newMetrics
      })
    }
    setPage(1)
  }

  // サブカテゴリ全選択のトグル
  const handleSubCategorySelectAll = (category: string, subCategory: string) => {
    const allMetrics = getAllMetricsInSubCategory(category, subCategory)
    const allSelected = allMetrics.every((m) => selectedMetrics.includes(m))

    if (allSelected) {
      setSelectedMetrics((prev) => prev.filter((m) => !allMetrics.includes(m)))
    } else {
      setSelectedMetrics((prev) => {
        const newMetrics = [...prev]
        allMetrics.forEach((m) => {
          if (!newMetrics.includes(m)) {
            newMetrics.push(m)
          }
        })
        return newMetrics
      })
    }
    setPage(1)
  }

  // データタイプフィルターのトグル
  const handleDataTypeToggle = (dataType: string) => {
    setSelectedDataTypes((prev) =>
      prev.includes(dataType)
        ? prev.filter((d) => d !== dataType)
        : [...prev, dataType]
    )
    setPage(1)
  }

  // カテゴリーの展開/折りたたみ
  const toggleMetricCategory = (category: string) => {
    setExpandedMetricCategories((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(category)) {
        newSet.delete(category)
      } else {
        newSet.add(category)
      }
      return newSet
    })
  }

  // サブカテゴリーの展開/折りたたみ
  const toggleMetricSubCategory = (subCategory: string) => {
    setExpandedMetricSubCategories((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(subCategory)) {
        newSet.delete(subCategory)
      } else {
        newSet.add(subCategory)
      }
      return newSet
    })
  }

  // 並び替えの変更
  const handleSortChange = (value: string) => {
    const option = SORT_OPTIONS.find((opt) => opt.value === value)
    if (option) {
      setSortBy(option.value)
      setOrder(option.order)
      setPage(1)
    }
  }

  // 全てのフィルターをリセット
  const clearAllFilters = () => {
    setSelectedTags({})
    setSelectedMetrics([])
    setSelectedDataTypes([])
    setIsFavorite(null)
    setSearch('')
    setStatus('all')
    setSortBy('created_at')
    setOrder('desc')
    setPage(1)
  }

  // 個別フィルターのリセット
  const clearMetricFilter = () => {
    setSelectedMetrics([])
    setPage(1)
  }

  const clearDataTypeFilter = () => {
    setSelectedDataTypes([])
    setPage(1)
  }

  const clearTagFilter = () => {
    setSelectedTags({})
    setPage(1)
  }

  // ページネーション用のページ番号配列を生成
  const getPageNumbers = () => {
    if (!competitionsData) return []
    const totalPages = competitionsData.total_pages
    const currentPage = page
    const pages: (number | string)[] = []

    // 現在ページの前後5ページを表示
    const startPage = Math.max(1, currentPage - 5)
    const endPage = Math.min(totalPages, currentPage + 5)

    // 先頭ページ
    if (startPage > 1) {
      pages.push(1)
      if (startPage > 2) {
        pages.push('...')
      }
    }

    // 現在ページ周辺
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i)
    }

    // 末尾ページ
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        pages.push('...')
      }
      pages.push(totalPages)
    }

    return pages
  }

  // 全体統計から開催中の数を計算
  const getActiveCount = () => {
    if (!totalStatsData) return 0
    // ここでは簡易的に取得。実際はバックエンドで status=active の count を取得する方が良い
    return totalStatsData.items.filter(c => c.status === 'active').length
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100">
      {/* Header Stats Bar */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-slate-200/60 shadow-sm sticky top-0 z-50">
        <div className="max-w-[1800px] mx-auto px-8 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Kaggle Competition Database</h1>
              <p className="text-sm text-slate-500 mt-1">コンペティション分析ダッシュボード</p>
            </div>
            {totalStatsData && (
              <div className="flex items-center gap-4">
                <div className="text-center px-5 py-2.5 bg-slate-50/50 rounded-xl border border-slate-200/60">
                  <div className="text-xl font-semibold text-slate-900">{totalStatsData.total}</div>
                  <div className="text-xs text-slate-500 font-medium mt-0.5">総コンペ数</div>
                </div>
                <div className="text-center px-5 py-2.5 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl border border-emerald-200/60">
                  <div className="text-xl font-semibold text-emerald-700">
                    {getActiveCount()}
                  </div>
                  <div className="text-xs text-emerald-600 font-medium mt-0.5">開催中</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="flex gap-6 max-w-[1800px] mx-auto px-8 py-6">
        {/* Sidebar - Filters */}
        <aside className="w-72 shrink-0">
          <div className="bg-white rounded-xl shadow-md border border-slate-200 sticky top-24 max-h-[calc(100vh-7rem)] flex flex-col">
            {/* ヘッダー */}
            <div className="flex items-center justify-between px-6 py-5 border-b border-slate-200">
              <div className="flex items-center gap-2">
                <div className="w-1 h-5 bg-blue-600 rounded-full"></div>
                <h2 className="text-base font-bold text-slate-900">絞り込み</h2>
              </div>
              <button
                onClick={clearAllFilters}
                className="px-3 py-1 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
              >
                全てリセット
              </button>
            </div>

            {/* フィルター内容（スクロール可能） */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
              {/* 検索 */}
              <div>
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

              {/* 評価指標フィルター（3階層） */}
              <div>
                <div className="flex items-center justify-between mb-2.5">
                  <label className="block text-sm font-semibold text-slate-700">
                    📊 評価指標
                  </label>
                  {selectedMetrics.length > 0 && (
                    <button
                      onClick={clearMetricFilter}
                      className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                    >
                      リセット
                    </button>
                  )}
                </div>
                {selectedMetrics.length > 0 && (
                  <div className="mb-2 px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded border border-blue-200">
                    {selectedMetrics.length} 件選択中
                  </div>
                )}
                <div className="space-y-1">
                  {Object.entries(METRIC_GROUPS).map(([category, subCategories]) => {
                    const allMetricsInCategory = getAllMetricsInCategory(category)
                    const allSelected = allMetricsInCategory.every((m) => selectedMetrics.includes(m))
                    const someSelected = allMetricsInCategory.some((m) => selectedMetrics.includes(m))

                    return (
                      <div key={category} className="border border-slate-200 rounded-lg overflow-hidden">
                        {/* カテゴリー */}
                        <div className="bg-slate-50">
                          <div className="flex items-center px-3 py-2">
                            <input
                              type="checkbox"
                              checked={allSelected}
                              ref={(el) => {
                                if (el) el.indeterminate = someSelected && !allSelected
                              }}
                              onChange={() => handleCategorySelectAll(category)}
                              className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-2 focus:ring-blue-500"
                            />
                            <button
                              onClick={() => toggleMetricCategory(category)}
                              className="flex-1 flex items-center justify-between ml-2 hover:bg-slate-100 rounded px-2 py-1 transition-colors"
                            >
                              <span className="text-sm font-semibold text-slate-700">{category}</span>
                              <svg
                                className={`w-4 h-4 text-slate-400 transition-transform ${
                                  expandedMetricCategories.has(category) ? 'rotate-180' : ''
                                }`}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                              </svg>
                            </button>
                          </div>
                        </div>

                        {/* サブカテゴリー */}
                        {expandedMetricCategories.has(category) && (
                          <div className="bg-white">
                            {Object.entries(subCategories).map(([subCategory, metrics]) => {
                              const allMetricsInSub = metrics as readonly string[]
                              const allSubSelected = allMetricsInSub.every((m) => selectedMetrics.includes(m))
                              const someSubSelected = allMetricsInSub.some((m) => selectedMetrics.includes(m))

                              return (
                                <div key={subCategory} className="border-t border-slate-100">
                                  <div className="flex items-center px-4 py-1.5">
                                    <input
                                      type="checkbox"
                                      checked={allSubSelected}
                                      ref={(el) => {
                                        if (el) el.indeterminate = someSubSelected && !allSubSelected
                                      }}
                                      onChange={() => handleSubCategorySelectAll(category, subCategory)}
                                      className="w-3 h-3 text-blue-600 border-slate-300 rounded focus:ring-2 focus:ring-blue-500"
                                    />
                                    <button
                                      onClick={() => toggleMetricSubCategory(`${category}-${subCategory}`)}
                                      className="flex-1 flex items-center justify-between ml-2 hover:bg-slate-50 rounded px-2 py-1 transition-colors"
                                    >
                                      <span className="text-xs font-medium text-slate-600">{subCategory}</span>
                                      <svg
                                        className={`w-3 h-3 text-slate-400 transition-transform ${
                                          expandedMetricSubCategories.has(`${category}-${subCategory}`) ? 'rotate-180' : ''
                                        }`}
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                      >
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                      </svg>
                                    </button>
                                  </div>

                                  {/* 指標リスト */}
                                  {expandedMetricSubCategories.has(`${category}-${subCategory}`) && (
                                    <div className="px-4 pb-2 space-y-1">
                                      {metrics.map((metric) => (
                                        <label
                                          key={metric}
                                          className="flex items-center cursor-pointer hover:bg-blue-50 px-2 py-1 rounded transition-colors"
                                        >
                                          <input
                                            type="checkbox"
                                            checked={selectedMetrics.includes(metric)}
                                            onChange={() => handleMetricToggle(metric)}
                                            className="w-3 h-3 text-blue-600 border-slate-300 rounded focus:ring-2 focus:ring-blue-500"
                                          />
                                          <span className="ml-2 text-xs text-slate-700">{metric}</span>
                                        </label>
                                      ))}
                                    </div>
                                  )}
                                </div>
                              )
                            })}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* データタイプフィルター */}
              <div>
                <div className="flex items-center justify-between mb-2.5">
                  <label className="block text-sm font-semibold text-slate-700">
                    📁 データタイプ
                  </label>
                  {selectedDataTypes.length > 0 && (
                    <button
                      onClick={clearDataTypeFilter}
                      className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                    >
                      リセット
                    </button>
                  )}
                </div>
                {selectedDataTypes.length > 0 && (
                  <div className="mb-2 px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded border border-blue-200">
                    {selectedDataTypes.length} 件選択中
                  </div>
                )}
                <div className="space-y-1.5 max-h-48 overflow-y-auto">
                  {DATA_TYPES.map((dataType) => (
                    <label
                      key={dataType.value}
                      className="flex items-center cursor-pointer hover:bg-blue-50 px-3 py-2 rounded-lg transition-colors group"
                    >
                      <input
                        type="checkbox"
                        checked={selectedDataTypes.includes(dataType.value)}
                        onChange={() => handleDataTypeToggle(dataType.value)}
                        className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="ml-3 text-sm text-slate-700 group-hover:text-slate-900 font-medium">
                        {dataType.label}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* タグカテゴリー（モデル種別を除外） */}
              {tagsData && Object.entries(tagsData)
                .filter(([category]) => category !== 'model_type')
                .map(([category, tags]) => (
                  <div key={category}>
                    <div className="flex items-center justify-between mb-2.5">
                      <h3 className="text-sm font-semibold text-slate-700">
                        {getCategoryLabel(category)}
                      </h3>
                      {selectedTags[category]?.length > 0 && (
                        <span className="px-2 py-0.5 text-xs font-bold bg-blue-600 text-white rounded-full">
                          {selectedTags[category].length}
                        </span>
                      )}
                    </div>
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
                          <span className="ml-3 text-sm text-slate-700 group-hover:text-slate-900 font-medium">
                            {tag.name}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </aside>

        {/* Main Content - Competition List */}
        <div className="flex-1">
          <div className="bg-white rounded-xl shadow-md border border-slate-200">
            {/* Header with Sort, Favorite, Status */}
            <div className="px-8 py-6 border-b-2 border-slate-200 bg-gradient-to-r from-slate-50 to-white">
              <div className="flex items-center justify-between mb-4">
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

              {/* フィルターコントロール */}
              <div className="flex items-center gap-3">
                {/* 並び替え */}
                <select
                  value={sortBy}
                  onChange={(e) => handleSortChange(e.target.value)}
                  className="px-4 py-2 text-sm border-2 border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all bg-white hover:bg-slate-50 cursor-pointer font-medium"
                >
                  {SORT_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>

                {/* ステータス */}
                <select
                  value={status}
                  onChange={(e) => {
                    setStatus(e.target.value)
                    setPage(1)
                  }}
                  className="px-4 py-2 text-sm border-2 border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all bg-white hover:bg-slate-50 cursor-pointer font-medium"
                >
                  <option value="all">すべて</option>
                  <option value="active">🟢 開催中</option>
                  <option value="completed">🔴 終了済み</option>
                </select>

                {/* お気に入り */}
                <button
                  onClick={() => {
                    setIsFavorite(isFavorite === true ? null : true)
                    setPage(1)
                  }}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-all border-2 ${
                    isFavorite === true
                      ? 'bg-yellow-50 text-yellow-700 border-yellow-300'
                      : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {isFavorite === true ? '⭐ お気に入りのみ' : 'お気に入り'}
                </button>
              </div>
            </div>

            {/* Loading State */}
            {isLoading && (
              <div className="px-6 py-12 text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-3 text-slate-600 font-medium">読み込み中...</p>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="px-6 py-12 text-center">
                <p className="text-red-600 font-medium">データの取得に失敗しました</p>
              </div>
            )}

            {/* Competition List */}
            {competitionsData && competitionsData.items.length > 0 && (
              <>
                <div className="space-y-4">
                  {competitionsData.items.map((competition) => (
                    <div
                      key={competition.id}
                      className="bg-white rounded-xl border border-slate-200/60 hover:border-slate-300 hover:shadow-lg transition-all duration-200 group overflow-hidden"
                    >
                      <div className="px-8 py-6">
                        <div className="flex items-start justify-between gap-8">
                          <div className="flex-1 min-w-0">
                            <h3
                              onClick={() => router.push(`/competitions/${competition.id}`)}
                              className="text-lg font-semibold text-slate-900 mb-3 group-hover:text-blue-600 transition-colors cursor-pointer tracking-tight"
                            >
                              {competition.title}
                            </h3>

                          {/* 最優先情報: 評価指標とタスクタイプ */}
                          <div className="flex flex-wrap items-center gap-2.5 mb-4">
                            <StatusBadge status={competition.status} />
                            {competition.metric && isDisplayableMetric(competition.metric) && (
                              <MetricBadge
                                metric={competition.metric}
                                description={competition.metric_description}
                              />
                            )}
                            {competition.tags?.filter(tag =>
                              tag.includes('分類') || tag.includes('回帰') || tag.includes('物体検出') ||
                              tag.includes('セグメンテーション') || tag.includes('生成') || tag.includes('ランキング')
                            )?.map((tag, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl"
                              >
                                🎯 {tag}
                              </span>
                            ))}
                          </div>

                          {/* 構造化要約 */}
                          <StructuredSummaryDisplay summary={competition.summary} />

                          {/* データセット情報 */}
                          {competition.dataset_info && (
                            <DatasetInfoDisplay datasetInfo={competition.dataset_info} />
                          )}

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
                            {competition.tags?.filter(tag =>
                              !tag.includes('分類') && !tag.includes('回帰') && !tag.includes('物体検出') &&
                              !tag.includes('セグメンテーション') && !tag.includes('生成') && !tag.includes('ランキング')
                            )?.map((tag, idx) => (
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
                          className="shrink-0 px-5 py-2.5 text-sm font-medium text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded-lg transition-all flex items-center gap-2 group/btn"
                        >
                          <span>Kaggle で見る</span>
                          <svg className="w-4 h-4 group-hover/btn:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </a>
                      </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pagination - 改善版 */}
                {competitionsData.total_pages > 1 && (
                  <div className="mt-6 px-6 py-4 bg-slate-50/50 border border-slate-200/60 rounded-xl">
                    <div className="flex items-center justify-center gap-1">
                      {/* 先頭ページへ */}
                      <button
                        onClick={() => setPage(1)}
                        disabled={page === 1}
                        className="px-3 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:border-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                        title="先頭ページ"
                      >
                        «
                      </button>

                      {/* 前へ */}
                      <button
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="px-3 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:border-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                      >
                        ‹
                      </button>

                      {/* ページ番号 */}
                      {getPageNumbers().map((pageNum, idx) => {
                        if (pageNum === '...') {
                          return (
                            <span key={`ellipsis-${idx}`} className="px-3 py-2 text-slate-400">
                              ...
                            </span>
                          )
                        }
                        const isActive = pageNum === page
                        return (
                          <button
                            key={pageNum}
                            onClick={() => setPage(pageNum as number)}
                            className={`px-3 py-2 text-sm font-medium rounded-lg transition-all ${
                              isActive
                                ? 'bg-blue-600 text-white border border-blue-600'
                                : 'text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 hover:border-slate-300'
                            }`}
                          >
                            {pageNum}
                          </button>
                        )
                      })}

                      {/* 次へ */}
                      <button
                        onClick={() => setPage((p) => Math.min(competitionsData.total_pages, p + 1))}
                        disabled={page === competitionsData.total_pages}
                        className="px-3 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:border-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                      >
                        ›
                      </button>

                      {/* 末尾ページへ */}
                      <button
                        onClick={() => setPage(competitionsData.total_pages)}
                        disabled={page === competitionsData.total_pages}
                        className="px-3 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:border-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                        title="末尾ページ"
                      >
                        »
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Empty State */}
            {competitionsData && competitionsData.items.length === 0 && (
              <div className="px-6 py-12 text-center">
                <p className="text-slate-600 font-medium">条件に一致するコンペがありません</p>
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
      <div className="mb-4 bg-slate-50 rounded-lg p-4 border border-slate-200 space-y-3">
        {/* Overview */}
        <div>
          <p className="text-sm text-slate-800 leading-relaxed">{parsed.overview}</p>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white rounded-md p-2.5 border border-slate-200">
            <div className="text-xs font-semibold text-slate-600 mb-1">🎯 予測対象</div>
            <div className="text-xs text-slate-800 leading-relaxed">{parsed.objective}</div>
          </div>
          <div className="bg-white rounded-md p-2.5 border border-slate-200">
            <div className="text-xs font-semibold text-slate-600 mb-1">📊 データ</div>
            <div className="text-xs text-slate-800 leading-relaxed">{parsed.data}</div>
          </div>
        </div>

        {/* Business Value */}
        <div className="bg-white rounded-md p-2.5 border border-slate-200">
          <div className="text-xs font-semibold text-slate-600 mb-1">💼 ビジネス価値</div>
          <div className="text-xs text-slate-800 leading-relaxed">{parsed.business_value}</div>
        </div>

        {/* Key Challenges */}
        {parsed.key_challenges && parsed.key_challenges.length > 0 && (
          <div className="bg-white rounded-md p-2.5 border border-slate-200">
            <div className="text-xs font-semibold text-slate-600 mb-1.5">⚡ 主な課題</div>
            <ul className="space-y-1">
              {parsed.key_challenges.map((challenge, idx) => (
                <li key={idx} className="flex items-start gap-1.5 text-xs text-slate-700">
                  <span className="text-blue-600 mt-0.5">•</span>
                  <span>{challenge}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    )
  } catch {
    // JSON parsing failed, display as plain text
    return <p className="text-sm text-slate-600 mb-2">{summary}</p>
  }
}

// Helper component for metric badge with tooltip
function MetricBadge({ metric, description }: { metric: string; description?: string }) {
  // すべての評価指標でiアイコン付きツールチップを表示
  return (
    <div className="group/metric relative inline-block">
      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 rounded-xl cursor-help hover:bg-blue-100 hover:border-blue-300 transition-colors">
        📊 {metric}
        <svg className="w-3 h-3 opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </span>
      {/* ツールチップ - 遅延なしで即座に表示 */}
      <div className="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover/metric:opacity-100 transition-opacity duration-0 z-50 w-80">
        <div className="bg-slate-900 text-white text-xs rounded-lg p-3 shadow-xl">
          <div className="font-semibold text-blue-200 mb-1">📊 評価指標について</div>
          <div className="text-slate-100 leading-relaxed">
            {description || '説明が登録されていません'}
          </div>
          {/* 吹き出しの矢印 */}
          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px">
            <div className="border-8 border-transparent border-t-slate-900"></div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Helper component for dataset info display
function DatasetInfoDisplay({ datasetInfo }: { datasetInfo: string }) {
  const [isExpanded, setIsExpanded] = useState(false)

  try {
    const parsed: DatasetInfo = JSON.parse(datasetInfo)

    return (
      <div className="mb-3 bg-slate-50 border border-slate-200 rounded-lg overflow-hidden">
        {/* ヘッダー（クリックで展開/折りたたみ） */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full px-4 py-2.5 flex items-center justify-between hover:bg-slate-100 transition-colors"
        >
          <div className="flex items-center gap-2">
            <span className="text-blue-600 text-base">📦</span>
            <span className="text-sm font-semibold text-slate-700">データセット情報</span>
            {parsed.total_size && (
              <span className="px-2 py-0.5 text-xs font-bold bg-blue-100 text-blue-700 rounded">
                {parsed.total_size}
              </span>
            )}
          </div>
          <svg
            className={`w-5 h-5 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* 展開コンテンツ */}
        {isExpanded && (
          <div className="px-4 pb-3 pt-1 space-y-3 border-t border-slate-200 bg-white">
            {/* データ概要 */}
            {parsed.description && (
              <div>
                <div className="text-xs font-semibold text-slate-600 mb-1">概要</div>
                <div className="text-xs text-slate-700">{parsed.description}</div>
              </div>
            )}

            {/* ファイル一覧 */}
            {parsed.files && parsed.files.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-slate-600 mb-1.5">
                  📁 ファイル ({parsed.files.length}件)
                </div>
                <div className="flex flex-wrap gap-2">
                  {parsed.files.map((file, idx) => (
                    <span
                      key={idx}
                      className="inline-block px-2.5 py-1 text-xs font-mono font-medium bg-slate-100 text-slate-700 rounded border border-slate-200"
                    >
                      {file}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* 特徴量・カラム一覧 */}
            {parsed.features && parsed.features.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-slate-600 mb-1.5">
                  🔧 主要な特徴量 ({parsed.features.length}件)
                </div>
                <div className="grid grid-cols-2 gap-1.5">
                  {parsed.features.map((feature, idx) => (
                    <span
                      key={idx}
                      className="inline-block px-2.5 py-1 text-xs font-mono font-medium bg-blue-50 text-blue-700 rounded border border-blue-200"
                    >
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    )
  } catch {
    // JSON parsing failed
    return null
  }
}

// Helper component for status badge
function StatusBadge({ status }: { status: string }) {
  if (status === 'active') {
    return (
      <span className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
        </span>
        開催中
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200 rounded-xl">
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
    solution_method: '解法種別',
    competition_feature: 'コンペ特徴',
    domain: 'ドメイン',
  }
  return labels[category] || category
}
