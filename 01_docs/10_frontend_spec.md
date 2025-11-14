# 10. フロントエンド詳細仕様

## 10.1 ホーム画面（`/`）

**コンポーネント構成**
```tsx
app/page.tsx
├─ <Dashboard />                      // ダッシュボード（統計情報）
│  ├─ <SummaryCards />                // サマリー統計（全コンペ・開催中）
│  ├─ <ActiveCompetitionsCarousel />  // 開催中コンペカード
│  │  └─ <ActiveCompetitionCard />    // 各カード
│  ├─ <YearlyChart />                 // 年別推移グラフ
│  └─ <DataTypeChart />               // データ種別グラフ
├─ <SearchBar />                      // 検索バー
├─ <FilterPanel />                    // フィルターUI
├─ <CompetitionTable />               // コンペ一覧テーブル
│  └─ <CompetitionRow />              // 各行
└─ <Pagination />                     // ページネーション
```

**状態管理**
```typescript
const [filters, setFilters] = useState({
  search: '',
  status: 'all',
  tags: [],
  data_types: [],
  metric: [],
  solution_status: 'all',
  year: 'all'
});

const [sort, setSort] = useState({
  by: 'end_date',
  order: 'desc'
});

const [page, setPage] = useState(1);

// ダッシュボード統計データ
const { data: summaryData } = useSWR('/api/stats/summary', fetcher);
const { data: yearlyData } = useSWR('/api/stats/yearly', fetcher);
const { data: dataTypesData } = useSWR('/api/stats/data-types', fetcher);
const { data: activeComps } = useSWR('/api/competitions/active?limit=12', fetcher);

// コンペ一覧データ
const { data, error, isLoading } = useSWR(
  `/api/competitions?${buildQueryString(filters, sort, page)}`,
  fetcher
);
```

**主要機能**
1. **ダッシュボード**: 統計情報の可視化、開催中コンペのカード表示
2. **検索**: リアルタイム検索（debounce 300ms）
3. **フィルタ**: 選択即反映（ページリロードなし）
4. **ソート**: カラムヘッダークリックでソート切替
5. **ページネーション**: ページ番号クリック、前へ/次へ
6. **グラフインタラクション**: クリックでフィルタ適用

## 10.2 コンペ詳細画面（`/competitions/[id]`）

**コンポーネント構成**
```tsx
app/competitions/[id]/page.tsx
├─ <CompetitionHeader />        // タイトル、リンク、ステータス
├─ <CompetitionBasicInfo />     // 基本情報
├─ <TagEditor />                // タグ編集（編集ボタン付き）
├─ <CompetitionSummary />       // 概要（日本語）
├─ <CompetitionDescription />   // 説明文（英語、折りたたみ）
│
├─ <DiscussionSection />        // Phase 2
│  ├─ <AddDiscussionButton />
│  └─ <DiscussionTable />
│
└─ <SolutionSection />          // Phase 3
   ├─ <AddSolutionButton />
   ├─ <SolutionTable />
   └─ <SolutionAnalysis />
```

**データ取得**
```typescript
const { data: competition } = useSWR(
  `/api/competitions/${id}`,
  fetcher
);
```

## 10.3 共通コンポーネント

### ダッシュボード関連

**SummaryCards.tsx**
```tsx
// サマリー統計カード
<SummaryCards 
  totalCompetitions={452}
  activeCompetitions={12}
/>
```

**ActiveCompetitionCard.tsx**
```tsx
// 開催中コンペのカード
<ActiveCompetitionCard
  id="housing-prices-2025"
  title="Housing Prices Prediction 2025"
  daysRemaining={15}
  summary="住宅価格を予測するコンペ。79個の特徴量を使った回帰タスク。初心者にも取り組みやすい課題。"
  tags={["テーブルデータ", "回帰", "特徴量エンジニアリング"]}
  metric="RMSE"
  url="https://www.kaggle.com/c/housing-prices-2025"
/>
```

**YearlyChart.tsx**
```tsx
// 年別コンペ数推移グラフ（Recharts使用）
<YearlyChart 
  data={yearlyData}
  onBarClick={(year) => handleFilterByYear(year)}
/>
```

**DataTypeChart.tsx**
```tsx
// データ種別分布グラフ（横棒グラフ）
<DataTypeChart 
  data={dataTypesData}
  onBarClick={(type) => handleFilterByDataType(type)}
/>
```

### 基本コンポーネント

**TagBadge.tsx**
```tsx
// タグのバッジ表示
<TagBadge 
  tag="テーブルデータ" 
  category="データ系"
  variant="blue"  // カテゴリごとに色分け
/>
```

**StatusBadge.tsx**
```tsx
// ステータスバッジ
<StatusBadge status="active" />  // 🟢 開催中
<StatusBadge status="completed" />  // 🔴 終了済み
```

**LoadingSpinner.tsx**
```tsx
// ローディング表示
<LoadingSpinner size="large" />
```

**ErrorMessage.tsx**
```tsx
// エラー表示
<ErrorMessage message="データの取得に失敗しました" />
```

## 10.4 型定義（types/competition.ts）

```typescript
export interface Competition {
  id: string;
  title: string;
  url: string;
  start_date: string;
  end_date: string;
  status: 'active' | 'completed';
  metric: string;
  description?: string;
  summary: string;
  tags: string[];
  data_types: string[];
  domain: string;
  discussion_count: number;
  solution_status: '未着手' | 'ディスカッションのみ' | '解法分析済み';
  created_at: string;
  updated_at: string;
}

export interface CompetitionListResponse {
  items: Competition[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface Discussion {
  id: number;
  competition_id: string;
  title: string;
  url: string;
  author: string;
  author_tier: string;
  author_medals: {
    gold: number;
    silver: number;
    bronze: number;
  };
  votes: number;
  comment_count: number;
  category: string;
  summary: string;
  key_points: string[];
  posted_at: string;
}

export interface Tag {
  id: number;
  name: string;
  category: '課題系' | 'データ系' | '手法系' | 'ドメイン系';
  display_order: number;
}

export interface SummaryStats {
  total_competitions: number;
  active_competitions: number;
  completed_competitions: number;
}

export interface YearlyData {
  year: number;
  count: number;
}

export interface DataTypeData {
  type: 'tabular' | 'image' | 'text' | 'time-series' | 'audio' | 'video';
  label: string;
  count: number;
}

export interface DataTypeStats {
  data: DataTypeData[];
  multi_modal_count: number;
}

export interface ActiveCompetition {
  id: string;
  title: string;
  url: string;
  end_date: string;
  days_remaining: number;
  status: 'active';
  summary: string;
  metric: string;
  tags: string[];
  data_types: string[];
}
```

## 10.5 APIクライアント（lib/api.ts）

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getCompetitions(params: CompetitionQueryParams) {
  const queryString = new URLSearchParams(params as any).toString();
  const response = await fetch(`${API_URL}/api/competitions?${queryString}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch competitions');
  }
  
  return response.json();
}

export async function getCompetitionById(id: string) {
  const response = await fetch(`${API_URL}/api/competitions/${id}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch competition');
  }
  
  return response.json();
}

export async function updateCompetitionTags(id: string, tags: string[]) {
  const response = await fetch(`${API_URL}/api/competitions/${id}/tags`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ tags }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to update tags');
  }
  
  return response.json();
}

// ダッシュボード統計API
export async function getSummaryStats() {
  const response = await fetch(`${API_URL}/api/stats/summary`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch summary stats');
  }
  
  return response.json();
}

export async function getYearlyStats(startYear: number = 2020) {
  const response = await fetch(`${API_URL}/api/stats/yearly?start_year=${startYear}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch yearly stats');
  }
  
  return response.json();
}

export async function getDataTypeStats() {
  const response = await fetch(`${API_URL}/api/stats/data-types`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch data type stats');
  }
  
  return response.json();
}

export async function getActiveCompetitions(limit: number = 12) {
  const response = await fetch(`${API_URL}/api/competitions/active?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch active competitions');
  }
  
  return response.json();
}

// その他のAPI関数...
```

---

**関連ドキュメント:**
- [機能要件](./02_requirements.md)
- [API設計](./07_api_design.md)
- [技術スタック](./04_tech_stack.md)
