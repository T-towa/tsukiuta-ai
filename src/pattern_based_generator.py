"""
定型パターンベースの月歌生成エンジン
確実に5-7-5形式を生成する
"""
import re
import random
from typing import List, Tuple, Optional
from .syllable_counter import SyllableCounter


class PatternBasedGenerator:
    """定型パターンベースの月歌生成クラス"""
    
    def __init__(self):
        self.syllable_counter = SyllableCounter()
        
        # 5音のパターン（上の句）
        self.kami_5 = [
            "つきあかり",    # 月明かり
            "あきのよの",    # 秋の夜の
            "しずかなる",    # 静かなる
            "つきかげが",    # 月影が
            "よるのにわ",    # 夜の庭
            "いしだたみ",    # 石畳
            "かぜすずし",    # 風涼し
            "つきをみて",    # 月を見て
            "こころにも",    # 心にも
            "ひとりきて",    # 一人来て
        ]
        
        # 7音のパターン（中の句）
        self.naka_7 = [
            "こころにしみる",      # 心に染みる
            "しずかにてらす",      # 静かに照らす
            "かがやきわたる",      # 輝き渡る
            "ひかりをあびて",      # 光を浴びて
            "そらにうかびて",      # 空に浮かびて
            "にわをてらして",      # 庭を照らして
            "おもいをはせる",      # 思いを馳せる
            "ときをわすれて",      # 時を忘れて
            "ゆめみるごとく",      # 夢見るごとく
            "かぜとともに",        # 風と共に
        ]
        
        # 5音のパターン（下の句）
        self.shimo_5 = [
            "あきのよる",    # 秋の夜
            "しずかなり",    # 静かなり
            "うつくしき",    # 美しき
            "こころあり",    # 心あり
            "ときながる",    # 時流る
            "かぜぞふく",    # 風ぞ吹く
            "つきのかげ",    # 月の影
            "よるふけて",    # 夜更けて
            "おもいあり",    # 思いあり
            "ひとりかな",    # 一人かな
        ]
        
        # 感想キーワードと月歌要素のマッピング
        self.keyword_mappings = {
            # 感情系
            "綺麗": ["うつくしき", "かがやきわたる", "こころにしみる"],
            "美しい": ["うつくしき", "かがやきわたる", "みとれけり"],
            "感動": ["こころにしみる", "おもいをはせる", "むねにひびく"],
            "静か": ["しずかなる", "しずかなり", "しずかにてらす"],
            "落ち着": ["こころやすらぐ", "おだやかなり", "ときをわすれて"],
            
            # 情景系
            "月": ["つきあかり", "つきかげが", "つきをみて", "つきのかげ"],
            "光": ["ひかりをあびて", "かがやきわたる", "てらしけり"],
            "夜": ["よるのにわ", "あきのよる", "よるふけて"],
            "秋": ["あきのよの", "あきかぜに", "あきのよる"],
            "風": ["かぜすずし", "かぜとともに", "かぜぞふく"],
            
            # 場所系
            "庭": ["にわをてらして", "よるのにわ", "にわにたつ"],
            "石": ["いしだたみ", "いしにつもる", "いわのうえ"],
            
            # 時間系
            "時": ["ときながる", "ときをわすれて", "ときすぎて"],
            "今": ["いまここに", "このときを", "いまをいきる"],
        }
        
    def extract_keywords(self, user_input: str) -> List[str]:
        """感想からキーワードを抽出"""
        keywords = []
        
        # マッピングされたキーワードを探す
        for key in self.keyword_mappings:
            if key in user_input:
                keywords.append(key)
        
        # 2-4文字の日本語単語も抽出
        japanese_words = re.findall(r'[ぁ-んァ-ン一-龥]{2,4}', user_input)
        keywords.extend(japanese_words)
        
        return list(set(keywords))  # 重複を除去
    
    def select_patterns(self, keywords: List[str]) -> Tuple[str, str, str]:
        """キーワードに基づいてパターンを選択"""
        # キーワードに関連する要素を収集
        related_elements = []
        
        for keyword in keywords:
            if keyword in self.keyword_mappings:
                related_elements.extend(self.keyword_mappings[keyword])
        
        # 上の句を選択
        kami_candidates = [p for p in self.kami_5 if any(e in p for e in related_elements)]
        if not kami_candidates:
            kami_candidates = self.kami_5
        kami = random.choice(kami_candidates)
        
        # 中の句を選択
        naka_candidates = [p for p in self.naka_7 if any(e in p for e in related_elements)]
        if not naka_candidates:
            naka_candidates = self.naka_7
        naka = random.choice(naka_candidates)
        
        # 下の句を選択
        shimo_candidates = [p for p in self.shimo_5 if any(e in p for e in related_elements)]
        if not shimo_candidates:
            shimo_candidates = self.shimo_5
        shimo = random.choice(shimo_candidates)
        
        return kami, naka, shimo
    
    def generate_with_keyword_insertion(self, user_input: str) -> Optional[str]:
        """キーワードを組み込んだ生成（実験的）"""
        keywords = self.extract_keywords(user_input)
        
        # 短いキーワード（2-3文字）を探す
        short_keywords = [k for k in keywords if 2 <= len(k) <= 3 and not re.match(r'[ぁ-ん]+', k)]
        
        if short_keywords and random.random() < 0.3:  # 30%の確率で試みる
            keyword = random.choice(short_keywords)
            
            # キーワードを含むパターンを作る
            patterns = [
                (f"{keyword}のよる", "しずかにてらす", "つきあかり"),  # 〇〇の夜
                ("つきあかり", f"{keyword}をてらして", "しずかなり"),  # 〇〇を照らして
                (f"{keyword}みて", "こころおだやか", "あきのよる"),    # 〇〇見て
            ]
            
            # 音数を確認して適切なものを選ぶ
            for pattern in patterns:
                total_mora = sum(self.syllable_counter.count_mora(p) for p in pattern)
                if total_mora == 17:
                    # 5-7-5になっているか確認
                    if (self.syllable_counter.count_mora(pattern[0]) == 5 and
                        self.syllable_counter.count_mora(pattern[1]) == 7 and
                        self.syllable_counter.count_mora(pattern[2]) == 5):
                        return " ".join(pattern)
        
        return None
    
    def generate(self, user_input: str) -> str:
        """月歌を生成（確実に5-7-5）"""
        # キーワード抽出
        keywords = self.extract_keywords(user_input)
        
        # キーワード挿入を試みる
        keyword_result = self.generate_with_keyword_insertion(user_input)
        if keyword_result:
            return keyword_result
        
        # 通常のパターン選択
        kami, naka, shimo = self.select_patterns(keywords)
        
        # 確実に5-7-5であることを確認
        assert self.syllable_counter.count_mora(kami) == 5
        assert self.syllable_counter.count_mora(naka) == 7
        assert self.syllable_counter.count_mora(shimo) == 5
        
        return f"{kami} {naka} {shimo}"
    
    def generate_multiple(self, user_input: str, count: int = 3) -> List[str]:
        """複数の月歌候補を生成"""
        results = []
        used_combinations = set()
        
        for _ in range(count * 3):  # 十分な試行回数
            keywords = self.extract_keywords(user_input)
            kami, naka, shimo = self.select_patterns(keywords)
            
            combination = (kami, naka, shimo)
            if combination not in used_combinations:
                used_combinations.add(combination)
                results.append(f"{kami} {naka} {shimo}")
                
            if len(results) >= count:
                break
                
        return results


# テスト用
if __name__ == "__main__":
    generator = PatternBasedGenerator()
    
    test_inputs = [
        "月がとても綺麗で感動しました",
        "静かな夜に心が落ち着きます",
        "秋の風が心地よいです",
        "月明かりが石畳を照らしています",
        "時間がゆっくり流れているようです",
    ]
    
    for user_input in test_inputs:
        print(f"\n感想: {user_input}")
        print("生成された月歌:")
        
        # 複数候補を生成
        results = generator.generate_multiple(user_input, count=3)
        for i, tsukiuta in enumerate(results, 1):
            print(f"  {i}. {tsukiuta}")
            
            # 音数確認
            parts = tsukiuta.split()
            mora_counts = [generator.syllable_counter.count_mora(p) for p in parts]
            print(f"     音数: {'-'.join(map(str, mora_counts))}")