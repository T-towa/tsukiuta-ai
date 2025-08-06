"""
日本語の音数（モーラ）をカウントするモジュール
俳句の5-7-5形式を検証するために使用
"""
import re
import jaconv
import mojimoji


class SyllableCounter:
    """日本語の音数をカウントするクラス"""
    
    def __init__(self):
        # 拗音（1音としてカウント）
        self.youon = ['ゃ', 'ゅ', 'ょ', 'ャ', 'ュ', 'ョ']
        # 促音・撥音（1音としてカウント）
        self.sokuon = ['っ', 'ッ', 'ん', 'ン']
        # 長音記号
        self.chouon = ['ー']
        
    def count_mora(self, text):
        """
        テキストの音数（モーラ）をカウント
        
        Args:
            text (str): カウント対象のテキスト
            
        Returns:
            int: 音数
        """
        # 全角に統一
        text = mojimoji.han_to_zen(text)
        
        # 基本的なカウント（文字数）
        count = len(text)
        
        # 拗音の調整（前の文字と合わせて1音）
        for y in self.youon:
            count -= text.count(y)
            
        # 促音・撥音は独立して1音
        # （すでに文字数でカウント済みなので調整不要）
        
        return count
    
    def split_575(self, text):
        """
        テキストを5-7-5に分割を試みる
        
        Args:
            text (str): 分割対象のテキスト
            
        Returns:
            tuple: (上の句, 中の句, 下の句) or None
        """
        text = text.replace(' ', '').replace('　', '')
        
        # 全体の音数を確認
        total_mora = self.count_mora(text)
        if total_mora != 17:
            return None
            
        # 5-7-5の分割を試行
        for i in range(1, len(text)):
            first_part = text[:i]
            if self.count_mora(first_part) == 5:
                for j in range(i+1, len(text)):
                    second_part = text[i:j]
                    if self.count_mora(second_part) == 7:
                        third_part = text[j:]
                        if self.count_mora(third_part) == 5:
                            return (first_part, second_part, third_part)
        
        return None
    
    def validate_575(self, text):
        """
        テキストが5-7-5形式かを検証
        
        Args:
            text (str): 検証対象のテキスト
            
        Returns:
            bool: 5-7-5形式の場合True
        """
        result = self.split_575(text)
        return result is not None
    
    def format_575(self, text):
        """
        5-7-5形式にフォーマット（スペース区切り）
        
        Args:
            text (str): フォーマット対象のテキスト
            
        Returns:
            str: フォーマット済みテキスト or 元のテキスト
        """
        result = self.split_575(text)
        if result:
            return f"{result[0]} {result[1]} {result[2]}"
        return text


# テスト用コード
if __name__ == "__main__":
    counter = SyllableCounter()
    
    # テストケース
    test_cases = [
        "つきあかりいしにしみいるあきのおと",  # 月明かり石に浸み入る秋の音
        "あきのよのつきはしずかにてらしけり",  # 秋の夜の月は静かに照らしけり
        "ちょっとまってよゆうびんきたよ",      # ちょっと待って郵便来たよ（拗音・促音のテスト）
    ]
    
    for text in test_cases:
        print(f"\n入力: {text}")
        print(f"音数: {counter.count_mora(text)}")
        print(f"5-7-5判定: {counter.validate_575(text)}")
        print(f"フォーマット: {counter.format_575(text)}")
        
        parts = counter.split_575(text)
        if parts:
            print(f"分割: {parts[0]}({counter.count_mora(parts[0])}) / " + 
                  f"{parts[1]}({counter.count_mora(parts[1])}) / " +
                  f"{parts[2]}({counter.count_mora(parts[2])})")