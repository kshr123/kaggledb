'use client'

import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import Link from 'next/link'

interface Notebook {
  id: number
  competition_id: string
  title: string
  author: string
  author_tier: string | null
  tier_color: string | null
  url: string
  type: string
  medal: string | null
  rank: number | null
  vote_count: number
  comment_count: number
  summary: string | null
  techniques: string | null
  created_at: string
}

interface NotebookSummary {
  purpose: string
  data_overview: string
  input_data: {
    format: string
    columns: string[]
    size: string
  }
  output_data: {
    type: string
    description: string
  }
  approach: string
  processing_steps: string[]
  key_techniques: Array<{
    name: string
    explanation: string
  }>
  models_used: Array<{
    name: string
    explanation: string
  }>
  glossary: Array<{
    term: string
    explanation: string
  }>
  results: string
  useful_for: string
}

export default function NotebookDetailPage() {
  const params = useParams()
  const router = useRouter()
  const competitionId = params.id as string
  const notebookId = params.notebookId as string

  const [notebook, setNotebook] = useState<Notebook | null>(null)
  const [summary, setSummary] = useState<NotebookSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [summarizing, setSummarizing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchNotebook() {
      try {
        setLoading(true)
        const res = await fetch(`http://localhost:8000/api/competitions/${competitionId}/notebooks`)
        if (!res.ok) throw new Error('Failed to fetch notebooks')

        const notebooks = await res.json()
        const found = notebooks.find((n: Notebook) => n.id === parseInt(notebookId))

        if (!found) {
          setError('Notebook not found')
          return
        }

        setNotebook(found)

        // summaryがあればパース
        if (found.summary) {
          try {
            const parsedSummary = JSON.parse(found.summary)
            setSummary(parsedSummary)
          } catch (e) {
            console.error('Failed to parse summary:', e)
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchNotebook()
  }, [competitionId, notebookId])

  const handleGenerateSummary = async () => {
    if (!notebook) return

    try {
      setSummarizing(true)
      setError(null)

      const res = await fetch(`http://localhost:8000/api/notebooks/${notebook.id}/summarize`, {
        method: 'POST'
      })

      if (!res.ok) {
        throw new Error('Failed to generate summary')
      }

      const data = await res.json()
      setSummary(data.summary)

      // notebookのsummaryも更新
      setNotebook({
        ...notebook,
        summary: JSON.stringify(data.summary)
      })

      alert(data.cached ? '✅ キャッシュから要約を取得しました' : '✅ 要約を生成しました')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      alert('❌ 要約の生成に失敗しました')
    } finally {
      setSummarizing(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8">
        <div className="max-w-5xl mx-auto">
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    )
  }

  if (error || !notebook) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8">
        <div className="max-w-5xl mx-auto">
          <p className="text-red-600">{error || 'Notebook not found'}</p>
          <Link href={`/competitions/${competitionId}`} className="text-blue-600 hover:underline mt-4 inline-block">
            ← Back to competition
          </Link>
        </div>
      </div>
    )
  }

  const getTierColorClass = (color: string | null) => {
    if (!color) return 'bg-gray-100 text-gray-700'
    const colorMap: Record<string, string> = {
      'orange': 'bg-orange-100 text-orange-700',
      'purple': 'bg-purple-100 text-purple-700',
      'blue': 'bg-blue-100 text-blue-700',
      'white': 'bg-gray-100 text-gray-700'
    }
    return colorMap[color.toLowerCase()] || 'bg-gray-100 text-gray-700'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link href={`/competitions/${competitionId}?tab=notebooks`} className="text-blue-600 hover:underline mb-4 inline-block">
            ← Back to notebooks
          </Link>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">{notebook.title}</h1>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span className="flex items-center gap-1">
              👤 {notebook.author}
              {notebook.author_tier && (
                <span className={`ml-2 px-2 py-0.5 rounded text-xs ${getTierColorClass(notebook.tier_color)}`}>
                  {notebook.author_tier}
                </span>
              )}
            </span>
            <span>👍 {notebook.vote_count} votes</span>
            <span>💬 {notebook.comment_count} comments</span>
          </div>
        </div>

        {/* Kaggle Link */}
        <a
          href={notebook.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block mb-6 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          📔 View on Kaggle →
        </a>

        {/* Summary Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-800">🤖 AI要約</h2>
            <button
              onClick={handleGenerateSummary}
              disabled={summarizing}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {summarizing ? '生成中...' : summary ? '要約を再生成' : '要約を生成'}
            </button>
          </div>

          {summary ? (
            <div className="space-y-6">
              {/* Purpose */}
              <div>
                <h3 className="text-lg font-semibold text-gray-700 mb-2">🎯 目的</h3>
                <p className="text-gray-600">{summary.purpose}</p>
              </div>

              {/* Data Overview */}
              <div>
                <h3 className="text-lg font-semibold text-gray-700 mb-2">📁 データ概要</h3>
                <p className="text-gray-600">{summary.data_overview}</p>
              </div>

              {/* Input Data */}
              {summary.input_data && (
                <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                  <h3 className="text-lg font-bold text-green-800 mb-3">📥 インプット（入力データ）</h3>
                  <div className="space-y-2 text-gray-700">
                    <div>
                      <span className="font-semibold">形式:</span> {summary.input_data.format}
                    </div>
                    {summary.input_data.columns && summary.input_data.columns.length > 0 && (
                      <div>
                        <span className="font-semibold">主要カラム:</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {summary.input_data.columns.map((col, index) => (
                            <span key={index} className="px-2 py-1 bg-green-100 border border-green-300 rounded text-sm">
                              {col}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    <div>
                      <span className="font-semibold">サイズ:</span> {summary.input_data.size}
                    </div>
                  </div>
                </div>
              )}

              {/* Output Data */}
              {summary.output_data && (
                <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                  <h3 className="text-lg font-bold text-blue-800 mb-3">📤 アウトプット（出力）</h3>
                  <div className="space-y-2 text-gray-700">
                    <div>
                      <span className="font-semibold">種類:</span> {summary.output_data.type}
                    </div>
                    <div>
                      <span className="font-semibold">説明:</span> {summary.output_data.description}
                    </div>
                  </div>
                </div>
              )}

              {/* Processing Steps */}
              {summary.processing_steps && summary.processing_steps.length > 0 && (
                <div className="bg-purple-50 border-l-4 border-purple-500 p-4 rounded">
                  <h3 className="text-lg font-bold text-purple-800 mb-3">⚡ 処理フロー</h3>
                  <ol className="space-y-2">
                    {summary.processing_steps.map((step, index) => (
                      <li key={index} className="flex gap-3 text-gray-700">
                        <span className="flex-shrink-0 w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {index + 1}
                        </span>
                        <span className="flex-1">{step}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Approach */}
              <div>
                <h3 className="text-lg font-semibold text-gray-700 mb-2">🔧 アプローチ</h3>
                <p className="text-gray-600">{summary.approach}</p>
              </div>

              {/* Key Techniques */}
              {summary.key_techniques && summary.key_techniques.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">⚙️ 主要な手法</h3>
                  <ul className="space-y-2">
                    {summary.key_techniques.map((tech, index) => (
                      <li key={index} className="text-gray-600">
                        <span className="font-medium text-gray-700">{tech.name}</span>
                        <br />
                        <span className="text-sm text-gray-500 ml-4">→ {tech.explanation}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Models Used */}
              {summary.models_used && summary.models_used.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">🤖 使用モデル</h3>
                  <ul className="space-y-2">
                    {summary.models_used.map((model, index) => (
                      <li key={index} className="text-gray-600">
                        <span className="font-medium text-gray-700">{model.name}</span>
                        <br />
                        <span className="text-sm text-gray-500 ml-4">→ {model.explanation}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Glossary */}
              {summary.glossary && summary.glossary.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">📚 用語集</h3>
                  <div className="space-y-2">
                    {summary.glossary.map((item, index) => (
                      <div key={index} className="bg-gray-50 p-3 rounded">
                        <span className="font-medium text-gray-700">{item.term}</span>
                        <p className="text-sm text-gray-600 mt-1">→ {item.explanation}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Results */}
              {summary.results && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">📈 結果</h3>
                  <p className="text-gray-600">{summary.results}</p>
                </div>
              )}

              {/* Useful For */}
              <div>
                <h3 className="text-lg font-semibold text-gray-700 mb-2">👥 対象者</h3>
                <p className="text-gray-600">{summary.useful_for}</p>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              要約を生成するには「要約を生成」ボタンをクリックしてください
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
