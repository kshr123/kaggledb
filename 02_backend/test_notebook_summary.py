"""
ノートブック要約機能のテストスクリプト
"""
import sys
sys.path.insert(0, '/Users/kotaro/Desktop/dev/kaggledb/02_backend')

from app.services.scraper_service import get_scraper_service
from app.services.llm_service import get_llm_service
import json


def test_notebook_summary():
    """ノートブック要約をテスト"""

    # テスト用のノートブックURL
    notebook_url = "https://www.kaggle.com/code/vanguarde/h-m-eda-first-look"
    notebook_title = "H&M EDA FIRST LOOK"

    print(f"=== ノートブック要約テスト ===")
    print(f"URL: {notebook_url}")
    print(f"タイトル: {notebook_title}\n")

    # 1. スクレイパーでノートブックのコンテンツを取得
    print("📥 ノートブックのコンテンツを取得中...")
    scraper = get_scraper_service()

    # ノートブックの詳細を取得（ディスカッション詳細取得メソッドを流用）
    detail = scraper.get_discussion_detail(notebook_url)

    if not detail or not detail.get('content'):
        print("❌ ノートブックのコンテンツ取得に失敗しました")
        return

    content = detail['content']
    print(f"✅ コンテンツ取得完了（{len(content)}文字）\n")

    # コンテンツの一部を表示
    print("--- コンテンツの最初の500文字 ---")
    print(content[:500])
    print("...\n")

    # 2. LLMで要約を生成
    print("🤖 LLMで要約を生成中...")
    llm = get_llm_service()

    summary_json = llm.summarize_notebook(content, notebook_title)

    if not summary_json or summary_json == "{}":
        print("❌ 要約生成に失敗しました")
        return

    # JSONをパース
    summary = json.loads(summary_json)

    # 3. 結果を表示
    print("\n" + "="*60)
    print("📊 生成された要約")
    print("="*60 + "\n")

    print(f"🎯 目的:")
    print(f"  {summary.get('purpose', 'N/A')}\n")

    print(f"📁 データ概要:")
    print(f"  {summary.get('data_overview', 'N/A')}\n")

    print(f"🔧 アプローチ:")
    print(f"  {summary.get('approach', 'N/A')}\n")

    print(f"⚙️ 主要な手法:")
    for i, technique in enumerate(summary.get('key_techniques', []), 1):
        if isinstance(technique, dict):
            print(f"  {i}. {technique.get('name', 'N/A')}")
            print(f"     → {technique.get('explanation', 'N/A')}")
        else:
            print(f"  {i}. {technique}")
    print()

    print(f"🤖 使用モデル:")
    models = summary.get('models_used', [])
    if models:
        for i, model in enumerate(models, 1):
            if isinstance(model, dict):
                print(f"  {i}. {model.get('name', 'N/A')}")
                print(f"     → {model.get('explanation', 'N/A')}")
            else:
                print(f"  {i}. {model}")
    else:
        print("  （モデルは使用されていません）")
    print()

    print(f"📚 用語集:")
    glossary = summary.get('glossary', [])
    if glossary:
        for i, term in enumerate(glossary, 1):
            if isinstance(term, dict):
                print(f"  {i}. {term.get('term', 'N/A')}")
                print(f"     → {term.get('explanation', 'N/A')}")
            else:
                print(f"  {i}. {term}")
    else:
        print("  （用語集なし）")
    print()

    print(f"📈 結果:")
    results = summary.get('results', '')
    print(f"  {results if results else '（結果の記載なし）'}\n")

    print(f"👥 対象者:")
    print(f"  {summary.get('useful_for', 'N/A')}\n")

    print("="*60)
    print("✅ テスト完了")
    print("="*60)

    # JSONを保存
    output_file = "/Users/kotaro/Desktop/dev/kaggledb/02_backend/test_notebook_summary_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n💾 結果を保存しました: {output_file}")


if __name__ == "__main__":
    test_notebook_summary()
