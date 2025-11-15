# 10. フロントエンド詳細仕様

## 10.1 ホーム画面（`/`）

**コンポーネント構成**
```tsx
app/page.tsx
├─ <Dashboard />                      // ダッシュボード（統計情報）
│  ├─ <SummaryCards />                // サマリー統計（全コンペ・開催中・新規）
│  ├─ <NewCompetitionsSection />      // 新規コンペ（30日以内）
│  │  └─ <CompetitionCard />          // カード表示
│  ├─ <ActiveCompetitionsSection />   // 開催中コンペ
│  │  └─ <CompetitionCard />          // カード表示
│  ├─ <RecommendationsSection />      // レコメンド
│  │  └─ <RecommendationCard />       // カード表示（類似度表示）
│  ├─ <YearlyChart />                 // 年別推移グラフ
│  └─ <DataTypeChart />               // データ種別グラフ
│
├─ <SearchBar />                      // 検索バー（高度な検索ボタン付き）
├─ <FilterPanel />                    // サイドバーフィルターUI（アコーディオン）
│  ├─ <TagCategoryFilter category="data_type" />
│  ├─ <TagCategoryFilter category="task_type" />
│  ├─ <TagCategoryFilter category="model_type" />
│  ├─ <TagCategoryFilter category="solution_method" />
│  ├─ <TagCategoryFilter category="competition_feature" />
│  └─ <TagCategoryFilter category="domain" />
│
├─ <ViewModeToggle />                 // 表示切り替え（テーブル/カード）
├─ <SelectedTagsDisplay />            // 選択中タグ表示
│
├─ <CompetitionTable /> または <CompetitionCardGrid />  // 表示モードに応じて切替
│  └─ <CompetitionRow /> または <CompetitionCard />
│
└─ <Pagination />                     // ページネーション
```

**状態管理**
```typescript
const [filters, setFilters] = useState({
  search: '',
  status: 'all',
  data_types: [],           // データ種別
  task_types: [],           // タスク種別（新規）
  model_types: [],          // モデル種別（新規）
  solution_methods: [],     // 解法種別（新規）
  competition_features: [], // コンペ特徴（新規）
  domains: [],              // ドメイン
  metric: [],
  solution_status: 'all',
  year: 'all'
});

const [sort, setSort] = useState({
  by: 'end_date',
  order: 'desc'
});

const [page, setPage] = useState(1);
const [viewMode, setViewMode] = useState<'table' | 'card'>('table'); // 表示モード

// ダッシュボード統計データ
const { data: summaryData } = useSWR('/api/stats/summary', fetcher);
const { data: yearlyData } = useSWR('/api/stats/yearly', fetcher);
const { data: dataTypesData } = useSWR('/api/stats/data-types', fetcher);

// 新規コンペ（30日以内）
const { data: newComps } = useSWR('/api/competitions/new?days=30&limit=5', fetcher);

// 開催中コンペ
const { data: activeComps } = useSWR('/api/competitions/active?limit=12', fetcher);

// レコメンド
const { data: recommendations } = useSWR('/api/recommendations?limit=6&strategy=mixed', fetcher);

// タグ一覧（フィルタパネル用）
const { data: tagsData } = useSWR('/api/tags?group_by_category=true', fetcher);

// コンペ一覧データ
const { data, error, isLoading } = useSWR(
  `/api/competitions?${buildQueryString(filters, sort, page, viewMode)}`,
  fetcher
);
```

**主要機能**
1. **ダッシュボード**: 統計情報の可視化、新規/開催中コンペ、レコメンド表示
2. **検索**: リアルタイム検索（debounce 300ms）+ 高度な検索モーダル
3. **フィルタ**:
   - カテゴリ別タグフィルタ（アコーディオン）
   - 同一カテゴリ内：OR条件
   - 異なるカテゴリ間：AND条件
   - 選択即反映（ページリロードなし）
4. **表示切り替え**: テーブル ⇄ カード表示
5. **ソート**: カラムヘッダークリックでソート切替（テーブルモード）
6. **ページネーション**: ページ番号クリック、前へ/次へ
7. **グラフインタラクション**: クリックでフィルタ適用
8. **レコメンド**: 閲覧履歴とタグ類似度ベース

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

## 10.3 新規コンポーネント詳細

### NewCompetitionsSection.tsx
```tsx
// 新規コンペセクション（30日以内）
<NewCompetitionsSection>
  <SectionHeader
    title="🆕 新規コンペ"
    subtitle="最近30日以内に追加"
    action={<Link href="/competitions/new">すべて見る →</Link>}
  />
  <CompetitionCardGrid>
    {newComps.map(comp => (
      <CompetitionCard
        key={comp.id}
        competition={comp}
        showBadge="new"
        daysLabel={`${comp.days_since_added}日前に追加`}
      />
    ))}
  </CompetitionCardGrid>
</NewCompetitionsSection>
```

### RecommendationsSection.tsx
```tsx
// レコメンドセクション
<RecommendationsSection>
  <SectionHeader
    title="🎯 あなたへのレコメンド"
    subtitle="閲覧履歴に基づく類似コンペ"
  />
  <RecommendationCardGrid>
    {recommendations.map(rec => (
      <RecommendationCard
        key={rec.id}
        competition={rec}
        similarityScore={rec.similarity_score}
        reason={rec.reason}
        commonTags={rec.common_tags}
      />
    ))}
  </RecommendationCardGrid>
</RecommendationsSection>
```

### TagCategoryFilter.tsx
```tsx
// カテゴリ別タグフィルタ（アコーディオン）
<TagCategoryFilter category="model_type">
  <AccordionHeader>
    モデル種別 ({selectedCount})
  </AccordionHeader>
  <AccordionBody>
    {tagsData.model_type.map(tag => (
      <Checkbox
        key={tag.id}
        label={tag.name}
        checked={filters.model_types.includes(tag.name)}
        onChange={(checked) => handleTagToggle('model_types', tag.name, checked)}
      />
    ))}
  </AccordionBody>
</TagCategoryFilter>
```

### ViewModeToggle.tsx
```tsx
// 表示切り替えボタン
<ViewModeToggle>
  <ToggleButton
    active={viewMode === 'table'}
    onClick={() => setViewMode('table')}
    icon={<TableIcon />}
    label="テーブル表示"
  />
  <ToggleButton
    active={viewMode === 'card'}
    onClick={() => setViewMode('card')}
    icon={<GridIcon />}
    label="カード表示"
  />
</ViewModeToggle>
```

### SelectedTagsDisplay.tsx
```tsx
// 選択中タグの表示（削除可能）
<SelectedTagsDisplay>
  {Object.entries(filters).flatMap(([category, tags]) =>
    tags.map(tag => (
      <TagChip
        key={`${category}-${tag}`}
        label={tag}
        onRemove={() => handleTagRemove(category, tag)}
      />
    ))
  )}
  {hasSelectedTags && (
    <Button variant="text" onClick={clearAllFilters}>
      すべてクリア
    </Button>
  )}
</SelectedTagsDisplay>
```

## 10.4 共通コンポーネント

### ダッシュボード関連

**SummaryCards.tsx**
```tsx
// サマリー統計カード（拡張）
<SummaryCards>
  <StatCard
    title="総コンペ数"
    value={summaryData.total_competitions}
    icon={<TrophyIcon />}
  />
  <StatCard
    title="開催中"
    value={summaryData.active_competitions}
    icon={<FireIcon />}
    accent="primary"
  />
  <StatCard
    title="今月追加"
    value={newComps.total}
    icon={<NewIcon />}
    accent="success"
  />
</SummaryCards>
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
