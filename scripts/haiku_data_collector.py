#!/usr/bin/env python3
"""
青空文庫俳句収集スクリプト（高精度版）
ルビを使った正確な音数カウントと厳密な俳句判定
"""
import requests
import re
import json
import time
import zipfile
import io
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import pandas as pd
from tqdm import tqdm
import jaconv
import sys

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(str(Path(__file__).parent.parent))


class AdvancedHaikuExtractor:
    """高精度な俳句抽出クラス"""
    
    def __init__(self):
        # 俳句でよく使われる切れ字
        self.kireji = ['や', 'かな', 'けり', 'よ', 'ぞ', 'か', 'らん', 'し', 'つ', 'ぬ', 'へ', 'れ', 'なり']
        
        # 季語の例（一部）
        self.kigo = {
            '春': ['春', '桜', '梅', '鶯', '霞', '陽炎', '蝶', '菜の花', '雛', '彼岸'],
            '夏': ['夏', '蝉', '蛍', '向日葵', '雷', '夕立', '梅雨', '青葉', '汗', '蚊'],
            '秋': ['秋', '月', '紅葉', '虫', '露', '霧', '稲', '萩', '芒', '栗'],
            '冬': ['冬', '雪', '霜', '氷', '寒', '炬燵', '餅', '年の瀬', '枯', '冴']
        }
        
        # 俳句として不適切なパターン
        self.exclude_patterns = [
            re.compile(r'[。、]が[。、]'),  # 「～が～」のような説明文
            re.compile(r'です|ます|である|だった'),  # 敬語・説明調
            re.compile(r'[0-9０-９]{2,}'),  # 数字が多い
            re.compile(r'第[一二三四五六七八九十]+'),  # 章番号など
            re.compile(r'^[「『]'),  # 会話文
            re.compile(r'という|ような|などの'),  # 説明的表現
        ]
        
    def extract_text_with_ruby(self, text: str) -> List[Tuple[str, str]]:
        """テキストとルビのペアを抽出"""
        # ルビ付きテキストのパターン: 漢字《かな》
        ruby_pattern = re.compile(r'([一-龥々]+)《([ぁ-ん]+)》')
        
        result = []
        last_end = 0
        
        for match in ruby_pattern.finditer(text):
            # ルビの前のテキスト
            if last_end < match.start():
                pre_text = text[last_end:match.start()]
                if pre_text:
                    result.append((pre_text, pre_text))
            
            # ルビ付きテキスト
            kanji = match.group(1)
            ruby = match.group(2)
            result.append((kanji, ruby))
            last_end = match.end()
        
        # 最後の部分
        if last_end < len(text):
            post_text = text[last_end:]
            if post_text:
                result.append((post_text, post_text))
        
        return result
    
    def count_mora_with_ruby(self, text_ruby_pairs: List[Tuple[str, str]]) -> int:
        """ルビを使った正確な音数カウント"""
        total_mora = 0
        
        for text, ruby in text_ruby_pairs:
            # ルビがある場合はルビの音数を数える
            if text != ruby:
                clean_ruby = ruby.replace('、', '').replace('。', '').replace(' ', '')
                total_mora += self._count_mora_kana(clean_ruby)
            else:
                # ルビがない場合は通常カウント
                clean_text = text.replace('、', '').replace('。', '').replace(' ', '')
                for char in clean_text:
                    if re.match(r'[ぁ-んァ-ン]', char):
                        total_mora += self._count_mora_kana(char)
                    elif re.match(r'[一-龥々]', char):
                        # 漢字1文字は通常2音として概算
                        total_mora += 2
                    # その他の文字は無視
        
        return total_mora
    
    def _count_mora_kana(self, kana_text: str) -> int:
        """かなテキストの音数を正確にカウント"""
        mora = 0
        i = 0
        
        while i < len(kana_text):
            char = kana_text[i]
            
            # 拗音は前の文字と合わせて1音
            if char in 'ゃゅょャュョ' and i > 0:
                mora += 0  # 既にカウント済み
            # 促音・撥音は1音
            elif char in 'っッんン':
                mora += 1
            # 長音記号
            elif char == 'ー':
                mora += 1
            # 通常のかな
            elif re.match(r'[ぁ-んァ-ン]', char):
                mora += 1
                # 次が拗音かチェック
                if i + 1 < len(kana_text) and kana_text[i + 1] in 'ゃゅょャュョ':
                    i += 1  # 拗音をスキップ
            
            i += 1
        
        return mora
    
    def is_haiku_structure(self, text: str, mora_count: int) -> bool:
        """俳句の構造として適切かチェック"""
        # 基本的な音数チェック（17音前後）
        if not (15 <= mora_count <= 19):
            return False
        
        # 除外パターンチェック
        for pattern in self.exclude_patterns:
            if pattern.search(text):
                return False
        
        # 切れ字チェック（あれば俳句の可能性が高い）
        has_kireji = any(text.endswith(kireji) or f'{kireji}　' in text or f'{kireji} ' in text 
                        for kireji in self.kireji)
        
        # 季語チェック
        has_kigo = any(kigo in text for season_kigo in self.kigo.values() for kigo in season_kigo)
        
        # 句読点の位置チェック（5-7-5の区切りっぽいか）
        parts = re.split(r'[　\s]', text)
        if len(parts) == 3:
            # 3つに分かれていれば俳句の可能性が高い
            return True
        
        # 切れ字か季語があれば俳句として採用
        if has_kireji or has_kigo:
            return True
        
        # その他、俳句らしさのヒューリスティック
        # 文末が名詞・形容詞で終わる（体言止め）
        if re.search(r'[きくしすむる]$', text):
            return True
        
        return mora_count == 17  # 正確に17音なら採用


class AozoraHaikuScraperAdvanced:
    """青空文庫から俳句を収集するクラス（高精度版）"""
    
    def __init__(self, output_dir: str = "data/raw/aozora_advanced"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.extractor = AdvancedHaikuExtractor()
        
        # 正しいURLのリスト（前と同じ）
        self.target_works = [
            {
                "author": "松尾芭蕉",
                "title": "俳句集（芭蕉翁古池真伝）",
                "url": "https://www.aozora.gr.jp/cards/002240/files/61619_ruby_78129.zip"
            },
            {
                "author": "正岡子規",
                "title": "寒山落木 巻一",
                "url": "https://www.aozora.gr.jp/cards/000305/files/1896_ruby.zip"
            },
            {
                "author": "正岡子規",
                "title": "牡丹句録",
                "url": "https://www.aozora.gr.jp/cards/000305/files/59088_ruby_76370.zip"
            },
            {
                "author": "正岡子規",
                "title": "夜寒十句",
                "url": "https://www.aozora.gr.jp/cards/000305/files/42168_ruby_12296.zip"
            },
            {
                "author": "内藤鳴雪",
                "title": "鳴雪句集",
                "url": "https://www.aozora.gr.jp/cards/000684/files/55833_txt_63814.zip"
            },
            {
                "author": "高浜虚子",
                "title": "五百句",
                "url": "https://www.aozora.gr.jp/cards/001310/files/51837_ruby_59424.zip"
            },
            {
                "author": "高浜虚子",
                "title": "五百五十句",
                "url": "https://www.aozora.gr.jp/cards/001310/files/51838_ruby_59505.zip"
            },
            {
                "author": "高浜虚子",
                "title": "六百句",
                "url": "https://www.aozora.gr.jp/cards/001310/files/51840_ruby_59583.zip"
            },
            {
                "author": "高浜虚子",
                "title": "六百五十句",
                "url": "https://www.aozora.gr.jp/cards/001310/files/51841_ruby_77134.zip"
            },
            {
                "author": "高浜虚子",
                "title": "七百五十句",
                "url": "https://www.aozora.gr.jp/cards/001310/files/51839_ruby_77843.zip"
            },
            {
                "author": "高浜虚子",
                "title": "俳句への道",
                "url": "https://www.aozora.gr.jp/cards/001310/files/55609_ruby_53015.zip"
            },
            {
                "author": "前田普羅",
                "title": "普羅句集",
                "url": "https://www.aozora.gr.jp/cards/001719/files/55258_ruby_64312.zip"
            },
            {
                "author": "萩原朔太郎",
                "title": "俳句",
                "url": "https://www.aozora.gr.jp/cards/000067/files/53521_ruby_43535.zip"
            },
            {
                "author": "川端茅舎",
                "title": "川端茅舎句集",
                "url": "https://www.aozora.gr.jp/cards/000369/files/55239_ruby_65169.zip"
            },
            {
                "author": "松本たかし",
                "title": "松本たかし句集",
                "url": "https://www.aozora.gr.jp/cards/001720/files/55259_ruby_66667.zip"
            }
        ]
    
    def download_and_extract_text(self, work_info: Dict) -> str:
        """ZIPファイルをダウンロードしてテキストを抽出（ルビ保持）"""
        try:
            url = work_info['url']
            print(f"  ダウンロード中: {work_info['title']}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # ZIPファイルを解凍
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                # テキストファイルを探す
                for filename in zf.namelist():
                    if filename.endswith('.txt'):
                        with zf.open(filename) as f:
                            # エンコーディングを試行
                            for encoding in ['shift-jis', 'utf-8', 'cp932']:
                                try:
                                    f.seek(0)
                                    content = f.read().decode(encoding)
                                    # ルビは保持したまま、その他の注記のみ除去
                                    return self.clean_aozora_text_preserve_ruby(content)
                                except UnicodeDecodeError:
                                    continue
                            
                            # すべて失敗した場合
                            f.seek(0)
                            content = f.read().decode('shift-jis', errors='ignore')
                            return self.clean_aozora_text_preserve_ruby(content)
                            
        except Exception as e:
            print(f"  エラー: {e}")
            return ""
            
        return ""
    
    def clean_aozora_text_preserve_ruby(self, text: str) -> str:
        """青空文庫のテキストをクリーニング（ルビは保持）"""
        # 注記を除去 ［］内の文字を削除（ただしルビ《》は保持）
        text = re.sub(r'［[^］]*］', '', text)
        
        # 底本情報を除去
        text = re.sub(r'底本：.*', '', text, flags=re.DOTALL)
        
        # その他の記号を除去
        text = re.sub(r'[｜※×]', '', text)
        
        # 青空文庫のヘッダー・フッターを除去
        text = re.sub(r'-{10,}.*?-{10,}', '', text, flags=re.DOTALL)
        
        return text
    
    def extract_haiku_from_text(self, text: str, author: str, title: str) -> List[Dict]:
        """テキストから俳句を高精度で抽出"""
        haiku_list = []
        lines = text.split('\n')
        
        # 連続する空行で段落を分ける
        paragraphs = []
        current_para = []
        
        for line in lines:
            line = line.strip()
            if line:
                current_para.append(line)
            elif current_para:
                paragraphs.append('\n'.join(current_para))
                current_para = []
        
        if current_para:
            paragraphs.append('\n'.join(current_para))
        
        # 各段落から俳句を抽出
        for para in paragraphs:
            # 長い段落は俳句ではない
            if len(para) > 50:
                continue
            
            # 段落内の各行をチェック
            para_lines = para.split('\n')
            for line in para_lines:
                line = line.strip()
                
                # 基本的なフィルタリング
                if not line or len(line) > 35:  # ルビ込みで35文字以内
                    continue
                
                # 見出しや番号をスキップ
                if re.match(r'^[一二三四五六七八九十百千万]+[、\s　]', line):
                    continue
                if re.match(r'^[（\(][一二三四五六七八九十0-9]+[）\)]', line):
                    continue
                
                # ルビを含むテキストとルビのペアを抽出
                text_ruby_pairs = self.extractor.extract_text_with_ruby(line)
                
                # ルビなしテキスト（表示用）
                clean_text = re.sub(r'《[^》]*》', '', line)
                
                # ルビを使った音数カウント
                mora_count = self.extractor.count_mora_with_ruby(text_ruby_pairs)
                
                # 俳句構造チェック
                if self.extractor.is_haiku_structure(clean_text, mora_count):
                    # 5-7-5の可能性チェック
                    is_575 = (mora_count == 17)
                    
                    # 季節の判定
                    season = self.detect_season(clean_text)
                    
                    haiku_list.append({
                        'text': clean_text,
                        'text_with_ruby': line,  # ルビ付き原文
                        'author': author,
                        'source': title,
                        'mora_count': mora_count,
                        'is_575': is_575,
                        'season': season,
                        'confidence': self.calculate_confidence(clean_text, mora_count)
                    })
        
        return haiku_list
    
    def detect_season(self, text: str) -> Optional[str]:
        """季節を判定"""
        for season, kigos in self.extractor.kigo.items():
            for kigo in kigos:
                if kigo in text:
                    return season
        return None
    
    def calculate_confidence(self, text: str, mora_count: int) -> float:
        """俳句としての信頼度を計算（0.0-1.0）"""
        confidence = 0.5  # 基本スコア
        
        # 17音ぴったりなら高評価
        if mora_count == 17:
            confidence += 0.3
        elif 16 <= mora_count <= 18:
            confidence += 0.1
        
        # 切れ字があれば高評価
        if any(text.endswith(kireji) for kireji in self.extractor.kireji):
            confidence += 0.1
        
        # 季語があれば高評価
        if self.detect_season(text):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def scrape_all_haiku(self) -> pd.DataFrame:
        """すべての俳句を収集"""
        all_haiku = []
        
        print("青空文庫から俳句を高精度で収集開始...\n")
        print(f"収集対象: {len(self.target_works)}作品")
        
        for work in tqdm(self.target_works, desc="全体進捗"):
            # ダウンロードとテキスト抽出
            text = self.download_and_extract_text(work)
            
            if text:
                # 俳句抽出
                haiku_list = self.extract_haiku_from_text(
                    text, work['author'], work['title']
                )
                
                # 信頼度でフィルタリング
                high_quality = [h for h in haiku_list if h['confidence'] >= 0.6]
                all_haiku.extend(high_quality)
                
                print(f"  → {work['title']}: {len(high_quality)}句を抽出（信頼度0.6以上）")
            else:
                print(f"  → {work['title']}: 取得失敗")
                
            # サーバー負荷軽減
            time.sleep(0.5)
        
        # データフレーム作成
        df = pd.DataFrame(all_haiku)
        
        if len(df) == 0:
            print("\n俳句が抽出できませんでした。")
            return df
        
        # 重複除去
        df = df.drop_duplicates(subset=['text'])
        
        # 追加情報
        df['has_moon'] = df['text'].str.contains('月')
        df['has_autumn'] = df['season'] == '秋'
        
        return df
    
    def save_results(self, df: pd.DataFrame):
        """結果を保存"""
        if len(df) == 0:
            print("保存するデータがありません。")
            return None, None
            
        # CSV形式で保存
        csv_path = self.output_dir / "aozora_haiku_advanced.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"\nCSVファイルを保存: {csv_path}")
        
        # JSON形式で保存（学習用）
        json_data = []
        for _, row in df.iterrows():
            json_data.append({
                'text': row['text'],
                'metadata': {
                    'author': row['author'],
                    'source': row['source'],
                    'mora_count': int(row['mora_count']),
                    'is_575': bool(row['is_575']),
                    'season': row['season'],
                    'has_moon': bool(row['has_moon']),
                    'has_autumn': bool(row['has_autumn']),
                    'confidence': float(row['confidence'])
                }
            })
        
        json_path = self.output_dir / "aozora_haiku_training_advanced.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"JSONファイルを保存: {json_path}")
        
        # 統計情報
        print("\n=== 収集結果の統計 ===")
        print(f"総俳句数: {len(df)}")
        print(f"作者数: {df['author'].nunique()}")
        print(f"5-7-5形式: {df['is_575'].sum()} ({df['is_575'].sum()/len(df)*100:.1f}%)")
        print(f"月を含む句: {df['has_moon'].sum()}")
        
        # 季節別
        print("\n季節別:")
        season_counts = df['season'].value_counts()
        for season, count in season_counts.items():
            if season:
                print(f"  {season}: {count}句")
        
        # 信頼度分布
        print("\n信頼度分布:")
        conf_bins = pd.cut(df['confidence'], bins=[0.6, 0.7, 0.8, 0.9, 1.0])
        for bin_range, count in conf_bins.value_counts().sort_index().items():
            print(f"  {bin_range}: {count}句")
        
        # 高品質な俳句の例
        print("\n高品質な俳句の例（信頼度0.9以上）:")
        high_quality = df[df['confidence'] >= 0.9].head(5)
        for _, row in high_quality.iterrows():
            print(f"  {row['text']} ({row['author']})")
        
        return csv_path, json_path


def main():
    """メイン処理"""
    print("=== 青空文庫俳句収集（高精度版） ===")
    print("ルビを使った正確な音数カウントと厳密な俳句判定を行います。\n")
    
    scraper = AozoraHaikuScraperAdvanced()
    
    input("収集を開始するにはEnterキーを押してください...")
    
    # スクレイピング実行
    df = scraper.scrape_all_haiku()
    
    if len(df) > 0:
        # 結果を保存
        csv_path, json_path = scraper.save_results(df)
        
        print("\n収集完了！")
        print("\n高精度な俳句データが取得できました。")
        print("通常の文章は除外され、俳句らしい構造のものだけが抽出されています。")
    else:
        print("\n収集に失敗しました。")


if __name__ == "__main__":
    main()