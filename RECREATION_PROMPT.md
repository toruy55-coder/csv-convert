# CSV結合・変換ツール - 再現プロンプト

このプロンプトをAIアシスタントに与えることで、CSV結合・変換ツール全体を再現できます。

---

## プロンプト

以下の仕様でCSV結合・変換ツールを作成してください。

### 全体要件

1. **Webアプリケーション版**（index.html）
   - 単一HTMLファイル（HTML/CSS/JavaScript統合）
   - 外部ライブラリ不使用
   - 日本語UI

2. **Pythonスクリプト版**（run.py）
   - Python 3.6以上
   - 標準ライブラリのみ使用
   - コマンドライン実行

3. **テストデータ**
   - test_a.csv（社員マスタ、9行）
   - test_b.csv（売上データ、10行、重複あり）
   - test_single.csv（カラム整形用、15行）

---

### 1. Webアプリケーション（index.html）

#### タブ構成（5つのタブ）

##### タブ1: 定義モード
**機能**:
- 設定名入力
- CSV A選択（ファイル選択 + ドラッグ&ドロップ）
- CSV B選択（ファイル選択 + ドラッグ&ドロップ）
- 結合キー選択（カラムインデックス）
- 結合方式選択（Inner/Left/Right/Outer Join）
- カラム設定
  - 選択（チェックボックス）
  - 並び替え（ドラッグ&ドロップ）
  - リネーム
- 変換ルール（カラム、変換前、変換後）
- データ検証設定（空白キー、重複キー、カラム数不一致、重複行除去）
- 保存（LocalStorage）
- エクスポート（JSONダウンロード）
- インポート（JSONアップロード）
- 🆕新規作成ボタン（すべてクリア）

**UI要素**:
```
[設定名入力欄]
[ファイルAドロップゾーン] [ファイル選択ボタン]
[ファイルBドロップゾーン] [ファイル選択ボタン]
[結合キーA選択] [結合キーB選択]
[○ Inner Join] [○ Left Join] [○ Right Join] [○ Outer Join]
[カラムリスト（ドラッグ可能、チェックボックス、リネーム欄）]
[変換ルール追加ボタン]
[☑ 空白キーチェック] [☑ 重複キーチェック] [☑ カラム数不一致チェック] [☑ 重複行除去]
[保存ボタン] [エクスポートボタン] [インポートボタン] [🆕新規作成ボタン]
```

##### タブ2: 実行モード
**機能**:
- 設定選択（LocalStorageから）
- CSV A選択（ファイル選択 + ドラッグ&ドロップ）
- CSV B選択（ファイル選択 + ドラッグ&ドロップ）
- 実行ボタン
- データ検証実行
- CSV結合実行
- 変換ルール適用
- 重複行除去
- プレビュー表示（最初の10行）
- CSVダウンロード（BOM付きUTF-8）
- 実行ログ記録
- **実行時に `lastExecutionData` グローバル変数に実行データを保存**

**重要な実装詳細**:
- グローバル変数 `executeFileA`、`executeFileB` を定義
- ファイル選択時（input.changeイベント）にグローバル変数を更新
- ドラッグ&ドロップ時にもグローバル変数を更新
- 実行ボタンでグローバル変数からファイルを取得
- 実行成功時に以下の構造で `lastExecutionData` に保存：
```javascript
lastExecutionData = {
  setting: setting,      // 使用した設定
  fileA: executeFileA,   // FileオブジェクトA
  fileB: executeFileB,   // FileオブジェクトB
  fileNameA: executeFileA.name,
  fileNameB: executeFileB.name,
  dataA: dataA,          // CSV Aのデータ
  dataB: dataB           // CSV Bのデータ
};
```

##### タブ3: ワンクリック実行モード
**機能**:
- 前回実行データの確認（`lastExecutionData` から読込）
- データがない場合: 実行モードでの実行を促すメッセージ表示
- データがある場合: 前回実行情報（設定名、ファイル名A/B、実行日時）を表示
- ワンクリック実行ボタン
- 保存されたデータを使って即座に実行
- プレビュー表示
- CSVダウンロード

**UI構造**:
```html
<div id="oneclick-no-data" style="display:none">
  <p>前回の実行データがありません。まず「実行モード」で実行してください。</p>
</div>
<div id="oneclick-with-data" style="display:none">
  <p>前回実行情報: [設定名] [ファイルA] [ファイルB] [実行日時]</p>
  <button id="oneclick-run">ワンクリック実行</button>
</div>
```

**重要**: ファイル選択UIは不要。前回実行の `lastExecutionData` を使用。

##### タブ4: カラム整形モード
**機能**:
- CSVファイル選択（ファイル選択 + ドラッグ&ドロップ）
- カラム選択
- カラム並び替え
- カラムリネーム
- 変換ルール
- 重複行除去
- プレビュー表示
- CSVダウンロード

##### タブ5: 実行ログモード
**機能**:
- 実行履歴表示（LocalStorageから）
- ログクリア

---

#### CSV結合ロジック

##### Inner Join
```javascript
// B側をHashMapに変換
const mapB = {};
for (const rowB of dataB.slice(1)) {
  const key = rowB[keyB];
  if (!mapB[key]) mapB[key] = [];
  mapB[key].push(rowB);
}

// A側をループして結合
for (const rowA of dataA.slice(1)) {
  const key = rowA[keyA];
  const rowsB = mapB[key] || [];
  if (rowsB.length > 0) {
    for (const rowB of rowsB) {
      output.push(combineRow(rowA, rowB, columns));
    }
  }
}
```

##### Left Join
```javascript
// Inner Joinと同様だが、マッチしない場合もA側を出力
for (const rowA of dataA.slice(1)) {
  const key = rowA[keyA];
  const rowsB = mapB[key] || [];
  if (rowsB.length > 0) {
    for (const rowB of rowsB) {
      output.push(combineRow(rowA, rowB, columns));
    }
  } else {
    output.push(combineRow(rowA, null, columns)); // B側は空
  }
}
```

##### Right Join
```javascript
// A側をHashMapに変換
const mapA = {};
for (const rowA of dataA.slice(1)) {
  const key = rowA[keyA];
  if (!mapA[key]) mapA[key] = [];
  mapA[key].push(rowA);
}

// B側をループして結合
for (const rowB of dataB.slice(1)) {
  const key = rowB[keyB];
  const rowsA = mapA[key] || [];
  if (rowsA.length > 0) {
    for (const rowA of rowsA) {
      output.push(combineRow(rowA, rowB, columns));
    }
  } else {
    output.push(combineRow(null, rowB, columns)); // A側は空
  }
}
```

##### Outer Join
```javascript
// まずLeft Joinを実行し、マッチしたB側のキーを記録
const matchedKeysB = new Set();
for (const rowA of dataA.slice(1)) {
  const key = rowA[keyA];
  const rowsB = mapB[key] || [];
  if (rowsB.length > 0) {
    matchedKeysB.add(key);
    for (const rowB of rowsB) {
      output.push(combineRow(rowA, rowB, columns));
    }
  } else {
    output.push(combineRow(rowA, null, columns));
  }
}

// B側の未マッチ行を追加
for (const rowB of dataB.slice(1)) {
  const key = rowB[keyB];
  if (!matchedKeysB.has(key)) {
    output.push(combineRow(null, rowB, columns));
  }
}
```

**重要**: Right JoinとOuter Joinは完全に別のロジック。Right Joinでマッチした行はすべて出力する。

---

#### ドラッグ&ドロップ実装

```javascript
function setupFileDrop(dropZoneId, fileInputId, fileNameId, onFileLoaded) {
  const dropZone = document.getElementById(dropZoneId);
  const fileInput = document.getElementById(fileInputId);

  // ドラッグオーバー
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
  });

  // ドラッグ離脱
  dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
  });

  // ドロップ
  dropZone.addEventListener('drop', async (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.name.endsWith('.csv')) {
        document.getElementById(fileNameId).textContent = file.name;
        const text = await readFile(file);
        onFileLoaded(file, text);
      } else {
        alert('CSVファイルを選択してください。');
      }
    }
  });

  // ファイル選択
  fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
      document.getElementById(fileNameId).textContent = file.name;
      const text = await readFile(file);
      onFileLoaded(file, text);
    }
  });
}

function readFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.onerror = reject;
    reader.readAsText(file, 'utf-8');
  });
}
```

**CSSスタイル**:
```css
.file-drop-zone {
  border: 2px dashed #ccc;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.file-drop-zone.drag-over {
  background-color: #e8f5e9;
  border-color: #4caf50;
}
```

---

#### CSV出力（BOM付きUTF-8）

```javascript
function downloadCSV(data, filename) {
  // CSVテキストを生成
  const csvText = data.map(row =>
    row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
  ).join('\n');

  // BOM付きUTF-8
  const bom = new Uint8Array([0xEF, 0xBB, 0xBF]);
  const blob = new Blob([bom, csvText], { type: 'text/csv;charset=utf-8;' });

  // ダウンロード
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
}
```

---

### 2. Pythonスクリプト（run.py）

#### 主要機能

1. **コマンドライン引数処理**:
```python
import sys

config_path = sys.argv[1] if len(sys.argv) > 1 else None
```

2. **設定ファイル自動検出**:
```python
def load_config(config_path=None):
    if config_path is None:
        json_files = [f for f in os.listdir('.') if f.endswith('.json')]

        if not json_files:
            print("❌ エラー: 設定ファイルが見つかりません")
            sys.exit(1)

        if len(json_files) == 1:
            config_path = json_files[0]
            print(f"📄 設定ファイルを自動検出: {config_path}")
        else:
            print("❌ エラー: 複数の設定ファイルが見つかりました")
            print("使い方: python run.py [設定ファイル名]")
            sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
```

3. **フォルダ自動作成**:
```python
def ensure_directories():
    os.makedirs('input', exist_ok=True)
    os.makedirs('output', exist_ok=True)
```

4. **入力ファイル検索**:
```python
def find_input_file(file_name):
    # カレントディレクトリを優先
    if os.path.exists(file_name):
        return file_name

    # input/ ディレクトリを確認
    input_path = os.path.join('input', file_name)
    if os.path.exists(input_path):
        return input_path

    return None
```

5. **CSV結合処理**:
- WebUI版と同じロジックを実装
- Inner/Left/Right/Outer Join対応
- 1対多の結合に対応

6. **データ検証**:
- 空白キーチェック
- 重複キーチェック
- カラム数不一致チェック

7. **変換ルール適用**:
```python
def apply_conversion_rules(data, rules):
    headers = data[0]
    column_indices = {header: idx for idx, header in enumerate(headers)}

    for rule in rules:
        col_idx = column_indices.get(rule['column'])
        if col_idx is not None:
            for row in data[1:]:
                if col_idx < len(row) and row[col_idx] == rule['from']:
                    row[col_idx] = rule['to']

    return data
```

8. **重複行除去**:
```python
def remove_duplicates(data):
    seen = set()
    unique = [data[0]]  # ヘッダー

    for row in data[1:]:
        key = '|'.join(row)
        if key not in seen:
            seen.add(key)
            unique.append(row)

    return unique, len(data) - len(unique)
```

9. **CSV出力（BOM付きUTF-8）**:
```python
with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data)
```

10. **実行ログ保存**:
```python
def save_log(config_name, file_a, file_b, output_rows, warnings, removed_count, output_file):
    log_path = 'output/run_log.csv'

    if not os.path.exists(log_path):
        with open(log_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['実行日時', '設定名', 'ファイルA', 'ファイルB', '出力行数', '警告有無', '重複除去', '出力ファイル'])

    with open(log_path, 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            config_name,
            file_a,
            file_b,
            output_rows,
            'あり' if warnings else 'なし',
            f'{removed_count}行' if removed_count > 0 else 'なし',
            output_file
        ])
```

---

### 3. Windows用バッチファイル（run.bat）

```batch
@echo off
chcp 65001 >nul
cls

echo ================================================================
echo CSV結合・変換ツール - Pythonスクリプト版
echo ================================================================
echo.

REM Pythonがインストールされているか確認
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ エラー: Pythonがインストールされていません。
    echo.
    echo Pythonをインストールしてください：
    echo https://www.python.org/downloads/
    echo.
    echo インストール時は「Add Python to PATH」にチェックを入れてください。
    echo.
    pause
    exit /b 1
)

REM Python スクリプトを実行（引数があればそのまま渡す）
if "%~1"=="" (
    python run.py
) else (
    python run.py %*
)
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% equ 0 (
    echo ✅ 処理が正常に完了しました。
) else (
    echo ❌ 処理がエラーで終了しました。
)
echo.

pause
exit /b %EXIT_CODE%
```

---

### 4. テストデータ

#### test_a.csv（社員マスタ）
```csv
社員ID,氏名,部署,入社年度
001,山田太郎,営業部,2020
002,佐藤花子,開発部,2019
003,鈴木一郎,営業部,2021
004,田中美咲,総務部,2018
005,高橋健太,開発部,2022
006,伊藤千代,営業部,2020
007,渡辺次郎,開発部,2019
009,中村真理,総務部,2021
008,小林優子,営業部,2023
```

#### test_b.csv（売上データ）
```csv
社員ID,売上金額,達成率,評価
001,5000000,120,1
002,4500000,110,1
004,3800000,95,2
005,6200000,135,1
006,4200000,105,2
008,3500000,88,3
009,5500000,125,1
005,7200000,135,1
005,8200000,135,1
```

**注意**:
- 005が3行重複（1対多のテスト）
- 003と007はtest_bに存在しない
- 009はtest_aに存在しない（Outer/Right Joinテスト用）
- 評価は1/2/3（変換ルールで「優」「良」「可」に変換）

#### test_single.csv（カラム整形用）
```csv
ID,名前,年齢,部署,役職,入社日,給与,評価
001,山田太郎,35,営業部,課長,2015-04-01,600000,A
002,佐藤花子,28,開発部,主任,2018-04-01,500000,B
003,鈴木一郎,42,営業部,部長,2010-04-01,800000,A
004,田中美咲,31,総務部,係長,2016-04-01,550000,B
005,高橋健太,26,開発部,一般,2020-04-01,450000,C
006,伊藤千代,38,営業部,課長,2012-04-01,650000,A
007,渡辺次郎,33,開発部,主任,2015-04-01,520000,B
008,小林優子,29,営業部,一般,2019-04-01,480000,C
009,中村真理,45,総務部,部長,2008-04-01,850000,A
010,山本健,27,開発部,一般,2021-04-01,440000,C
001,山田太郎,35,営業部,課長,2015-04-01,600000,A
002,佐藤花子,28,開発部,主任,2018-04-01,500000,B
003,鈴木一郎,42,営業部,部長,2010-04-01,800000,A
004,田中美咲,31,総務部,係長,2016-04-01,550000,B
```

**注意**: 001-004が重複（重複除去テスト用）

---

### 5. 設定ファイル例（settings.json）

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
    },
    {
      "source": "A",
      "original": "氏名",
      "name": "氏名",
      "index": 1,
      "selected": true
    },
    {
      "source": "A",
      "original": "部署",
      "name": "部署",
      "index": 2,
      "selected": true
    },
    {
      "source": "A",
      "original": "入社年度",
      "name": "入社年度",
      "index": 3,
      "selected": true
    },
    {
      "source": "B",
      "original": "社員ID",
      "name": "社員ID_B",
      "index": 0,
      "selected": false
    },
    {
      "source": "B",
      "original": "売上金額",
      "name": "売上金額",
      "index": 1,
      "selected": true
    },
    {
      "source": "B",
      "original": "達成率",
      "name": "達成率",
      "index": 2,
      "selected": true
    },
    {
      "source": "B",
      "original": "評価",
      "name": "評価",
      "index": 3,
      "selected": true
    }
  ],
  "rules": [
    {
      "column": "評価",
      "from": "1",
      "to": "優"
    },
    {
      "column": "評価",
      "from": "2",
      "to": "良"
    },
    {
      "column": "評価",
      "from": "3",
      "to": "可"
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

---

### 6. 重要な実装ポイント

#### ポイント1: 実行モードのファイル管理
グローバル変数を使用してファイルを管理：
```javascript
let executeFileA = null;
let executeFileB = null;

// ファイル選択時
document.getElementById('execute-file-a').addEventListener('change', (e) => {
  executeFileA = e.target.files[0];
});

// ドラッグ&ドロップ時
setupFileDrop('execute-drop-a', 'execute-file-a', 'execute-file-a-name', (file, text) => {
  executeFileA = file;
  // データ読込処理
});

// 実行時
document.getElementById('execute-run').addEventListener('click', () => {
  if (!executeFileA || !executeFileB) {
    alert('両方のCSVファイルを選択してください。');
    return;
  }
  // 実行処理
});
```

#### ポイント2: ワンクリック実行モードのデータ保存
実行モードで実行成功時：
```javascript
lastExecutionData = {
  setting: setting,
  fileA: executeFileA,
  fileB: executeFileB,
  fileNameA: executeFileA.name,
  fileNameB: executeFileB.name,
  dataA: dataA,
  dataB: dataB
};
```

#### ポイント3: Right Joinの実装
Right JoinとOuter Joinを完全に分離：
```javascript
if (joinType === 'right') {
  // A側をHashMapに変換
  const mapA = {};
  for (const rowA of dataA.slice(1)) {
    const key = rowA[keyA];
    if (!mapA[key]) mapA[key] = [];
    mapA[key].push(rowA);
  }

  // B側をループ
  for (const rowB of dataB.slice(1)) {
    const key = rowB[keyB];
    const rowsA = mapA[key] || [];

    if (rowsA.length > 0) {
      // マッチする行をすべて出力
      for (const rowA of rowsA) {
        output.push(combineRow(rowA, rowB, columns));
      }
    } else {
      // マッチしない行も出力
      output.push(combineRow(null, rowB, columns));
    }
  }
}
```

#### ポイント4: カラムのドラッグ&ドロップ並び替え
```javascript
let draggedElement = null;

columnList.addEventListener('dragstart', (e) => {
  draggedElement = e.target;
  e.target.style.opacity = '0.5';
});

columnList.addEventListener('dragend', (e) => {
  e.target.style.opacity = '';
});

columnList.addEventListener('dragover', (e) => {
  e.preventDefault();
  const afterElement = getDragAfterElement(columnList, e.clientY);
  if (afterElement == null) {
    columnList.appendChild(draggedElement);
  } else {
    columnList.insertBefore(draggedElement, afterElement);
  }
});

function getDragAfterElement(container, y) {
  const draggableElements = [...container.querySelectorAll('.column-item:not(.dragging)')];

  return draggableElements.reduce((closest, child) => {
    const box = child.getBoundingClientRect();
    const offset = y - box.top - box.height / 2;

    if (offset < 0 && offset > closest.offset) {
      return { offset: offset, element: child };
    } else {
      return closest;
    }
  }, { offset: Number.NEGATIVE_INFINITY }).element;
}
```

---

### 7. 期待される出力例

#### Left Join（test_a.csv + test_b.csv）
- 出力行数: 11行（ヘッダー含む、データ10行）
- 005が3行（1対多）
- 003と007はB側が空白

#### Inner Join（test_a.csv + test_b.csv）
- 出力行数: 8行（ヘッダー含む、データ7行）
- 003と007は出力されない
- 009も出力されない（Aに存在しない）

#### Right Join（test_a.csv + test_b.csv）
- 出力行数: 10行（ヘッダー含む、データ9行）
- B側の全行が出力される
- 009のA側カラムは空白

#### Outer Join（test_a.csv + test_b.csv）
- 出力行数: 12行（ヘッダー含む、データ11行）
- AとBの全行が出力される
- 003と007はB側が空白、009はA側が空白

---

### 8. README作成

以下の内容でREADME.mdとREADME_python.mdを作成してください。

**README.md**: Webアプリケーション版の使い方

**README_python.md**: Pythonスクリプト版の使い方（超シンプルな使用手順、フォルダ構成、トラブルシューティング）

---

### 9. 追加要件

1. **.gitignore**を作成し、`output/*.csv`を除外（`output/`ディレクトリは残す）
2. すべてのコードに適切なコメントを追加
3. エラーハンドリングを実装（ファイル読込エラー、CSV解析エラーなど）
4. ユーザーフィードバック（処理中表示、成功・エラーメッセージ）
5. レスポンシブデザイン（モバイル対応は不要だが、可読性を確保）

---

## 実装順序の推奨

1. **Webアプリケーションのベース**
   - HTML構造、タブ切り替え、基本的なCSS

2. **定義モード**
   - ファイル選択、ドラッグ&ドロップ
   - 結合キー・結合方式選択
   - カラムリスト表示

3. **CSV結合ロジック**
   - Inner/Left/Right/Outer Join実装
   - データ検証
   - 変換ルール

4. **実行モード**
   - グローバル変数でファイル管理
   - 結合実行
   - プレビュー表示
   - lastExecutionDataの保存

5. **ワンクリック実行モード**
   - lastExecutionDataの読込
   - 前回実行情報表示
   - ワンクリック実行

6. **カラム整形モード**
   - 単一CSV処理

7. **実行ログモード**
   - LocalStorageからログ読込・表示

8. **Pythonスクリプト**
   - 設定ファイル読込
   - CSV結合ロジック（Webと同一）
   - 実行ログ出力

9. **テストデータ作成**
   - test_a.csv、test_b.csv、test_single.csv

10. **ドキュメント作成**
    - README.md、README_python.md

---

## 完成チェックリスト

- [ ] index.html（単一ファイル、外部ライブラリなし）
- [ ] run.py（Python標準ライブラリのみ）
- [ ] run.bat（Windows用）
- [ ] test_a.csv（9行）
- [ ] test_b.csv（10行、重複あり）
- [ ] test_single.csv（15行、重複あり）
- [ ] settings.json（サンプル設定）
- [ ] README.md
- [ ] README_python.md
- [ ] .gitignore
- [ ] タブが5つ（定義、実行、ワンクリック、整形、ログ）
- [ ] ドラッグ&ドロップ対応（定義、実行、整形）
- [ ] 新規作成ボタン（定義モード）
- [ ] Inner/Left/Right/Outer Join実装
- [ ] 実行モードでグローバル変数を使用
- [ ] ワンクリック実行モードでlastExecutionDataを使用
- [ ] BOM付きUTF-8出力
- [ ] LocalStorage保存（設定、ログ）
- [ ] 実行ログCSV出力（Python版）
- [ ] フォルダ自動作成（Python版）
- [ ] 設定ファイル自動検出（Python版）

---

このプロンプトをAIアシスタントに与えることで、プロジェクト全体を再現できます。
