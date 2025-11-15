import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'KaggleDB - Kaggle Competition Knowledge Base',
  description: 'Track and analyze Kaggle competitions, discussions, and solutions',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <h1 className="text-2xl font-bold text-gray-900">
              🏆 KaggleDB
            </h1>
            <p className="text-sm text-gray-600">Kaggle Competition Knowledge Base</p>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  )
}
