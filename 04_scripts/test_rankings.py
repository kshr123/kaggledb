#!/usr/bin/env python3
"""
Test the rankings scraper with 1 page
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from fetch_kaggle_rankings import fetch_competition_rankings

result = fetch_competition_rankings(max_pages=1)

print(f'\n✅ テスト結果:')
print(f'  Grandmasters: {len(result["grandmasters"])}名')
print(f'  Masters: {len(result["masters"])}名')

if result['grandmasters']:
    print(f'  GM例: {result["grandmasters"][:3]}')
if result['masters']:
    print(f'  Master例: {result["masters"][:3]}')
