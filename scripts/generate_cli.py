#!/usr/bin/env python3
"""
月歌生成CLIツール（簡易版）
デモ機能のみ実装
"""
import click
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from src.syllable_counter import SyllableCounter


@click.group()
def cli():
    """月歌生成CLIツール"""
    pass


@cli.command()
@click.option('--count', '-c', default=5, help='生成するサンプル数')
def demo(count):
    """デモ用のサンプル生成"""
    # デモ用の感想リスト
    sample_inputs = [
        "月がとても綺麗で感動しました",
        "静かな夜に心が落ち着きます",
        "幻想的な光景に包まれています",
        "秋の風が心地よいです",
        "月明かりが石畳を照らしています",
        "時間がゆっくり流れているようです",
        "日本の美を感じます",
        "心が洗われるようです"
    ]
    
    print("🌙 月歌生成デモ 🌙\n")
    print("注: これは事前定義されたパターンを使用したデモです。")
    print("実際の生成にはAIモデルのロードが必要です。\n")
    
    # 簡易的なデモ生成
    demo_patterns = [
        ("つきあかり", "こころにしみる", "あきのよる"),
        ("しずかなる", "にわにてりつつ", "つきをみる"),
        ("あきかぜに", "ゆれるすすきと", "つきのかげ"),
        ("いしだたみ", "てらすつきかげ", "うつくしき"),
        ("ときながれ", "こころおだやか", "つきをみて"),
        ("つきみじに", "あつまるひとの", "えがおかな"),
        ("よるのにわ", "つきのひかりに", "つつまれて"),
        ("かぜすずし", "つきはしずかに", "かがやけり")
    ]
    
    from random import choice, shuffle
    
    # 音数カウンター
    counter = SyllableCounter()
    
    used_patterns = demo_patterns.copy()
    shuffle(used_patterns)
    
    for i in range(min(count, len(sample_inputs))):
        print(f"\n--- サンプル {i+1} ---")
        print(f"感想: {sample_inputs[i]}")
        
        if i < len(used_patterns):
            tsukiuta = " ".join(used_patterns[i])
        else:
            tsukiuta = " ".join(choice(demo_patterns))
        
        # 音数を確認
        parts = used_patterns[i] if i < len(used_patterns) else choice(demo_patterns)
        mora_counts = [counter.count_mora(part) for part in parts]
        
        print(f"月歌: {tsukiuta}")
        print(f"音数: {mora_counts[0]}-{mora_counts[1]}-{mora_counts[2]}")
        
    print("\n" + "="*50)
    print("これはデモ版です。実際のAI生成を使うには、")
    print("必要なモジュールをすべてインストールしてください。")


@cli.command()
def test_counter():
    """音数カウンターのテスト"""
    counter = SyllableCounter()
    
    print("🌙 音数カウンターテスト 🌙\n")
    
    test_cases = [
        "つきあかり",
        "こころにしみる", 
        "あきのよる",
        "しずかなよる",
        "きょうのつき",
        "ちょっとまって",
        "つきあかりこころにしみるあきのよる",
    ]
    
    for text in test_cases:
        mora = counter.count_mora(text)
        is_575 = counter.validate_575(text)
        
        print(f"テキスト: {text}")
        print(f"  音数: {mora}")
        print(f"  5-7-5判定: {'○' if is_575 else '×'}")
        
        if is_575:
            formatted = counter.format_575(text)
            print(f"  フォーマット: {formatted}")
        print()


if __name__ == "__main__":
    cli()