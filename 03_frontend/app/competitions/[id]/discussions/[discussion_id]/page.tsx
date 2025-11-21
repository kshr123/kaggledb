'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { Discussion } from '@/types/competition'

export default function DiscussionDetailPage() {
  const params = useParams()
  const router = useRouter()
  const competitionId = params.id as string
  const discussionId = params.discussion_id as string

  const [discussion, setDiscussion] = useState<Discussion | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isFetching, setIsFetching] = useState(false)
  const [links, setLinks] = useState<{ notebooks: string[], github: string[], other: string[] } | null>(null)

  useEffect(() => {
    async function fetchDiscussion() {
      try {
        const response = await fetch(`http://localhost:8000/api/discussions/${discussionId}`)
        if (!response.ok) {
          throw new Error('ディスカッション情報の取得に失敗しました')
        }
        const data = await response.json()
        setDiscussion(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : '予期しないエラーが発生しました')
      } finally {
        setLoading(false)
      }
    }

    fetchDiscussion()
  }, [discussionId])

  const handleFetchContent = async () => {
    setIsFetching(true)
    try {
      const res = await fetch(`http://localhost:8000/api/discussions/${discussionId}/fetch`, {
        method: 'POST',
      })

      if (!res.ok) {
        throw new Error('ディスカッション詳細の取得に失敗しました')
      }

      const result = await res.json()
      setDiscussion(result.discussion)
      if (result.links) {
        setLinks(result.links)
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'エラーが発生しました')
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

  if (error || !discussion) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100 flex items-center justify-center">
        <div className="text-slate-700 text-lg font-medium">{error || 'ディスカッションが見つかりません'}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100 py-8">
      <div className="max-w-5xl mx-auto px-6">
        {/* パンくずリスト */}
        <nav className="mb-6 flex items-center gap-2 text-sm text-slate-600">
          <Link href="/" className="hover:text-blue-600 transition-colors">
            ホーム
          </Link>
          <span>/</span>
          <Link href={`/competitions/${competitionId}`} className="hover:text-blue-600 transition-colors">
            コンペティション
          </Link>
          <span>/</span>
          <Link href={`/competitions/${competitionId}?tab=discussion`} className="hover:text-blue-600 transition-colors">
            ディスカッション一覧
          </Link>
          <span>/</span>
          <span className="text-slate-900 font-medium">詳細</span>
        </nav>

        {/* ヘッダー */}
        <div className="bg-white/90 backdrop-blur-sm rounded-xl border border-slate-200 shadow-sm p-8 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                {discussion.is_pinned && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                    📌 ピン留め
                  </span>
                )}
                {discussion.author_tier && (
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    discussion.author_tier === 'Grandmaster' ? 'bg-yellow-100 text-yellow-700' :
                    discussion.author_tier === 'Master' ? 'bg-purple-100 text-purple-700' :
                    'bg-slate-100 text-slate-700'
                  }`}>
                    🏆 {discussion.author_tier}
                  </span>
                )}
              </div>

              <h1 className="text-3xl font-bold text-slate-900 mb-4">
                {discussion.title}
              </h1>

              <div className="flex items-center gap-6 text-sm text-slate-600">
                {discussion.author && (
                  <div className="flex items-center gap-2">
                    {discussion.tier_color && (
                      <svg width="16" height="16" viewBox="0 0 16 16">
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
                      'text-slate-700'
                    }`}>
                      👤 {discussion.author}
                    </span>
                  </div>
                )}
                <span className="flex items-center gap-1.5">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                  </svg>
                  {discussion.vote_count} 票
                </span>
                <span className="flex items-center gap-1.5">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  {discussion.comment_count} コメント
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleFetchContent}
                disabled={isFetching}
                className={`inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                  discussion.content
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
                    <span>{discussion.content ? '要約を再生成' : '詳細を取得'}</span>
                  </>
                )}
              </button>

              <a
                href={discussion.url}
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

        {/* コンテンツ */}
        <div className="bg-white/90 backdrop-blur-sm rounded-xl border border-slate-200 shadow-sm p-8">
          {discussion.content ? (
            <div className="space-y-6">
              {/* 構造化要約（存在する場合） */}
              {discussion.summary && (() => {
                try {
                  const summaryData = JSON.parse(discussion.summary)
                  return (
                    <div className="space-y-4">
                      {/* 概要 */}
                      {summaryData.overview && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-5">
                          <h2 className="text-md font-semibold text-blue-900 mb-2">📝 概要</h2>
                          <p className="text-slate-700 leading-relaxed">{summaryData.overview}</p>
                        </div>
                      )}

                      {/* 主なトピック */}
                      {summaryData.main_topic && (
                        <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                          <h3 className="text-md font-semibold text-slate-900 mb-2">🎯 主なトピック</h3>
                          <p className="text-slate-700">{summaryData.main_topic}</p>
                        </div>
                      )}

                      {/* 重要ポイント */}
                      {summaryData.key_points && summaryData.key_points.length > 0 && (
                        <div className="bg-green-50 border border-green-200 rounded-lg p-5">
                          <h3 className="text-md font-semibold text-green-900 mb-3">✨ 重要ポイント</h3>
                          <ul className="space-y-2">
                            {summaryData.key_points.map((point: string, i: number) => (
                              <li key={i} className="flex items-start gap-2 text-slate-700">
                                <span className="text-green-600 mt-1">•</span>
                                <span>{point}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* 技術的な詳細 */}
                      {summaryData.technical_details && (
                        <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                          <h3 className="text-md font-semibold text-slate-900 mb-3">🔧 技術的な詳細</h3>
                          <p className="text-slate-700 leading-relaxed">{summaryData.technical_details}</p>
                        </div>
                      )}

                      {/* 専門用語集 */}
                      {summaryData.glossary && summaryData.glossary.length > 0 && (
                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-5">
                          <h3 className="text-md font-semibold text-purple-900 mb-4">📖 専門用語集</h3>
                          <div className="space-y-3">
                            {summaryData.glossary.map((item: { term: string, explanation: string }, i: number) => (
                              <div key={i} className="bg-white rounded p-3 border border-slate-200">
                                <div className="font-semibold text-purple-700 mb-1">{item.term}</div>
                                <div className="text-slate-600 text-sm">{item.explanation}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* アプローチ・手法 */}
                      {summaryData.approaches && summaryData.approaches.length > 0 && (
                        <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                          <h3 className="text-md font-semibold text-slate-900 mb-3">💡 提案されているアプローチ</h3>
                          <ul className="space-y-2">
                            {summaryData.approaches.map((approach: string, i: number) => (
                              <li key={i} className="flex items-start gap-2 text-slate-700">
                                <span className="text-slate-600 mt-1">→</span>
                                <span>{approach}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* コード例 */}
                      {summaryData.code_examples && (
                        <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                          <h3 className="text-md font-semibold text-slate-900 mb-3">💻 コード例</h3>
                          <p className="text-slate-700 leading-relaxed">{summaryData.code_examples}</p>
                        </div>
                      )}

                      {/* 結果・結論 */}
                      {summaryData.results && (
                        <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                          <h3 className="text-md font-semibold text-slate-900 mb-3">✅ 結果・結論</h3>
                          <p className="text-slate-700 leading-relaxed">{summaryData.results}</p>
                        </div>
                      )}

                      {/* 関連リンク・リソース */}
                      {summaryData.related_links && (
                        <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                          <h3 className="text-md font-semibold text-slate-900 mb-2">🔗 関連リソース</h3>
                          <p className="text-slate-700">{summaryData.related_links}</p>
                        </div>
                      )}
                    </div>
                  )
                } catch {
                  // JSON パースに失敗した場合は従来の表示
                  return (
                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                      <h2 className="text-md font-semibold text-slate-900 mb-3">📝 要約</h2>
                      <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
                        {discussion.summary}
                      </p>
                    </div>
                  )
                }
              })()}

              {/* 和訳された詳細 */}
              {discussion.content && (
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                  <h2 className="text-md font-semibold text-slate-900 mb-3">📄 詳細（和訳）</h2>
                  <div className="text-slate-700 leading-relaxed whitespace-pre-wrap">
                    {discussion.content}
                  </div>
                </div>
              )}

              {/* リンク（存在する場合） */}
              {links && (links.notebooks.length > 0 || links.github.length > 0 || links.other.length > 0) && (
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                  <h3 className="text-md font-semibold text-slate-900 mb-4">🔗 本文内のリンク</h3>
                  <div className="space-y-3">
                    {links.notebooks.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-slate-700 mb-2">📓 Kaggle Notebooks</div>
                        <ul className="space-y-1">
                          {links.notebooks.map((url, i) => (
                            <li key={i}>
                              <a href={url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:text-blue-800 hover:underline break-all">
                                {url}
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {links.github.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-slate-700 mb-2">💾 GitHub</div>
                        <ul className="space-y-1">
                          {links.github.map((url, i) => (
                            <li key={i}>
                              <a href={url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:text-blue-800 hover:underline break-all">
                                {url}
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {links.other.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-slate-700 mb-2">🌐 その他のリンク</div>
                        <ul className="space-y-1">
                          {links.other.map((url, i) => (
                            <li key={i}>
                              <a href={url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:text-blue-800 hover:underline break-all">
                                {url}
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <svg className="w-16 h-16 mx-auto text-slate-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-slate-500 text-lg mb-4">ディスカッション詳細がまだ取得されていません</p>
              <p className="text-slate-400 text-sm">上の「詳細を取得」ボタンをクリックしてください</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
