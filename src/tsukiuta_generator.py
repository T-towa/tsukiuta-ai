"""
月歌生成エンジン（簡易版）
rinnaモデルを使用して、感想から5-7-5形式の月歌を生成
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import re
from typing import List, Optional
from .syllable_counter import SyllableCounter
import time


class TsukiutaGenerator:
    """月歌生成クラス"""
    
    def __init__(self, model_path: str = "rinna/japanese-gpt-neox-small"):
        """
        初期化
        注: 最初はsmallモデルを使用（メモリ節約のため）
        """
        print(f"モデルを読み込んでいます: {model_path}")
        print("初回は時間がかかります...")
        
        self.device = torch.device("cpu")  # MacBookではCPUを使用
        
        # モデルとトークナイザーの読み込み
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        
        # 音数カウンター
        self.syllable_counter = SyllableCounter()
        
        print("モデルの読み込み完了！")
        
    def create_prompt(self, user_input: str) -> str:
        """プロンプトを作成"""
        prompt = f"""5-7-5の俳句を作ってください。必ず5音、7音、5音の3つの部分に分けてください。

例：
ふるいけや（5音） かわずとびこむ（7音） みずのおと（5音）
つきあかり（5音） いしにしみいる（7音） あきのかぜ（5音）

感想: {user_input}
俳句:"""
        return prompt
    
    def extract_haiku_candidates(self, generated_text: str) -> List[str]:
        """生成されたテキストから俳句候補を抽出"""
        # 改行で分割
        lines = generated_text.split('\n')
        
        candidates = []
        for line in lines:
            # 空行をスキップ
            line = line.strip()
            if not line:
                continue
                
            # 句読点や記号を除去
            cleaned = re.sub(r'[。、！？「」『』（）\(\)]', '', line)
            cleaned = cleaned.replace(' ', '').replace('　', '')
            
            # 10文字以上25文字以下の行を候補とする
            if 10 <= len(cleaned) <= 25:
                candidates.append(cleaned)
                
        return candidates[:5]  # 最大5候補
    
    def generate_tsukiuta(self, user_input: str) -> Optional[str]:
        """月歌を生成（簡易版）"""
        start_time = time.time()
        
        # プロンプト作成
        prompt = self.create_prompt(user_input)
        
        # トークナイズ
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        # 生成
        print("生成中...")
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.8,
                do_sample=True,
                num_return_sequences=3,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        
        # デコード
        generated_texts = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
        
        # 候補を探す
        all_candidates = []
        for text in generated_texts:
            # プロンプト部分を除去
            text = text.replace(prompt, "").strip()
            candidates = self.extract_haiku_candidates(text)
            all_candidates.extend(candidates)
        
        # 5-7-5形式の候補を探す
        for candidate in all_candidates:
            if self.syllable_counter.validate_575(candidate):
                elapsed_time = time.time() - start_time
                print(f"生成時間: {elapsed_time:.2f}秒")
                return self.syllable_counter.format_575(candidate)
        
        # 見つからない場合は最初の候補を返す
        elapsed_time = time.time() - start_time
        print(f"生成時間: {elapsed_time:.2f}秒")
        print("警告: 正確な5-7-5形式が生成できませんでした")
        
        if all_candidates:
            best = all_candidates[0]
            mora = self.syllable_counter.count_mora(best)
            print(f"音数: {mora}")
            return best
        
        return None
    
    def generate_with_fixed_patterns(self, user_input: str) -> str:
        """定型パターンを使った月歌生成（フォールバック用）"""
        # 定型パターン
        patterns = [
            ("つきあかり", "KEYWORD をてらして", "しずかなり"),
            ("あきのよの", "KEYWORD のなかに", "つきうかぶ"),
            ("KEYWORD に", "つきのひかりが", "そそぎけり"),
        ]
        
        # 感想からキーワードを抽出（簡易版）
        keywords = re.findall(r'[ぁ-んァ-ン]{2,4}', user_input)
        if not keywords:
            keywords = ["おもい"]
            
        # パターンに当てはめる
        import random
        pattern = random.choice(patterns)
        keyword = random.choice(keywords)
        
        # キーワードが長すぎる場合は調整
        if len(keyword) > 4:
            keyword = keyword[:4]
            
        haiku_parts = []
        for part in pattern:
            if "KEYWORD" in part:
                part = part.replace("KEYWORD", keyword)
            haiku_parts.append(part)
            
        return " ".join(haiku_parts)