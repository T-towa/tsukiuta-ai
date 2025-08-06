#!/usr/bin/env python3
"""
月歌生成CLIツール
ターミナルから感想を入力して月歌を生成する
"""
import click
import sys
import json
from pathlib import Path
from datetime import datetime

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from src.tsukiuta_generator import TsukiutaGenerator
from src.syllable_counter import SyllableCounter


class TsukiutaCLI:
    """月歌生成CLIクラス"""
    
    def __init__(self, model_path: str = None):
        """初期化"""
        self.model_path = model_path or "rinna/japanese-gpt-neox-3.6b"
        self.generator = None
        self.syllable_counter = SyllableCounter()
        self.history = []
        
    def load_generator(self):
        """ジェネレーターを遅延読み込み"""
        if self.generator is None:
            print("月歌AIを初期化しています...\n")
            self.generator = TsukiutaGenerator(self.model_path)
            
    def save_history(self, output_file: str = "tsukiuta_history.json"):
        """生成履歴を保存"""
        history_path = Path(output_file)
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
        print(f"\n履歴を保存しました: {history_path}")
        
    def display_tsukiuta(self, tsukiuta: str, user_input: str):
        """月歌を表示"""
        print("\n" + "="*50)
        print("🌙 生成された月歌 🌙")
        print("="*50)
        print(f"\n{tsukiuta}\n")
        
        # 音数を表示
        parts = self.syllable_counter.split_575(tsukiuta.replace(' ', ''))
        if parts:
            print(f"音数: {self.syllable_counter.count_mora(parts[0])}-" +
                  f"{self.syllable_counter.count_mora(parts[1])}-" +
                  f"{self.syllable_counter.count_mora(parts[2])}")
        
        print("\n元の感想:", user_input)
        print("="*50 + "\n")
        
    def interactive_mode(self):
        """対話モード"""
        self.load_generator()
        
        print("🌙 月歌生成システム 🌙")
        print("感想を入力すると、5-7-5形式の月歌を生成します。")
        print("\nコマンド:")
        print("  quit/exit/q - 終了")
        print("  history - 生成履歴を表示")
        print("  save - 履歴を保存\n")
        
        while True:
            try:
                # 感想の入力
                user_input = input("感想を入力してください > ").strip()
                
                # コマンド処理
                if user_input.lower() in ['quit', 'exit', 'q']:
                    if self.history:
                        save = input("\n履歴を保存しますか？ (y/n): ")
                        if save.lower() == 'y':
                            self.save_history()
                    print("\n月歌生成システムを終了します。")
                    break
                    
                elif user_input.lower() == 'history':
                    if not self.history:
                        print("\nまだ月歌を生成していません。\n")
                    else:
                        print(f"\n=== 生成履歴 ({len(self.history)}件) ===")
                        for i, item in enumerate(self.history, 1):
                            print(f"\n{i}. {item['tsukiuta']}")
                            print(f"   感想: {item['input']}")
                            print(f"   時刻: {item['timestamp']}")
                        print()
                    continue
                    
                elif user_input.lower() == 'save':
                    if self.history:
                        self.save_history()
                    else:
                        print("\n保存する履歴がありません。\n")
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
                print("\n月歌を生成中...")
                tsukiuta = self.generator.generate_tsukiuta(user_input)
                
                if not tsukiuta:
                    # フォールバック
                    print("5-7-5形式の生成に失敗しました。定型パターンを使用します。")
                    tsukiuta = self.generator.generate_with_fixed_patterns(user_input)
                
                # 表示
                self.display_tsukiuta(tsukiuta, user_input)
                
                # 履歴に追加
                self.history.append({
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


@click.group()
def cli():
    """月歌生成CLIツール"""
    pass


@cli.command()
@click.option('--model', '-m', default=None, help='使用するモデルのパス')
def interactive(model):
    """対話モードで月歌を生成"""
    cli_app = TsukiutaCLI(model)
    cli_app.interactive_mode()


@cli.command()
@click.argument('input_text')
@click.option('--model', '-m', default=None, help='使用するモデルのパス')
def generate(input_text, model):
    """単発で月歌を生成"""
    cli_app = TsukiutaCLI(model)
    cli_app.load_generator()
    
    print(f"\n感想: {input_text}")
    print("月歌を生成中...")
    
    tsukiuta = cli_app.generator.generate_tsukiuta(input_text)
    if not tsukiuta:
        tsukiuta = cli_app.generator.generate_with_fixed_patterns(input_text)
    
    cli_app.display_tsukiuta(tsukiuta, input_text)


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
        ("ときながれ", "こころおだやか", "つきをみて")
    ]
    
    from random import choice, shuffle
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
    print("実際の使用には 'tsukiuta interactive' を実行してください。")


if __name__ == "__main__":
    cli()