"""
既存のディスカッションタイトルをクリーニングするスクリプト
"""
import sqlite3
from pathlib import Path

# configから正しいデータベースパスを取得
from app.config import DATABASE_PATH


def clean_title(title: str, author: str = None) -> str:
    """
    タイトルから投稿者名や投稿日情報を削除

    Args:
        title: 元のタイトル
        author: 投稿者名（オプション）

    Returns:
        クリーニングされたタイトル
    """
    if not title:
        return title

    # " · Last comment..." 以降を削除
    if ' · Last comment' in title:
        title = title.split(' · Last comment')[0]

    # 末尾の作者名を削除（作者名が取得できている場合）
    if author and title.endswith(author):
        title = title[:-len(author)].strip()

    # その他のクリーニング
    title = title.strip()

    return title


def main():
    """既存のディスカッションタイトルをクリーニング"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 全ディスカッションを取得
    cursor.execute("SELECT id, title, author FROM discussions")
    discussions = cursor.fetchall()

    updated_count = 0

    for disc in discussions:
        disc_id = disc['id']
        old_title = disc['title']
        author = disc['author']

        # タイトルをクリーニング
        new_title = clean_title(old_title, author)

        # タイトルが変更された場合のみ更新
        if new_title != old_title:
            cursor.execute(
                "UPDATE discussions SET title = ? WHERE id = ?",
                (new_title, disc_id)
            )
            updated_count += 1
            print(f"Updated: {old_title[:50]}... → {new_title[:50]}...")

    conn.commit()
    conn.close()

    print(f"\n✅ 完了: {updated_count}件のディスカッションタイトルを更新しました")


if __name__ == "__main__":
    main()
