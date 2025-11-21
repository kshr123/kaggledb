'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Solution } from '@/types/competition'

interface Technique {
  name: string
  english: string
  description: string
}

interface StructuredSummary {
  overview: string
  approach: string
  key_points: string[]
  results: string
  techniques: Technique[]
}

interface Links {
  notebooks: string[]
  github: string[]
  other: string[]
}

export default function SolutionDetailPage() {
  const params = useParams()
  const router = useRouter()
  const competitionId = params.id as string
  const solutionId = params.solutionId as string

  const [solution, setSolution] = useState<Solution | null>(null)
  const [loading, setLoading] = useState(true)
  const [isFetching, setIsFetching] = useState(false)
  const [structuredSummary, setStructuredSummary] = useState<StructuredSummary | null>(null)
  const [links, setLinks] = useState<Links | null>(null)
  const [error, setError] = useState<string | null>(null)

  // 解法情報を取得
  useEffect(() => {
    async function fetchSolution() {
      try {
        const res = await fetch(`http://localhost:8000/api/competitions/${competitionId}/solutions`)
        if (!res.ok) throw new Error('解法の取得に失敗しました')

        const solutions: Solution[] = await res.json()
        const sol = solutions.find(s => s.id === parseInt(solutionId))

        if (!sol) throw new Error('解法が見つかりません')

        setSolution(sol)

        // 既存の要約があれば読み込む
        if (sol.summary && sol.summary !== 'null') {
          try {
            setStructuredSummary(JSON.parse(sol.summary))
          } catch (e) {
            console.error('Failed to parse summary:', e)
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : '不明なエラー')
      } finally {
        setLoading(false)
      }
    }

    fetchSolution()
  }, [competitionId, solutionId])

  const handleFetchContent = async () => {
    if (!solution) return

    setIsFetching(true)
    setError(null)

    try {
      const response = await fetch(`http://localhost:8000/api/solutions/${solution.id}/fetch`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('解法詳細の取得に失敗しました')
      }

      const data = await response.json()

      if (data.solution) {
        setSolution(data.solution)
        if (data.solution.summary && data.solution.summary !== 'null') {
          try {
            setStructuredSummary(JSON.parse(data.solution.summary))
          } catch (e) {
            console.error('Failed to parse summary:', e)
          }
        }
      }
      if (data.links) {
        setLinks(data.links)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '詳細取得中にエラーが発生しました')
    } finally {
      setIsFetching(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100 flex items-center justify-center">
        <div className="text-slate-700 text-lg font-medium">読み込み中...</div>
      </div>
    )
  }

  if (error || !solution) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100 flex items-center justify-center">
        <div className="text-slate-700 text-lg font-medium">{error || '解法が見つかりません'}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* ヘッダー */}
        <button
          onClick={() => router.push(`/competitions/${competitionId}?tab=solutions`)}
          className="mb-4 flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors font-medium"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          解法一覧に戻る
        </button>

        {/* 解法ヘッダー */}
        <div className="bg-white/90 backdrop-blur-sm rounded-xl border border-slate-200 shadow-sm p-8 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                {solution.medal && (
                  <span className="text-3xl">
                    {solution.medal === 'gold' && '🥇'}
                    {solution.medal === 'silver' && '🥈'}
                    {solution.medal === 'bronze' && '🥉'}
                  </span>
                )}
                {solution.author_tier && (
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    solution.author_tier === 'Grandmaster' ? 'bg-yellow-100 text-yellow-700' :
                    solution.author_tier === 'Master' ? 'bg-purple-100 text-purple-700' :
                    'bg-slate-100 text-slate-700'
                  }`}>
                    🏆 {solution.author_tier}
                  </span>
                )}
              </div>

              <h1 className="text-3xl font-bold text-slate-900 mb-4">
                {solution.title}
              </h1>

              <div className="flex items-center gap-6 text-sm text-slate-600">
                {solution.author && (
                  <div className="flex items-center gap-2">
                    {solution.tier_color && (
                      <svg width="16" height="16" viewBox="0 0 16 16">
                        <circle r="6" cx="8" cy="8" fill="none" strokeWidth="2" style={{ stroke: solution.tier_color }} />
                      </svg>
                    )}
                    <span className={`font-medium ${
                      solution.author_tier === 'Grandmaster' ? 'text-yellow-600' :
                      solution.author_tier === 'Master' ? 'text-purple-600' :
                      'text-slate-700'
                    }`}>
                      👤 {solution.author}
                    </span>
                  </div>
                )}
                {solution.rank && (
                  <span className="flex items-center gap-1.5">
                    🏅 ランク #{solution.rank}
                  </span>
                )}
                <span className="flex items-center gap-1.5">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                  </svg>
                  {solution.vote_count} 票
                </span>
                <span className="flex items-center gap-1.5">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  {solution.comment_count} コメント
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleFetchContent}
                disabled={isFetching}
                className={`inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                  solution.content
                    ? 'text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 hover:border-blue-300'
                    : 'text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400'
                }`}
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
                    <span>{solution.content ? '要約を再生成' : '詳細を取得'}</span>
                  </>
                )}
              </button>

              <a
                href={solution.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded-lg transition-all"
              >
                <span>Kaggleで見る</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        </div>

        {/* リンクセクション */}
        {links && (links.notebooks.length > 0 || links.github.length > 0 || links.other.length > 0) && (
          <div className="bg-white rounded-lg p-6 mb-6 border border-slate-200">
            <h3 className="font-semibold text-slate-700 mb-3">🔗 関連リンク</h3>
            <div className="space-y-2">
              {links.notebooks.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-slate-600 mb-1">📓 Kaggle Notebooks</p>
                  <ul className="space-y-1">
                    {links.notebooks.map((link, idx) => (
                      <li key={idx}>
                        <a href={link} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:text-blue-800 hover:underline break-all">
                          {link}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {links.github.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-slate-600 mb-1">💻 GitHub</p>
                  <ul className="space-y-1">
                    {links.github.map((link, idx) => (
                      <li key={idx}>
                        <a href={link} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:text-blue-800 hover:underline break-all">
                          {link}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {links.other.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-slate-600 mb-1">🌐 その他</p>
                  <ul className="space-y-1">
                    {links.other.map((link, idx) => (
                      <li key={idx}>
                        <a href={link} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:text-blue-800 hover:underline break-all">
                          {link}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* コンテンツ */}
        <div className="bg-white/90 backdrop-blur-sm rounded-xl border border-slate-200 shadow-sm p-8">
          {solution.content || structuredSummary ? (
            <div className="space-y-6">
              {/* 構造化要約 */}
              {structuredSummary && (
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-5 space-y-6">
                  <h2 className="text-md font-semibold text-slate-900 mb-4">📝 要約</h2>

                  {structuredSummary.overview && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-5">
                      <h3 className="text-md font-semibold text-blue-900 mb-2">📋 概要</h3>
                      <p className="text-slate-700 leading-relaxed">{structuredSummary.overview}</p>
                    </div>
                  )}

                  {structuredSummary.approach && (
                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                      <h3 className="text-md font-semibold text-slate-900 mb-2">🎯 アプローチ</h3>
                      <p className="text-slate-700 leading-relaxed whitespace-pre-line">{structuredSummary.approach}</p>
                    </div>
                  )}

                  {structuredSummary.key_points && structuredSummary.key_points.length > 0 && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-5">
                      <h3 className="text-md font-semibold text-green-900 mb-3">✨ 重要ポイント</h3>
                      <ul className="space-y-2">
                        {structuredSummary.key_points.map((point, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-slate-700">
                            <span className="text-green-600 mt-1">•</span>
                            <span>{point}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {structuredSummary.results && (
                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                      <h3 className="text-md font-semibold text-slate-900 mb-3">✅ 結果・結論</h3>
                      <p className="text-slate-700 leading-relaxed">{structuredSummary.results}</p>
                    </div>
                  )}

                  {structuredSummary.techniques && structuredSummary.techniques.length > 0 && (
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-5">
                      <h3 className="text-md font-semibold text-purple-900 mb-3">🔧 使用技術</h3>
                      <div className="space-y-3">
                        {structuredSummary.techniques.map((tech, idx) => (
                          <div key={idx} className="bg-white border border-purple-200 rounded-lg p-3">
                            <div className="flex items-baseline gap-2 mb-1">
                              <span className="font-semibold text-slate-900">{tech.name}</span>
                              <span className="text-xs text-slate-500">({tech.english})</span>
                            </div>
                            <p className="text-sm text-slate-600">{tech.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 和訳された詳細 */}
              {solution.content && (
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                  <h2 className="text-md font-semibold text-slate-900 mb-3">📄 詳細（和訳）</h2>
                  <div className="text-slate-700 leading-relaxed whitespace-pre-wrap">
                    {solution.content}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <svg className="w-16 h-16 mx-auto text-slate-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-slate-500 text-lg mb-4">解法詳細がまだ取得されていません</p>
              <p className="text-slate-400 text-sm">上の「詳細を取得」ボタンをクリックしてください</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
