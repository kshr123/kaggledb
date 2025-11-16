'use client'

import { Solution } from '@/types/competition'
import { useState, useEffect } from 'react'

interface SolutionModalProps {
  solution: Solution | null
  isOpen: boolean
  onClose: () => void
}

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

export default function SolutionModal({ solution, isOpen, onClose }: SolutionModalProps) {
  const [loading, setLoading] = useState(false)
  const [structuredSummary, setStructuredSummary] = useState<StructuredSummary | null>(null)
  const [links, setLinks] = useState<Links | null>(null)
  const [error, setError] = useState<string | null>(null)

  // モーダルが開いたときに既存の要約を読み込む
  useEffect(() => {
    if (isOpen && solution) {
      // 既存の要約があればそれを読み込む
      if (solution.summary && solution.summary !== 'null') {
        try {
          setStructuredSummary(JSON.parse(solution.summary))
        } catch (e) {
          console.error('Failed to parse summary:', e)
        }
      } else {
        // 要約がない場合はクリア
        setStructuredSummary(null)
      }
    }
  }, [isOpen, solution])

  if (!isOpen || !solution) return null

  const hasSummary = solution.summary && solution.summary !== 'null'

  const handleGenerateSummary = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`http://localhost:8000/api/solutions/${solution.id}/summarize`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('要約の生成に失敗しました')
      }

      const data = await response.json()

      // Parse the JSON strings
      if (data.summary) {
        setStructuredSummary(JSON.parse(data.summary))
      }
      if (data.links) {
        setLinks(data.links)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '要約の生成中にエラーが発生しました')
    } finally {
      setLoading(false)
    }
  }

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose()
      // Reset state when closing
      setStructuredSummary(null)
      setLinks(null)
      setError(null)
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-slate-200 p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                {/* Medal */}
                {solution.medal && (
                  <span className="text-3xl">
                    {solution.medal === 'gold' && '🥇'}
                    {solution.medal === 'silver' && '🥈'}
                    {solution.medal === 'bronze' && '🥉'}
                  </span>
                )}
                <h2 className="text-2xl font-bold text-slate-800">
                  {solution.title}
                </h2>
              </div>

              {/* Meta info */}
              <div className="flex items-center gap-4 text-sm text-slate-600">
                {/* Author */}
                {solution.author && (
                  <div className="flex items-center gap-2">
                    {solution.tier_color && (
                      <svg width="16" height="16" viewBox="0 0 16 16" className="flex-shrink-0">
                        <circle
                          r="6"
                          cx="8"
                          cy="8"
                          fill="none"
                          strokeWidth="2"
                          style={{ stroke: solution.tier_color }}
                        />
                      </svg>
                    )}
                    <span className="font-medium">{solution.author}</span>
                  </div>
                )}

                {/* Rank */}
                {solution.rank && (
                  <span className="text-slate-700 font-semibold">#{solution.rank}</span>
                )}

                {/* Votes */}
                <div className="flex items-center gap-1">
                  <span>👍</span>
                  <span>{solution.vote_count}</span>
                </div>

                {/* Comments */}
                <div className="flex items-center gap-1">
                  <span>💬</span>
                  <span>{solution.comment_count}</span>
                </div>
              </div>
            </div>

            {/* Close button */}
            <button
              onClick={() => {
                onClose()
                setStructuredSummary(null)
                setLinks(null)
                setError(null)
              }}
              className="text-slate-400 hover:text-slate-600 text-2xl leading-none ml-4"
            >
              ×
            </button>
          </div>

          {/* Original link */}
          <a
            href={solution.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 mt-4 text-blue-600 hover:text-blue-800 text-sm"
          >
            <span>📄</span>
            <span>元のディスカッションを見る</span>
            <span>↗</span>
          </a>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Links Section */}
          {links && (links.notebooks.length > 0 || links.github.length > 0 || links.other.length > 0) && (
            <div className="bg-slate-50 rounded-lg p-4">
              <h3 className="font-semibold text-slate-700 mb-3">🔗 関連リンク</h3>
              <div className="space-y-2">
                {links.notebooks.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-slate-600 mb-1">📓 Kaggle Notebooks</p>
                    <ul className="space-y-1">
                      {links.notebooks.map((link, idx) => (
                        <li key={idx}>
                          <a
                            href={link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:text-blue-800 hover:underline break-all"
                          >
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
                          <a
                            href={link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:text-blue-800 hover:underline break-all"
                          >
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
                          <a
                            href={link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:text-blue-800 hover:underline break-all"
                          >
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

          {/* Generate Summary Button */}
          {!structuredSummary && (
            <button
              onClick={handleGenerateSummary}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              {loading ? '要約生成中...' : '🤖 要約を生成'}
            </button>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              <p className="font-medium">エラー</p>
              <p className="text-sm">{error}</p>
            </div>
          )}

          {/* Structured Summary */}
          {structuredSummary && (
            <div className="space-y-6">
              {/* Overview */}
              {structuredSummary.overview && (
                <div>
                  <h3 className="font-semibold text-slate-700 mb-2 flex items-center gap-2">
                    <span>📋</span>
                    <span>概要</span>
                  </h3>
                  <p className="text-slate-600 leading-relaxed">
                    {structuredSummary.overview}
                  </p>
                </div>
              )}

              {/* Approach */}
              {structuredSummary.approach && (
                <div>
                  <h3 className="font-semibold text-slate-700 mb-2 flex items-center gap-2">
                    <span>🎯</span>
                    <span>アプローチ</span>
                  </h3>
                  <p className="text-slate-600 leading-relaxed whitespace-pre-line">
                    {structuredSummary.approach}
                  </p>
                </div>
              )}

              {/* Key Points */}
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

              {/* Results */}
              {structuredSummary.results && (
                <div>
                  <h3 className="font-semibold text-slate-700 mb-2 flex items-center gap-2">
                    <span>🏆</span>
                    <span>結果</span>
                  </h3>
                  <p className="text-slate-600 leading-relaxed">
                    {structuredSummary.results}
                  </p>
                </div>
              )}

              {/* Techniques */}
              {structuredSummary.techniques && structuredSummary.techniques.length > 0 && (
                <div>
                  <h3 className="font-semibold text-slate-700 mb-2 flex items-center gap-2">
                    <span>🔧</span>
                    <span>使用技術</span>
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {structuredSummary.techniques.map((tech, idx) => (
                      <span
                        key={idx}
                        className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-medium"
                      >
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
    </div>
  )
}
