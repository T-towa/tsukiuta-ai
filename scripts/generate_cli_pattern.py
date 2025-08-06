#!/usr/bin/env python3
"""
月歌生成CLIツール（定型パターン版）
確実に5-7-5を生成するバージョン
"""
import click
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from src.pattern_based_generator import PatternBasedGenerator
from src.syllable_counter import SyllableCounter


class TsukiutaCLI:
    """月歌生成CLIクラス"""
    
    def __init__(self):
        self.generator = PatternBasedGenerator()
        self.syllable_counter = SyllableCounter()
        self.history = []
        
    def save_history(self, output_file: str = "tsukiuta_history.json"):
        """生成履歴を保存"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
        print(f"\n履歴を保存しました: {output_file}")
        
    def display_tsukiuta(self, tsukiuta: str, user_input: str):
        """月歌を表示"""
        print("\n" + "="*50)
        print("🌙 生成された月歌 🌙")
        print("="*50)
        print(f"\n{tsukiuta}\n")
        
        # 音数を表示（確認用）
        parts = tsukiuta.split()
        mora_counts = [self.syllable_counter.count_mora(p) for p in parts]
        print(f"音数: {'-'.join(map(str, mora_counts))}")
        
        print(f"\n元の感想: {user_input}")
        print("="*50 + "\n")


@click.group()
def cli():
    """月歌生成CLIツール"""
    pass


@cli.command()
def interactive():
    """対話モードで月歌を生成"""
    cli_app = TsukiutaCLI()
    
    print("🌙 月歌生成システム（定型パターン版）🌙")
    print("感想を入力すると、5-7-5形式の月歌を生成します。")
    print("\nコマンド:")
    print("  quit/exit/q - 終了")
    print("  history - 生成履歴を表示")
    print("  save - 履歴を保存")
    print("  multi - 複数候補を生成\n")
    
    while True:
        try:
            # 感想の入力
            user_input = input("感想を入力してください > ").strip()
            
            # コマンド処理
            if user_input.lower() in ['quit', 'exit', 'q']:
                if cli_app.history:
                    save = input("\n履歴を保存しますか？ (y/n): ")
                    if save.lower() == 'y':
                        cli_app.save_history()
                print("\n月歌生成システムを終了します。")
                break
                
            elif user_input.lower() == 'history':
                if not cli_app.history:
                    print("\nまだ月歌を生成していません。\n")
                else:
                    print(f"\n=== 生成履歴 ({len(cli_app.history)}件) ===")
                    for i, item in enumerate(cli_app.history, 1):
                        print(f"\n{i}. {item['tsukiuta']}")
                        print(f"   感想: {item['input']}")
                        print(f"   時刻: {item['timestamp']}")
                    print()
                continue
                
            elif user_input.lower() == 'save':
                if cli_app.history:
                    cli_app.save_history()
                else:
                    print("\n保存する履歴がありません。\n")
                continue
                
            elif user_input.lower() == 'multi':
                # 複数候補モード
                sub_input = input("感想を入力してください（複数候補） > ").strip()
                if sub_input:
                    print("\n生成中...")
                    results = cli_app.generator.generate_multiple(sub_input, count=5)
                    print(f"\n=== 生成候補（5件）===")
                    for i, tsukiuta in enumerate(results, 1):
                        print(f"{i}. {tsukiuta}")
                    print()
                continue
                
            # 空入力チェック
            if not user_input:
                print("\n感想を入力してください。\n")
                continue
                
            # 文字数チェック
            if len(user_input) > 50:
                print("\n感想は50文字以内で入力してください。\n")
                continue
                
            # 月歌生成
            print("\n生成中...")
            tsukiuta = cli_app.generator.generate(user_input)
            
            # 表示
            cli_app.display_tsukiuta(tsukiuta, user_input)
            
            # 履歴に追加
            cli_app.history.append({
                'timestamp': datetime.now().isoformat(),
                'input': user_input,
                'tsukiuta': tsukiuta
            })
            
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
    generator = PatternBasedGenerator()
    counter = SyllableCounter()
    
    print(f"\n感想: {input_text}")
    print("生成中...")
    
    tsukiuta = generator.generate(input_text)
    
    print(f"\n生成された月歌: {tsukiuta}")
    
    # 音数確認
    parts = tsukiuta.split()
    mora_counts = [counter.count_mora(p) for p in parts]
    print(f"音数: {'-'.join(map(str, mora_counts))}")


@cli.command()
def test():
    """テストモード - いろいろな感想で試す"""
    generator = PatternBasedGenerator()
    
    test_inputs = [
        "月がとても綺麗で感動しました",
        "静かな夜に心が落ち着きます",
        "秋の風が心地よいです",
        "月明かりが石畳を照らしています",
        "時間がゆっくり流れているようです",
        "幻想的な光景です",
        "日本の美を感じます",
        "心が洗われるようです",
    ]
    
    print("🌙 月歌生成テスト 🌙\n")
    
    for user_input in test_inputs:
        print(f"感想: {user_input}")
        tsukiuta = generator.generate(user_input)
        print(f"月歌: {tsukiuta}")
        print()


if __name__ == "__main__":
    cli()