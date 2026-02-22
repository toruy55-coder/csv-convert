# CSV結合・変換ツール - Pythonスクリプト版

ブラウザのセキュリティ制限を回避し、真の「ワンクリック実行」を実現するPythonスクリプトです。

## 🚀 使い方（超シンプル！）

### 1. 設定ファイルをエクスポート

ブラウザ（index.html）で：
1. 定義モードで設定を作成
2. 「設定をエクスポート」ボタンをクリック
3. ダウンロードされたJSONファイルを **このフォルダに保存**

### 2. CSVファイルを配置

結合したいCSVファイルを **このフォルダに配置**：
- `test_a.csv`
- `test_b.csv`

または、`input/` フォルダに配置してもOK（自動作成されます）

### 3. 実行

#### Windows（ダブルクリック実行）
```
run.bat をダブルクリック
```

#### Mac/Linux（コマンドライン実行）
```bash
python3 run.py
```

#### 設定ファイルを指定する場合
```bash
python run.py 設定01.json
python run.py マスタ結合.json
```

### 4. 完了！

- `output/` フォルダに結合されたCSVが出力されます
- 実行ログ: `output/run_log.csv`

## 📁 フォルダ構造（自動生成）

```
csv-convert/
├── run.py                    # メインスクリプト
├── run.bat                   # Windows用バッチファイル
├── settings.json             # 設定ファイル（ここに配置）
├── test_a.csv                # 入力ファイルA（ここに配置）
├── test_b.csv                # 入力ファイルB（ここに配置）
├── input/                    # または input/ に配置してもOK（自動作成）
│   ├── test_a.csv
│   └── test_b.csv
└── output/                   # 出力フォルダ（自動作成）
    ├── 設定01_20260221123456.csv
    └── run_log.csv
```

## ✨ 新機能

### 1. フォルダ自動作成
- `input/` と `output/` フォルダは自動作成されます
- 手動でフォルダを作る必要はありません

### 2. 設定ファイルの柔軟な配置
- ルートディレクトリに配置するだけでOK
- 複数の設定ファイルがある場合は、引数で指定

### 3. 入力ファイルの自動検出
- カレントディレクトリを優先的に検索
- 見つからない場合は `input/` フォルダを検索

## ⚙️ 機能

### 対応している結合方法
- Inner Join（両方に一致する行だけ出力）
- Left Join（Aを基準にBを補完）
- Right Join（Bを基準にAを補完）
- Outer Join（すべての行を出力）

### データ検証
- 空白キーチェック
- 重複キーチェック
- カラム数不一致チェック

### データ変換
- 変換ルール適用（値の置き換え）
- 重複行除去
- カラムの選択・除外・リネーム

### 出力形式
- BOM付きUTF-8（Excelで文字化けしない）
- 実行ログの自動記録

## 📋 設定ファイルの例

```json
{
  "name": "テスト設定01",
  "fileNameA": "test_a.csv",
  "fileNameB": "test_b.csv",
  "keyA": "0",
  "keyB": "0",
  "joinType": "left",
  "columns": [
    {
      "source": "A",
      "original": "社員ID",
      "name": "社員ID",
      "index": 0,
      "selected": true
    }
  ],
  "rules": [
    {
      "column": "評価",
      "from": "1",
      "to": "優"
    }
  ],
  "validation": {
    "checkBlank": true,
    "checkDuplicate": false,
    "checkColumnCount": false,
    "removeDuplicates": true
  }
}
```

## 🔧 技術仕様

- **Python**: 3.6以上
- **依存ライブラリ**: なし（標準ライブラリのみ使用）
- **使用モジュール**: csv, json, os, datetime, collections

## ❌ トラブルシューティング

### Pythonがインストールされていない

**エラー**: `'python' は、内部コマンドまたは外部コマンド...`

**解決策**:
1. https://www.python.org/downloads/ からPythonをダウンロード
2. インストール時に「Add Python to PATH」にチェック
3. コマンドプロンプトを再起動

### 設定ファイルが見つからない

**エラー**: `❌ エラー: 設定ファイルが見つかりません`

**解決策**:
1. ブラウザで設定をエクスポート
2. ダウンロードしたJSONファイルをルートディレクトリに配置

### 複数の設定ファイルがある

**エラー**: `❌ エラー: 複数の設定ファイルが見つかりました`

**解決策**:
実行時に設定ファイルを指定してください：
```bash
python run.py 設定01.json
```

### 入力ファイルが見つからない

**エラー**: `❌ エラー: ファイルが見つかりません: test_a.csv`

**解決策**:
1. 設定ファイルの `fileNameA` と `fileNameB` を確認
2. 対応するファイルをカレントディレクトリまたは `input/` フォルダに配置

## 📝 実行ログの形式

`output/run_log.csv`:

| 実行日時 | 設定名 | ファイルA | ファイルB | 出力行数 | 警告有無 | 重複除去 | 出力ファイル |
|---------|--------|-----------|-----------|----------|----------|----------|--------------|
| 2026-02-21 12:34:56 | テスト設定01 | test_a.csv | test_b.csv | 9 | あり | 1行 | テスト設定01_20260221123456.csv |

## 🎯 使用例

### 例1: 最もシンプルな使い方

```bash
# 1. settings.json をルートに配置
# 2. test_a.csv と test_b.csv をルートに配置
# 3. 実行
run.bat  # または python run.py
```

### 例2: 複数の設定を使い分け

```bash
# 設定ファイルごとに実行
python run.py マスタ結合.json
python run.py 日次集計.json
python run.py 月次レポート.json
```

### 例3: input/ フォルダを使用

```
csv-convert/
├── run.py
├── settings.json
└── input/
    ├── master.csv
    └── sales.csv
```

```bash
python run.py  # 自動的に input/ から読み込み
```

## 💡 便利な使い方

### バッチ処理
複数の設定を順番に実行：

**Windows (run_all.bat)**:
```batch
@echo off
python run.py 設定01.json
python run.py 設定02.json
python run.py 設定03.json
pause
```

**Mac/Linux (run_all.sh)**:
```bash
#!/bin/bash
python3 run.py 設定01.json
python3 run.py 設定02.json
python3 run.py 設定03.json
```

### 定期実行
Windowsタスクスケジューラやcronで自動実行：

```bash
# cron で毎日朝9時に実行
0 9 * * * cd /path/to/csv-convert && python3 run.py settings.json
```

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. Pythonのバージョン: `python --version`
2. 設定ファイルの存在: `settings.json`
3. 入力ファイルの存在: カレントディレクトリまたは `input/`
4. 実行ログ: `output/run_log.csv`

---

## 🆚 WebUI版との使い分け

| 項目 | WebUI版 (index.html) | Python版 (run.py) |
|------|----------------------|-------------------|
| 設定作成 | ✅ ブラウザで簡単 | ❌ WebUIで作成が必要 |
| 実行速度 | 普通 | ⚡ 高速 |
| ファイル選択 | 毎回選択 | 自動検出 |
| 自動化 | ❌ 不可 | ✅ 可能（バッチ・cron） |
| 定期実行 | ❌ 不可 | ✅ 可能 |
| 大量データ | △ 制限あり | ✅ 大容量OK |

**推奨**: 設定はWebUIで作成し、実行はPythonスクリプトで自動化！
