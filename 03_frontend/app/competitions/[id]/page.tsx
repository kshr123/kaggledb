'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Competition, DatasetInfo, StructuredSummary, Discussion, Solution } from '@/types/competition'
import SolutionCard from './components/SolutionCard'

type Tab = 'overview' | 'data' | 'discussion' | 'solutions' | 'notebooks'

export default function CompetitionDetailPage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const id = params.id as string

  // URLパラメータからタブを取得（デフォルトは'overview'）
  const tabFromUrl = (searchParams.get('tab') as Tab) || 'overview'

  const [competition, setCompetition] = useState<Competition | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<Tab>(tabFromUrl)
  const [isFavoriteLoading, setIsFavoriteLoading] = useState(false)
  const [isFetchingInfo, setIsFetchingInfo] = useState(false)

  useEffect(() => {
    async function fetchCompetition() {
      try {
        const response = await fetch(`http://localhost:8000/api/competitions/${id}`)
        if (!response.ok) {
          throw new Error('コンペティション情報の取得に失敗しました')
        }
        const data = await response.json()
        setCompetition(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : '予期しないエラーが発生しました')
      } finally {
        setLoading(false)
      }
    }

    fetchCompetition()
  }, [id])

  // お気に入り切り替え
  const toggleFavorite = async () => {
    if (!competition) return

    // お気に入りを外す場合は確認ダイアログを表示
    if (competition.is_favorite) {
      const confirmed = window.confirm(
        `このコンペのディスカッション（${competition.discussion_count}件）も削除されます。よろしいですか？`
      )
      if (!confirmed) return
    }

    setIsFavoriteLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/competitions/${id}/favorite`, {
        method: 'PATCH',
      })

      if (!response.ok) {
        throw new Error('お気に入りの更新に失敗しました')
      }

      const data = await response.json()

      // 成功通知
      if (data.is_favorite) {
        alert('お気に入りに追加しました')
      } else {
        alert(`お気に入りから削除しました（ディスカッション ${data.deleted_discussions} 件を削除）`)
      }

      // コンペティション情報を更新
      setCompetition({
        ...competition,
        is_favorite: data.is_favorite,
        discussion_count: data.is_favorite ? competition.discussion_count : 0
      })
    } catch (err) {
      alert(err instanceof Error ? err.message : 'エラーが発生しました')
    } finally {
      setIsFavoriteLoading(false)
    }
  }

  // 概要とデータセット情報を一度に取得
  const handleFetchAllInfo = async () => {
    if (!competition) return

    setIsFetchingInfo(true)
    try {
      // 概要を生成
      const summaryResponse = await fetch(`http://localhost:8000/api/competitions/${id}/summary/generate`, {
        method: 'POST',
      })

      if (!summaryResponse.ok) {
        throw new Error('概要の生成に失敗しました')
      }

      const summaryData = await summaryResponse.json()

      // データセット情報を取得
      const datasetResponse = await fetch(`http://localhost:8000/api/competitions/${id}/data/fetch`, {
        method: 'POST',
      })

      if (!datasetResponse.ok) {
        throw new Error('データセット情報の取得に失敗しました')
      }

      const datasetData = await datasetResponse.json()

      // コンペティション情報を更新
      setCompetition({
        ...competition,
        summary: JSON.stringify(summaryData.summary),
        dataset_info: JSON.stringify(datasetData.dataset_info)
      })

      alert('✅ 概要とデータセット情報を取得しました')
    } catch (err) {
      alert(err instanceof Error ? err.message : 'エラーが発生しました')
    } finally {
      setIsFetchingInfo(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100 flex items-center justify-center">
        <div className="text-slate-700 text-lg font-medium">読み込み中...</div>
      </div>
    )
  }

  if (error || !competition) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100 flex items-center justify-center">
        <div className="text-slate-700 text-lg font-medium">{error || 'コンペティションが見つかりません'}</div>
      </div>
    )
  }

  // summary and dataset_info are stored as plain text or JSON
  // Try to parse as JSON, fallback to plain text
  let summaryData: StructuredSummary | string | null = null
  if (competition.summary) {
    try {
      summaryData = JSON.parse(competition.summary)
    } catch {
      summaryData = competition.summary
    }
  }

  let datasetInfoData: DatasetInfo | string | null = null
  if (competition.dataset_info) {
    try {
      datasetInfoData = JSON.parse(competition.dataset_info)
    } catch {
      datasetInfoData = competition.dataset_info
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* ヘッダー */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/')}
            className="mb-4 flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors font-medium"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            一覧に戻る
          </button>

          <div className="flex items-start justify-between mb-3">
            <h1 className="text-3xl font-semibold text-slate-900 tracking-tight">{competition.title}</h1>
            <button
              onClick={toggleFavorite}
              disabled={isFavoriteLoading}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                competition.is_favorite
                  ? 'bg-yellow-50 text-yellow-700 border-2 border-yellow-200 hover:bg-yellow-100'
                  : 'bg-slate-100 text-slate-600 border-2 border-slate-200 hover:bg-slate-200'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              title={competition.is_favorite ? 'お気に入りから削除' : 'お気に入りに追加'}
            >
              <span className="text-xl">{competition.is_favorite ? '⭐' : '☆'}</span>
              <span className="text-sm">{competition.is_favorite ? 'お気に入り' : 'お気に入りに追加'}</span>
            </button>
          </div>

          <div className="flex items-center gap-3 text-sm">
            <span className={`px-3 py-1.5 rounded-xl font-medium ${competition.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'}`}>
              {competition.status === 'active' ? '開催中' : '終了'}
            </span>
            <span className="text-slate-600">{competition.domain}</span>
            {competition.metric && (
              <span className="flex items-center gap-1.5 text-slate-600">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                {competition.metric}
              </span>
            )}
          </div>
        </div>

        {/* タブナビゲーション */}
        <div className="bg-white/80 backdrop-blur-sm rounded-t-xl border border-slate-200/60">
          <div className="flex gap-1 p-1.5">
            <TabButton
              active={activeTab === 'overview'}
              onClick={() => setActiveTab('overview')}
              icon="📊"
              label="概要"
            />
            <TabButton
              active={activeTab === 'data'}
              onClick={() => setActiveTab('data')}
              icon="💾"
              label="データ"
              disabled={!datasetInfoData}
            />
            <TabButton
              active={activeTab === 'discussion'}
              onClick={() => setActiveTab('discussion')}
              icon="💬"
              label="ディスカッション"
              count={competition.discussion_count}
            />
            <TabButton
              active={activeTab === 'solutions'}
              onClick={() => setActiveTab('solutions')}
              icon="🏆"
              label="解法"
            />
            <TabButton
              active={activeTab === 'notebooks'}
              onClick={() => setActiveTab('notebooks')}
              icon="📔"
              label="ノートブック"
            />
          </div>
        </div>

        {/* タブコンテンツ */}
        <div className="bg-white/80 backdrop-blur-sm rounded-b-xl border border-slate-200/60 border-t-0 p-8">
          {activeTab === 'overview' && (
            <OverviewTab
              competition={competition}
              summary={summaryData}
              onFetchInfo={handleFetchAllInfo}
              isFetchingInfo={isFetchingInfo}
            />
          )}
          {activeTab === 'data' && <DataTab datasetInfo={datasetInfoData} competitionId={id} />}
          {activeTab === 'discussion' && <DiscussionTab competitionId={id} />}
          {activeTab === 'solutions' && <SolutionsTab competitionId={id} />}
          {activeTab === 'notebooks' && <NotebooksTab competitionId={id} />}
        </div>
      </div>
    </div>
  )
}

// タブボタンコンポーネント
function TabButton({ active, onClick, icon, label, count, disabled }: {
  active: boolean
  onClick: () => void
  icon: string
  label: string
  count?: number
  disabled?: boolean
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all ${
        active
          ? 'bg-white text-blue-600 shadow-sm border border-blue-100'
          : disabled
          ? 'text-slate-400 cursor-not-allowed'
          : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
      }`}
    >
      <span>{icon}</span>
      <span>{label}</span>
      {count !== undefined && count > 0 && (
        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${active ? 'bg-blue-100 text-blue-600' : 'bg-slate-200 text-slate-600'}`}>
          {count}
        </span>
      )}
    </button>
  )
}

// 概要タブ
function OverviewTab({
  competition,
  summary,
  onFetchInfo,
  isFetchingInfo = false
}: {
  competition: Competition
  summary: StructuredSummary | string | null
  onFetchInfo?: () => void
  isFetchingInfo?: boolean
}) {
  return (
    <div className="space-y-5">
      {/* Kaggleで見る & スクレイピングボタン */}
      <div className="flex justify-end gap-3">
        {onFetchInfo && (
          <button
            onClick={onFetchInfo}
            disabled={isFetchingInfo}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-lg transition-all"
          >
            <span>{isFetchingInfo ? '取得中...' : '📝 概要・データ情報を取得'}</span>
          </button>
        )}
        <a
          href={competition.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded-lg transition-all group/btn"
        >
          <span>Kaggle で見る</span>
          <svg className="w-4 h-4 group-hover/btn:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>

      {summary && (
        <div className="bg-slate-50 rounded-xl p-6 border border-slate-200 space-y-5">
          {typeof summary === 'string' ? (
            /* プレーンテキストの場合 */
            <div>
              <h3 className="text-base font-semibold text-slate-900 mb-2 flex items-center gap-2">
                <span>📝</span>
                概要
              </h3>
              <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">{summary}</p>
            </div>
          ) : (
            <>
              {/* 構造化データの場合 */}
              <div>
                <h3 className="text-base font-semibold text-slate-900 mb-2 flex items-center gap-2">
                  <span>📝</span>
                  概要
                </h3>
                <p className="text-slate-700 leading-relaxed">{summary.overview}</p>
              </div>

              {/* 目的・データ・ビジネス価値を2カラムで表示 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white rounded-lg p-4 border border-slate-200">
                  <h4 className="text-sm font-semibold text-slate-900 mb-2 flex items-center gap-1.5">
                    <span>🎯</span>
                    予測目的
                  </h4>
                  <p className="text-sm text-slate-700 leading-relaxed">{summary.objective}</p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-slate-200">
                  <h4 className="text-sm font-semibold text-slate-900 mb-2 flex items-center gap-1.5">
                    <span>📊</span>
                    データ
                  </h4>
                  <p className="text-sm text-slate-700 leading-relaxed">{summary.data}</p>
                </div>
              </div>

              {/* ビジネス価値 */}
              <div className="bg-white rounded-lg p-4 border border-slate-200">
                <h4 className="text-sm font-semibold text-slate-900 mb-2 flex items-center gap-1.5">
                  <span>💼</span>
                  ビジネス価値
                </h4>
                <p className="text-sm text-slate-700 leading-relaxed">{summary.business_value}</p>
              </div>

              {/* 評価指標（最重要） */}
              {summary.evaluation && (
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-5 border-2 border-blue-200">
                  <h4 className="text-base font-bold text-blue-900 mb-3 flex items-center gap-2">
                    <span className="text-xl">📈</span>
                    評価指標
                  </h4>
                  <div className="space-y-3">
                    {/* 指標名 */}
                    <div>
                      <span className="inline-block px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm font-bold mb-2">
                        {summary.evaluation.metric}
                      </span>
                    </div>

                    {/* 説明 */}
                    <div className="bg-white/80 rounded-lg p-3 border border-blue-100">
                      <h5 className="text-xs font-semibold text-blue-900 mb-1.5">📖 指標の説明</h5>
                      <p className="text-sm text-slate-700 leading-relaxed">{summary.evaluation.explanation}</p>
                    </div>

                    {/* 重要性 */}
                    <div className="bg-white/80 rounded-lg p-3 border border-blue-100">
                      <h5 className="text-xs font-semibold text-blue-900 mb-1.5">💡 なぜ重要か</h5>
                      <p className="text-sm text-slate-700 leading-relaxed">{summary.evaluation.why_important}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* 主な課題 */}
              {summary.key_challenges && summary.key_challenges.length > 0 && (
                <div className="bg-white rounded-lg p-4 border border-slate-200">
                  <h4 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-1.5">
                    <span>⚡</span>
                    主な課題
                  </h4>
                  <ul className="space-y-2">
                    {summary.key_challenges.map((challenge, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-slate-700">
                        <span className="text-blue-600 mt-0.5">•</span>
                        <span>{challenge}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* タグとデータタイプを横並びで表示 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {competition.tags && competition.tags.length > 0 && (
          <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
            <h3 className="text-base font-semibold text-slate-900 mb-3 flex items-center gap-2">
              <span>🏷️</span>
              タグ
            </h3>
            <div className="flex flex-wrap gap-2">
              {competition.tags.map((tag) => (
                <span key={tag} className="px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-xl text-sm font-medium">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {competition.data_types && competition.data_types.length > 0 && (
          <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
            <h3 className="text-base font-semibold text-slate-900 mb-3 flex items-center gap-2">
              <span>📦</span>
              データタイプ
            </h3>
            <div className="flex flex-wrap gap-2">
              {competition.data_types.map((dataType) => (
                <span key={dataType} className="px-3 py-1.5 bg-purple-50 text-purple-700 border border-purple-200 rounded-xl text-sm font-medium">
                  {dataType}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// データタブ
function DataTab({ datasetInfo, competitionId }: { datasetInfo: DatasetInfo | string | null; competitionId: string }) {
  if (!datasetInfo) {
    return (
      <div className="text-center py-12 text-slate-500">
        データセット情報がまだ収集されていません
      </div>
    )
  }

  // If datasetInfo is a plain string, show it as text
  if (typeof datasetInfo === 'string') {
    return (
      <div className="space-y-6">
        <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900 mb-3">📄 データセット情報</h3>
          <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">{datasetInfo}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Kaggleで見るボタン */}
      <div className="flex justify-end">
        <a
          href={`https://www.kaggle.com/competitions/${competitionId}/data`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded-lg transition-all group/btn"
        >
          <span>Kaggle で見る</span>
          <svg className="w-4 h-4 group-hover/btn:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
      {/* データセット概要 */}
      {datasetInfo.description && (
        <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900 mb-3">📄 データセット概要</h3>
          <p className="text-slate-700 leading-relaxed">{datasetInfo.description}</p>
        </div>
      )}

      {/* ファイル一覧 */}
      {datasetInfo.files && datasetInfo.files.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
            <span>📁</span>
            ファイル一覧
            {datasetInfo.total_size && (
              <span className="text-sm font-normal text-slate-500">({datasetInfo.total_size})</span>
            )}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {datasetInfo.files.map((file, index) => (
              <div key={index} className="bg-slate-50 rounded-lg px-4 py-3 border border-slate-200 flex items-center gap-3 hover:border-slate-300 transition-colors">
                <svg className="w-5 h-5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <span className="text-slate-700 font-mono text-sm">{file}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* カラム情報 */}
      {datasetInfo.columns && datasetInfo.columns.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-slate-900 mb-3">🔧 カラム情報</h3>
          <div className="overflow-x-auto border border-slate-200 rounded-xl">
            <table className="w-full">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700 w-48">カラム名</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700">説明</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {datasetInfo.columns.map((column, index) => (
                  <tr key={index} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3">
                      <code className="px-2.5 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg text-sm font-mono font-semibold">
                        {column.name}
                      </code>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-700 leading-relaxed">
                      {column.description}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 特徴量一覧（columnsがない場合のフォールバック） */}
      {(!datasetInfo.columns || datasetInfo.columns.length === 0) && datasetInfo.features && datasetInfo.features.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-slate-900 mb-3">🔧 主要な特徴量</h3>
          <div className="flex flex-wrap gap-2">
            {datasetInfo.features.map((feature, index) => (
              <code key={index} className="px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-xl text-sm font-mono font-medium">
                {feature}
              </code>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ディスカッションタブ
function DiscussionTab({ competitionId }: { competitionId: string }) {
  const [discussions, setDiscussions] = useState<Discussion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedDiscussion, setSelectedDiscussion] = useState<Discussion | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isFetching, setIsFetching] = useState(false)

  useEffect(() => {
    async function fetchDiscussions() {
      try {
        setLoading(true)
        setError(null)
        const res = await fetch(`http://localhost:8000/api/competitions/${competitionId}/discussions`)

        if (!res.ok) {
          throw new Error('ディスカッションの取得に失敗しました')
        }

        const data = await res.json()
        setDiscussions(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : '不明なエラーが発生しました')
      } finally {
        setLoading(false)
      }
    }

    fetchDiscussions()
  }, [competitionId])

  // ディスカッション取得・更新
  const handleFetchDiscussions = async () => {
    setIsFetching(true)
    try {
      const res = await fetch(`http://localhost:8000/api/competitions/${competitionId}/discussions/fetch`, {
        method: 'POST',
      })

      if (!res.ok) {
        throw new Error('ディスカッションの取得に失敗しました')
      }

      const data = await res.json()

      // 成功メッセージ（Writeups・解法も同時に取得されたことを通知）
      const writeupsInfo = data.writeups_count > 0 ? `\n（Writeups: ${data.writeups_count}件含む）` : ''
      alert(
        `✅ ディスカッション・解法取得完了\n\n` +
        `【ディスカッション】\n` +
        `新規: ${data.discussions.saved}件\n` +
        `更新: ${data.discussions.updated}件\n` +
        `合計: ${data.discussions.total}件${writeupsInfo}\n\n` +
        `【解法】\n` +
        `新規: ${data.solutions.saved}件\n` +
        `更新: ${data.solutions.updated}件\n` +
        `合計: ${data.solutions.total}件`
      )

      // ディスカッション一覧を再取得
      const listRes = await fetch(`http://localhost:8000/api/competitions/${competitionId}/discussions`)
      if (listRes.ok) {
        const listData = await listRes.json()
        setDiscussions(listData)
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'エラーが発生しました')
    } finally {
      setIsFetching(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-500 font-medium">{error}</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{discussions.length}件のディスカッション</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleFetchDiscussions}
            disabled={isFetching}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 border border-blue-600 rounded-lg transition-all"
          >
            {isFetching ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>取得中...</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>ディスカッション更新</span>
              </>
            )}
          </button>
          <a
            href={`https://www.kaggle.com/competitions/${competitionId}/discussion`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded-lg transition-all group/btn"
          >
            <span>Kaggle で見る</span>
            <svg className="w-4 h-4 group-hover/btn:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </div>

      {/* ディスカッション一覧 */}
      {discussions.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-slate-500 font-medium">ディスカッションがありません</div>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-lg divide-y divide-slate-200">
          {discussions.map((discussion) => (
            <Link
              key={discussion.id}
              href={`/competitions/${competitionId}/discussions/${discussion.id}`}
              className="block px-4 py-3 hover:bg-slate-50 transition-colors group"
            >
              <div className="flex items-start gap-3">
                {/* 投票数 */}
                <div className="flex flex-col items-center min-w-[48px] pt-1">
                  <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                  </svg>
                  <span className="text-sm font-medium text-slate-700">{discussion.vote_count}</span>
                </div>

                {/* ディスカッション情報 */}
                <div className="flex-1 min-w-0">
                  {/* タイトル */}
                  <h4 className="text-base font-medium text-slate-900 group-hover:text-blue-600 transition-colors mb-1">
                    {discussion.title}
                  </h4>

                  {/* メタ情報 */}
                  <div className="flex items-center gap-3 text-sm text-slate-500">
                    {discussion.author && (
                      <div className="flex items-center gap-1.5">
                        {/* Tier色インジケーター */}
                        {discussion.tier_color && (
                          <svg width="16" height="16" viewBox="0 0 16 16" className="flex-shrink-0">
                            <circle
                              r="6"
                              cx="8"
                              cy="8"
                              fill="none"
                              strokeWidth="2"
                              style={{ stroke: discussion.tier_color }}
                            />
                          </svg>
                        )}
                        <span className={`font-medium ${
                          discussion.author_tier === 'Grandmaster' ? 'text-yellow-600' :
                          discussion.author_tier === 'Master' ? 'text-purple-600' :
                          'text-slate-600'
                        }`}>
                          {discussion.author}
                        </span>
                      </div>
                    )}
                    <span>·</span>
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                      {discussion.comment_count}
                    </span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* ディスカッション詳細モーダル */}
      {isModalOpen && selectedDiscussion && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setIsModalOpen(false)}
        >
          <div
            className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* ヘッダー */}
            <div className="flex items-start justify-between p-6 border-b border-slate-200">
              <div className="flex-1 min-w-0 pr-4">
                <div className="flex items-center gap-2 mb-2">
                  {selectedDiscussion.is_pinned && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
                      📌 ピン留め
                    </span>
                  )}
                  {selectedDiscussion.author_tier && (selectedDiscussion.author_tier === 'Master' || selectedDiscussion.author_tier === 'Grandmaster') && (
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                      selectedDiscussion.author_tier === 'Grandmaster' ? 'bg-yellow-100 text-yellow-700' : 'bg-purple-100 text-purple-700'
                    }`}>
                      🏆 {selectedDiscussion.author_tier}
                    </span>
                  )}
                </div>
                <h2 className="text-xl font-semibold text-slate-900 mb-2">
                  {selectedDiscussion.title}
                </h2>
                <div className="flex items-center gap-4 text-sm text-slate-600">
                  {selectedDiscussion.author && (
                    <span className={
                      selectedDiscussion.author_tier === 'Grandmaster' ? 'text-yellow-600 font-semibold' :
                      selectedDiscussion.author_tier === 'Master' ? 'text-purple-600 font-semibold' :
                      'text-slate-600'
                    }>
                      👤 {selectedDiscussion.author}
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                    </svg>
                    {selectedDiscussion.vote_count} 票
                  </span>
                  <span className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    {selectedDiscussion.comment_count} コメント
                  </span>
                </div>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* コンテンツ */}
            <div className="flex-1 overflow-y-auto p-6">
              {selectedDiscussion.summary ? (
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-2">📝 要約</h3>
                  <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
                    {selectedDiscussion.summary}
                  </p>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-slate-500">要約がまだ生成されていません</p>
                </div>
              )}
            </div>

            {/* フッター */}
            <div className="border-t border-slate-200 p-6 flex justify-end">
              <a
                href={selectedDiscussion.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
              >
                <span>Kaggle で見る</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// 解法タブコンポーネント
function SolutionsTab({ competitionId }: { competitionId: string }) {
  const [solutions, setSolutions] = useState<Solution[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [fetching, setFetching] = useState(false)

  useEffect(() => {
    async function fetchSolutions() {
      try {
        setLoading(true)
        setError(null)
        const res = await fetch(`http://localhost:8000/api/competitions/${competitionId}/solutions`)

        if (!res.ok) {
          throw new Error('解法の取得に失敗しました')
        }

        const data = await res.json()
        setSolutions(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : '不明なエラーが発生しました')
      } finally {
        setLoading(false)
      }
    }

    fetchSolutions()
  }, [competitionId])

  const handleFetchSolutions = async () => {
    if (fetching) return

    try {
      setFetching(true)
      setError(null)

      const res = await fetch(
        `http://localhost:8000/api/competitions/${competitionId}/solutions/fetch`,
        { method: 'POST' }
      )

      if (!res.ok) {
        throw new Error('解法の収集に失敗しました')
      }

      const result = await res.json()

      // 解法一覧を再取得
      const solutionsRes = await fetch(`http://localhost:8000/api/competitions/${competitionId}/solutions`)
      if (solutionsRes.ok) {
        const data = await solutionsRes.json()
        setSolutions(data)
      }

      alert(
        `✅ 解法収集完了\n\n` +
        `新規: ${result.saved}件\n` +
        `更新: ${result.updated}件`
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : '不明なエラーが発生しました')
    } finally {
      setFetching(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error}</p>
      </div>
    )
  }

  if (solutions.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500 mb-4">解法がまだ収集されていません</p>

        {/* 解法収集ボタン */}
        <button
          onClick={handleFetchSolutions}
          disabled={fetching}
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            fetching
              ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {fetching ? '収集中...' : '解法を取得'}
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* 解法収集ボタン（上部） */}
      <div className="flex justify-end">
        <button
          onClick={handleFetchSolutions}
          disabled={fetching}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
            fetching
              ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {fetching ? '収集中...' : '解法を再取得'}
        </button>
      </div>

      {/* 解法一覧 */}
      <div className="space-y-3">
        {solutions.map((solution) => (
          <SolutionCard
            key={solution.id}
            solution={solution}
            competitionId={competitionId}
          />
        ))}
      </div>
    </div>
  )
}

// ノートブックタブコンポーネント
function NotebooksTab({ competitionId }: { competitionId: string }) {
  const [notebooks, setNotebooks] = useState<Solution[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [fetching, setFetching] = useState(false)

  useEffect(() => {
    async function loadNotebooks() {
      try {
        setLoading(true)
        setError(null)
        const res = await fetch(`http://localhost:8000/api/competitions/${competitionId}/notebooks`)

        if (!res.ok) {
          throw new Error('ノートブックの取得に失敗しました')
        }

        const data = await res.json()
        setNotebooks(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : '不明なエラーが発生しました')
      } finally {
        setLoading(false)
      }
    }

    loadNotebooks()
  }, [competitionId])

  const handleFetchNotebooks = async () => {
    try {
      setFetching(true)
      setError(null)

      const res = await fetch(
        `http://localhost:8000/api/competitions/${competitionId}/notebooks/fetch`,
        { method: 'POST' }
      )

      if (!res.ok) {
        throw new Error('ノートブックの収集に失敗しました')
      }

      const result = await res.json()

      // ノートブック一覧を再取得
      const notebooksRes = await fetch(`http://localhost:8000/api/competitions/${competitionId}/notebooks`)
      if (notebooksRes.ok) {
        const data = await notebooksRes.json()
        setNotebooks(data)
      }

      alert(
        `✅ ノートブック収集完了\n\n` +
        `新規: ${result.saved}件\n` +
        `更新: ${result.updated}件`
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : '不明なエラーが発生しました')
    } finally {
      setFetching(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">読み込み中...</div>
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={handleFetchNotebooks}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          再試行
        </button>
      </div>
    )
  }

  if (notebooks.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500 mb-4">ノートブックがまだ収集されていません</p>

        {/* ノートブック収集ボタン */}
        <button
          onClick={handleFetchNotebooks}
          disabled={fetching}
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            fetching
              ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {fetching ? '収集中...' : 'ノートブックを取得'}
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* ノートブック収集ボタン（上部） */}
      <div className="flex justify-end">
        <button
          onClick={handleFetchNotebooks}
          disabled={fetching}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
            fetching
              ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {fetching ? '収集中...' : 'ノートブックを再取得'}
        </button>
      </div>

      {/* ノートブック一覧 */}
      <div className="space-y-3">
        {notebooks.map((notebook) => (
          <SolutionCard
            key={notebook.id}
            solution={notebook}
            competitionId={competitionId}
          />
        ))}
      </div>
    </div>
  )
}

// セクションコンポーネント
function Section({ title, content }: { title: string; content: string }) {
  return (
    <div>
      <h3 className="text-lg font-semibold text-slate-900 mb-3">{title}</h3>
      <p className="text-slate-700 leading-relaxed">{content}</p>
    </div>
  )
}
