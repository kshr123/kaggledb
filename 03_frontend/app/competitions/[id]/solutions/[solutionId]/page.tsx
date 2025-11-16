'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Solution } from '@/types/competition'

interface StructuredSummary {
  overview: string
  approach: string
  key_points: string[]
  results: string
  techniques: string[]
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
  const [summarizing, setSummarizing] = useState(false)
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

  const handleGenerateSummary = async () => {
    if (!solution) return

    setSummarizing(true)
    setError(null)

    try {
      const response = await fetch(`http://localhost:8000/api/solutions/${solution.id}/summarize`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('要約の生成に失敗しました')
      }

      const data = await response.json()

      if (data.summary) {
        setStructuredSummary(JSON.parse(data.summary))
      }
      if (data.links) {
        setLinks(data.links)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '要約の生成中にエラーが発生しました')
    } finally {
      setSummarizing(false)
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

  const hasSummary = solution.summary && solution.summary !== 'null'

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* ヘッダー */}
        <button
          onClick={() => router.push(`/competitions/${competitionId}`)}
          className="mb-4 flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors font-medium"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          解法一覧に戻る
        </button>

        {/* 解法ヘッダー */}
        <div className="bg-white rounded-lg p-6 mb-6 border border-slate-200">
          <div className="flex items-start gap-3 mb-4">
            {solution.medal && (
              <span className="text-3xl">
                {solution.medal === 'gold' && '🥇'}
                {solution.medal === 'silver' && '🥈'}
                {solution.medal === 'bronze' && '🥉'}
              </span>
            )}
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-slate-800 mb-2">
                {solution.title}
              </h1>
              <div className="flex items-center gap-4 text-sm text-slate-600">
                {solution.author && (
                  <div className="flex items-center gap-2">
                    {solution.tier_color && (
                      <svg width="16" height="16" viewBox="0 0 16 16" className="flex-shrink-0">
                        <circle r="6" cx="8" cy="8" fill="none" strokeWidth="2" style={{ stroke: solution.tier_color }} />
                      </svg>
                    )}
                    <span className="font-medium">{solution.author}</span>
                  </div>
                )}
                {solution.rank && <span className="text-slate-700 font-semibold">#{solution.rank}</span>}
                <div className="flex items-center gap-1">
                  <span>👍</span>
                  <span>{solution.vote_count}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>💬</span>
                  <span>{solution.comment_count}</span>
                </div>
              </div>
            </div>
          </div>

          <a
            href={solution.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 text-sm"
          >
            <span>📄</span>
            <span>元のディスカッションを見る</span>
            <span>↗</span>
          </a>
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

        {/* 要約生成ボタン */}
        {!structuredSummary && (
          <div className="bg-white rounded-lg p-6 mb-6 border border-slate-200">
            <button
              onClick={handleGenerateSummary}
              disabled={summarizing}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              {summarizing ? '要約生成中...' : '🤖 要約を生成'}
            </button>
          </div>
        )}

        {/* 要約表示 */}
        {structuredSummary && (
          <div className="bg-white rounded-lg p-6 border border-slate-200 space-y-6">
            <h2 className="text-xl font-bold text-slate-800">📝 要約</h2>

            {structuredSummary.overview && (
              <div>
                <h3 className="font-semibold text-slate-700 mb-2 flex items-center gap-2">
                  <span>📋</span>
                  <span>概要</span>
                </h3>
                <p className="text-slate-600 leading-relaxed">{structuredSummary.overview}</p>
              </div>
            )}

            {structuredSummary.approach && (
              <div>
                <h3 className="font-semibold text-slate-700 mb-2 flex items-center gap-2">
                  <span>🎯</span>
                  <span>アプローチ</span>
                </h3>
                <p className="text-slate-600 leading-relaxed whitespace-pre-line">{structuredSummary.approach}</p>
              </div>
            )}

            {structuredSummary.key_points && structuredSummary.key_points.length > 0 && (
              <div>
                <h3 className="font-semibold text-slate-700 mb-2 flex items-center gap-2">
                  <span>💡</span>
                  <span>重要ポイント</span>
                </h3>
                <ul className="space-y-2">
                  {structuredSummary.key_points.map((point, idx) => (
                    <li key={idx} className="flex gap-2">
                      <span className="text-blue-600 font-bold">•</span>
                      <span className="text-slate-600 leading-relaxed">{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {structuredSummary.results && (
              <div>
                <h3 className="font-semibold text-slate-700 mb-2 flex items-center gap-2">
                  <span>🏆</span>
                  <span>結果</span>
                </h3>
                <p className="text-slate-600 leading-relaxed">{structuredSummary.results}</p>
              </div>
            )}

            {structuredSummary.techniques && structuredSummary.techniques.length > 0 && (
              <div>
                <h3 className="font-semibold text-slate-700 mb-2 flex items-center gap-2">
                  <span>🔧</span>
                  <span>使用技術</span>
                </h3>
                <div className="flex flex-wrap gap-2">
                  {structuredSummary.techniques.map((tech, idx) => (
                    <span key={idx} className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-medium">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
