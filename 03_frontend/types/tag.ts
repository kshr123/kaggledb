/**
 * タグ関連の型定義
 */

export interface Tag {
  id: number;
  name: string;
  category: string;
  display_order: number;
}

export interface TagsByCategory {
  [category: string]: Tag[];
}
