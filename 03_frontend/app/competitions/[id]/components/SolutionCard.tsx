import { Solution } from '@/types/competition'
import Link from 'next/link'

interface SolutionCardProps {
  solution: Solution
  competitionId: string
}

export default function SolutionCard({ solution, competitionId }: SolutionCardProps) {
  return (
    <Link
      href={`/competitions/${competitionId}/solutions/${solution.id}`}
      className="block border border-slate-200 rounded-lg p-4 hover:border-blue-300 hover:bg-blue-50/30 transition-all cursor-pointer"
    >
      <div className="flex items-start gap-3">
        {/* メダルアイコン */}
        {solution.medal && (
          <div className="flex-shrink-0 mt-1">
            {solution.medal === 'gold' && <span className="text-2xl">🥇</span>}
            {solution.medal === 'silver' && <span className="text-2xl">🥈</span>}
            {solution.medal === 'bronze' && <span className="text-2xl">🥉</span>}
          </div>
        )}

        <div className="flex-1 min-w-0">
          {/* タイトル */}
          <div className="mb-2">
            <h3 className="text-blue-600 font-medium hover:text-blue-800 text-lg">
              {solution.title}
            </h3>
          </div>

          {/* メタ情報 */}
          <div className="flex items-center gap-4 text-sm text-slate-600">
            {/* 投稿者 */}
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
                <span>{solution.author}</span>
              </div>
            )}

            {/* 順位 */}
            {solution.rank && (
              <div className="flex items-center gap-1">
                <span className="text-slate-500">#{solution.rank}</span>
              </div>
            )}

            {/* 投票数 */}
            <div className="flex items-center gap-1">
              <span>👍</span>
              <span>{solution.vote_count}</span>
            </div>

            {/* コメント数 */}
            <div className="flex items-center gap-1">
              <span>💬</span>
              <span>{solution.comment_count}</span>
            </div>

            {/* タイプ */}
            <div className="text-xs px-2 py-1 bg-slate-100 rounded">
              {solution.type === 'notebook' ? '📓 Notebook' : '💬 Discussion'}
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}
