"""
2020年以降のランクに関わるKaggleコンペティション情報を取得してDBに保存
ランクに関わらないコンペや2020年より前のコンペは削除
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "02_backend"))

from kaggle.api.kaggle_api_extended import KaggleApi

def main():
    # Kaggle API初期化
    api = KaggleApi()
    api.authenticate()

    # データベース接続
    db_path = project_root / "02_backend" / "data" / "kaggle_competitions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 既存のコンペを全て削除
    print('Clearing existing competitions...')
    cursor.execute('DELETE FROM competitions')
    cursor.execute('DELETE FROM discussions')
    cursor.execute('DELETE FROM solutions')
    conn.commit()
    print('✅ Cleared all existing data')

    # ランクに関わるコンペを取得
    # カテゴリ: featured (ランクに関わる), research (一部), getting-started (練習用、除外)
    categories = ['featured', 'research']

    all_competitions = []
    for category in categories:
        print(f'\nFetching {category} competitions...')
        page = 1
        max_pages = 10  # 最大10ページまで取得

        while page <= max_pages:
            try:
                comps = api.competitions_list(category=category, page=page)
                if not comps:
                    break

                all_competitions.extend(comps)
                print(f'Page {page}: Found {len(comps)} competitions')
                page += 1
            except Exception as e:
                print(f'Error fetching {category} page {page}: {e}')
                break

        print(f'Total {category} competitions: {sum(1 for c in all_competitions if hasattr(c, "category") or True)}')

    count = 0
    for comp in all_competitions:
        # 2020年以降のコンペのみ
        comp_year = None
        if comp.deadline:
            comp_year = comp.deadline.year
        elif hasattr(comp, 'enabledDate') and comp.enabledDate:
            comp_year = comp.enabledDate.year

        if comp_year and comp_year >= 2020:
            try:
                # 属性が存在するか確認してから使用
                metric = getattr(comp, 'evaluationMetric', None) or getattr(comp, 'metric', None) or ''
                description = getattr(comp, 'description', '') or ''

                cursor.execute('''
                    INSERT OR REPLACE INTO competitions
                    (id, title, url, start_date, end_date, status, metric, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (
                    comp.ref,
                    comp.title,
                    f'https://www.kaggle.com/competitions/{comp.ref}',
                    None,  # start_dateは後で取得
                    comp.deadline.isoformat() if comp.deadline else None,
                    'active' if not comp.deadline or comp.deadline > datetime.now() else 'completed',
                    metric,
                    description
                ))
                count += 1
                print(f'Added: {comp.title} (deadline: {comp.deadline.strftime("%Y-%m-%d")})')
            except Exception as e:
                print(f'Error adding {comp.ref}: {e}')

    conn.commit()
    conn.close()
    print(f'\n✅ Total added/updated: {count} competitions')

if __name__ == "__main__":
    main()
