#!/usr/bin/env python3
"""
既存の要約キャッシュをクリアして、新しい要約形式で再生成できるようにするスクリプト
"""

import sys
import sqlite3
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent / "02_backend"
sys.path.insert(0, str(project_root))

from app.config import DATABASE_PATH


def get_connection():
    """データベース接続を取得"""
    return sqlite3.connect(DATABASE_PATH)


def clear_competition_summaries():
    """コンペティションの要約をクリア"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE competitions SET summary = NULL WHERE summary IS NOT NULL")
        conn.commit()
        count = cursor.rowcount
        print(f"✅ {count}件のコンペティション要約をクリアしました")
        return count
    except Exception as e:
        conn.rollback()
        print(f"❌ エラー: {e}")
        return 0
    finally:
        conn.close()


def clear_discussion_summaries():
    """ディスカッションの要約をクリア"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE discussions SET summary = NULL WHERE summary IS NOT NULL")
        conn.commit()
        count = cursor.rowcount
        print(f"✅ {count}件のディスカッション要約をクリアしました")
        return count
    except Exception as e:
        conn.rollback()
        print(f"❌ エラー: {e}")
        return 0
    finally:
        conn.close()


def clear_solution_summaries():
    """解法の要約をクリア"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE solutions SET summary = NULL WHERE summary IS NOT NULL")
        conn.commit()
        count = cursor.rowcount
        print(f"✅ {count}件の解法要約をクリアしました")
        return count
    except Exception as e:
        conn.rollback()
        print(f"❌ エラー: {e}")
        return 0
    finally:
        conn.close()


def main():
    print("🗑️  要約キャッシュをクリアします...\n")

    comp_count = clear_competition_summaries()
    disc_count = clear_discussion_summaries()
    sol_count = clear_solution_summaries()

    total = comp_count + disc_count + sol_count

    print(f"\n✨ 合計 {total}件の要約をクリアしました")
    print("\n📝 新しい要約形式で再生成するには：")
    print("   - コンペ詳細ページで「要約を生成」ボタンをクリック")
    print("   - ノートブック詳細ページで「要約を生成」ボタンをクリック")


if __name__ == "__main__":
    main()
