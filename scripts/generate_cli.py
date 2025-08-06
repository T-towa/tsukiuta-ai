#!/usr/bin/env python3
"""
月歌生成CLIツール（AI対応版）
"""
import click
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.tsukiuta_generator import TsukiutaGenerator
from src.syllable_counter import SyllableCounter


@click.group()
def cli():
    """月歌生成CLIツール"""
    pass


@cli.command()
def interactive():
    """対話モードで月歌を生成"""
    print("🌙 月歌生成システム 🌙")
    print("AIモデルを初期化しています...")
    print("（初回は5-10分かかることがあります）\n")
    
    try:
        generator = TsukiutaGenerator()
        counter = SyllableCounter()
    except Exception as e:
        print(f"エラー: モデルの読み込みに失敗しました")
        print(f"詳細: {e}")
        return
    
    print("\n準備完了！")
    print("感想を入力すると、5-7-5形式の月歌を生成します。")
    print("終了: quit または exit\n")
    
    while True:
        try:
            # 感想の入力
            user_input = input("感想を入力してください > ").strip()
            
            # 終了コマンド
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n月歌生成システムを終了します。")
                break
                
            # 空入力チェック
            if not user_input:
                print("感想を入力してください。\n")
                continue
                
            # 月歌生成
            print("\n月歌を生成中...")
            tsukiuta = generator.generate_tsukiuta(user_input)
            
            if not tsukiuta:
                print("AI生成に失敗しました。定型パターンを使用します。")
                tsukiuta = generator.generate_with_fixed_patterns(user_input)
            
            # 表示
            print("\n" + "="*50)
            print("🌙 生成された月歌 🌙")
            print("="*50)
            print(f"\n{tsukiuta}\n")
            
            # 音数を表示
            parts = counter.split_575(tsukiuta.replace(' ', ''))
            if parts:
                print(f"音数: {counter.count_mora(parts[0])}-" +
                      f"{counter.count_mora(parts[1])}-" +
                      f"{counter.count_mora(parts[2])}")
            
            print(f"\n元の感想: {user_input}")
            print("="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n中断されました。")
            break
        except Exception as e:
            print(f"\nエラーが発生しました: {e}\n")
            continue


@cli.command()
@click.argument('input_text')
def generate(input_text):
    """単発で月歌を生成"""
    print("モデルを読み込んでいます...")
    
    try:
        generator = TsukiutaGenerator()
        counter = SyllableCounter()
    except Exception as e:
        print(f"エラー: {e}")
        return
    
    print(f"\n感想: {input_text}")
    print("月歌を生成中...")
    
    tsukiuta = generator.generate_tsukiuta(input_text)
    if not tsukiuta:
        tsukiuta = generator.generate_with_fixed_patterns(input_text)
    
    print(f"\n生成された月歌: {tsukiuta}")
    
    # 音数確認
    mora = counter.count_mora(tsukiuta.replace(' ', ''))
    print(f"音数: {mora}")


@cli.command()
@click.option('--count', '-c', default=5, help='生成するサンプル数')
def demo(count):
    """デモ用のサンプル生成（AIなし）"""
    # 既存のデモコードと同じ
    sample_inputs = [
        "月がとても綺麗で感動しました",
        "静かな夜に心が落ち着きます",
        "幻想的な光景に包まれています",
        "秋の風が心地よいです",
        "月明かりが石畳を照らしています",
    ]
    
    print("🌙 月歌生成デモ 🌙\n")
    print("注: これはAIを使わない簡易デモです。\n")
    
    demo_patterns = [
        ("つきあかり", "こころにしみる", "あきのよる"),
        ("しずかなる", "にわにてりつつ", "つきをみる"),
        ("あきかぜに", "ゆれるすすきと", "つきのかげ"),
        ("いしだたみ", "てらすつきかげ", "うつくしき"),
        ("ときながれ", "こころおだやか", "つきをみて"),
    ]
    
    from random import choice, shuffle
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
            
        print(f"月歌: {tsukiuta}")
        
    print("\n" + "="*50)
    print("AI生成を使うには: python scripts/generate_cli.py interactive")


if __name__ == "__main__":
    cli()