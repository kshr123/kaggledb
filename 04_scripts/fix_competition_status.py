#!/usr/bin/env python3
"""
すべてのコンペのstatusをend_dateを基に修正
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from datetime import datetime, date
from app.config import DATABASE_PATH


def main():
    print("=" * 60)
    print("コンペのstatus修正")
    print("=" * 60)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # end_dateがあるコンペを取得
    cursor.execute("""
        SELECT id, end_date, status
        FROM competitions
        WHERE end_date IS NOT NULL AND end_date != ''
    """)

    competitions = cursor.fetchall()
    print(f"\n対象: {len(competitions)}件のコンペ\n")

    updated_count = 0
    today = date.today()

    for comp_id, end_date_str, current_status in competitions:
        try:
            end_date_obj = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            # 正しいstatusを判定
            correct_status = 'completed' if end_date_obj < today else 'active'

            # 現在のstatusと異なる場合は更新
            if current_status != correct_status:
                cursor.execute("""
                    UPDATE competitions
                    SET status = ?
                    WHERE id = ?
                """, (correct_status, comp_id))

                print(f"✅ {comp_id}: {current_status} → {correct_status} (終了: {end_date_str})")
                updated_count += 1

        except Exception as e:
            print(f"❌ {comp_id}: エラー - {e}")

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print(f"完了: {updated_count}件のstatusを修正しました")
    print("=" * 60)


if __name__ == "__main__":
    main()
