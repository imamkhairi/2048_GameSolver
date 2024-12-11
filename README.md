# 2048 ゲームAI開発実験

この実験では、2048ゲームのAIプレイヤーを開発します。
2048は4x4のグリッド上で数字のタイルを動かして、より大きな数字のタイルを作っていくパズルゲームです。

## 実験の準備

1. まずRyeをインストールします。OSに応じて以下のコマンドを実行してください:

Linux/macOSの場合:
```bash
curl -sSf https://rye.astral.sh/get | bash
```

Windowsの場合:
- [Ryeのインストールページ](https://rye.astral.sh/guide/installation/)から適切なバイナリをダウンロード
- ダウンロードしたファイルを実行

2. リポジトリをクローンし、必要なライブラリをインストール:
```bash
git clone https://github.com/matt76k/z2048
cd z2048
rye sync
```

3. ゲームの実行:
```bash
rye run python src/main.py
```

## 実験内容

1. src/main.pyを開き、RandomPlayerクラスを参考にして独自のAIプレイヤーを実装してください。

2. 以下の点を考慮してAIを設計しましょう:
- タイルの配置をどのように評価するか
- どの方向に動かすのが最適か
- 何手先まで読むか

3. 実装したAIの性能を評価し、改善を試みてください。