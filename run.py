#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV結合・変換ツール - Pythonスクリプト版
ブラウザからエクスポートした設定を使用して、CSVファイルを結合・変換します。

使い方:
    python run.py [設定ファイル名]

    例: python run.py settings.json
        python run.py テスト設定01.json
"""

import csv
import json
import os
import sys
from datetime import datetime
from collections import defaultdict


def ensure_directories():
    """必要なディレクトリを自動作成"""
    os.makedirs('input', exist_ok=True)
    os.makedirs('output', exist_ok=True)


def load_config(config_path=None):
    """設定ファイルを読み込む"""
    # 引数で指定されていない場合、デフォルトのファイル名を探す
    if config_path is None:
        # カレントディレクトリの .json ファイルを探す
        json_files = [f for f in os.listdir('.') if f.endswith('.json')]

        if not json_files:
            print("❌ エラー: 設定ファイルが見つかりません")
            print()
            print("使い方:")
            print("  python run.py [設定ファイル名]")
            print()
            print("例:")
            print("  python run.py settings.json")
            print("  python run.py テスト設定01.json")
            print()
            print("または、カレントディレクトリに .json ファイルを配置してください。")
            sys.exit(1)

        if len(json_files) == 1:
            config_path = json_files[0]
            print(f"📄 設定ファイルを自動検出: {config_path}")
        else:
            print("❌ エラー: 複数の設定ファイルが見つかりました")
            print()
            print("以下のファイルから1つを選んで指定してください:")
            for f in json_files:
                print(f"  - {f}")
            print()
            print("使い方: python run.py [設定ファイル名]")
            sys.exit(1)

    if not os.path.exists(config_path):
        print(f"❌ エラー: 設定ファイルが見つかりません: {config_path}")
        print()
        print("ブラウザで設定を作成し、JSONエクスポートしてください。")
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 設定ファイルを読み込みました: {config['name']}")
        return config
    except Exception as e:
        print(f"❌ エラー: 設定ファイルの読み込みに失敗しました: {e}")
        sys.exit(1)


def find_input_file(file_name):
    """入力ファイルを探す（カレントディレクトリ → input/ の順）"""
    # カレントディレクトリを優先
    if os.path.exists(file_name):
        return file_name

    # input/ ディレクトリを確認
    input_path = os.path.join('input', file_name)
    if os.path.exists(input_path):
        return input_path

    return None


def load_csv(file_name):
    """CSVファイルを読み込む"""
    file_path = find_input_file(file_name)

    if file_path is None:
        print(f"❌ エラー: ファイルが見つかりません: {file_name}")
        print(f"   カレントディレクトリまたは input/ フォルダに配置してください。")
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            data = list(reader)
        print(f"✅ CSVファイルを読み込みました: {file_path} ({len(data)-1}行)")
        return data
    except Exception as e:
        print(f"❌ エラー: CSVファイルの読み込みに失敗しました: {e}")
        sys.exit(1)


def validate_data(data_a, data_b, config):
    """データ検証を実行"""
    warnings = []
    validation = config.get('validation', {})
    key_a = int(config['keyA'])
    key_b = int(config['keyB'])

    # 空白キーチェック
    if validation.get('checkBlank', False):
        blank_count_a = sum(1 for row in data_a[1:] if not row[key_a].strip())
        blank_count_b = sum(1 for row in data_b[1:] if not row[key_b].strip())

        if blank_count_a > 0:
            warnings.append(f"CSV Aの結合キーに空白が{blank_count_a}件あります")
        if blank_count_b > 0:
            warnings.append(f"CSV Bの結合キーに空白が{blank_count_b}件あります")

    # 重複キーチェック
    if validation.get('checkDuplicate', False):
        keys_a = [row[key_a] for row in data_a[1:]]
        keys_b = [row[key_b] for row in data_b[1:]]

        dup_count_a = len(keys_a) - len(set(keys_a))
        dup_count_b = len(keys_b) - len(set(keys_b))

        if dup_count_a > 0:
            warnings.append(f"CSV Aの結合キーに重複が{dup_count_a}件あります")
        if dup_count_b > 0:
            warnings.append(f"CSV Bの結合キーに重複が{dup_count_b}件あります")

    # カラム数不一致チェック
    if validation.get('checkColumnCount', False):
        col_count_a = len(data_a[0])
        col_count_b = len(data_b[0])

        mismatch_a = sum(1 for row in data_a[1:] if len(row) != col_count_a)
        mismatch_b = sum(1 for row in data_b[1:] if len(row) != col_count_b)

        if mismatch_a > 0:
            warnings.append(f"CSV Aにカラム数不一致の行が{mismatch_a}件あります")
        if mismatch_b > 0:
            warnings.append(f"CSV Bにカラム数不一致の行が{mismatch_b}件あります")

    if warnings:
        print("⚠️  警告:")
        for warning in warnings:
            print(f"   - {warning}")

    return warnings


def perform_join(data_a, data_b, config):
    """CSV結合を実行"""
    key_a = int(config['keyA'])
    key_b = int(config['keyB'])
    join_type = config['joinType']
    columns = config['columns']

    # B側をマップに変換
    map_b = defaultdict(list)
    for row in data_b[1:]:
        if key_b < len(row):
            key = row[key_b]
            map_b[key].append(row)

    result = []
    matched_keys_b = set()

    # 出力ヘッダー
    output_headers = [col['name'] for col in columns if col.get('selected', True)]
    result.append(output_headers)

    # Inner/Left/Outer Join
    if join_type in ['inner', 'left', 'outer']:
        for row_a in data_a[1:]:
            if key_a >= len(row_a):
                continue

            key = row_a[key_a]
            rows_b = map_b.get(key, [])

            if rows_b:
                for row_b in rows_b:
                    output_row = []
                    for col in columns:
                        if not col.get('selected', True):
                            continue

                        if col['source'] == 'A':
                            idx = col['index']
                            output_row.append(row_a[idx] if idx < len(row_a) else '')
                        else:
                            idx = col['index']
                            output_row.append(row_b[idx] if idx < len(row_b) else '')

                    result.append(output_row)
                matched_keys_b.add(key)
            elif join_type in ['left', 'outer']:
                output_row = []
                for col in columns:
                    if not col.get('selected', True):
                        continue

                    if col['source'] == 'A':
                        idx = col['index']
                        output_row.append(row_a[idx] if idx < len(row_a) else '')
                    else:
                        output_row.append('')

                result.append(output_row)

    # Right Join
    if join_type == 'right':
        # A側をマップに変換
        map_a = defaultdict(list)
        for row in data_a[1:]:
            if key_a < len(row):
                key = row[key_a]
                map_a[key].append(row)

        for row_b in data_b[1:]:
            if key_b >= len(row_b):
                continue

            key = row_b[key_b]
            rows_a = map_a.get(key, [])

            if rows_a:
                for row_a in rows_a:
                    output_row = []
                    for col in columns:
                        if not col.get('selected', True):
                            continue

                        if col['source'] == 'A':
                            idx = col['index']
                            output_row.append(row_a[idx] if idx < len(row_a) else '')
                        else:
                            idx = col['index']
                            output_row.append(row_b[idx] if idx < len(row_b) else '')

                    result.append(output_row)
            else:
                output_row = []
                for col in columns:
                    if not col.get('selected', True):
                        continue

                    if col['source'] == 'B':
                        idx = col['index']
                        output_row.append(row_b[idx] if idx < len(row_b) else '')
                    else:
                        output_row.append('')

                result.append(output_row)

    # Outer Join: B側の未マッチ行を追加
    if join_type == 'outer':
        for row_b in data_b[1:]:
            if key_b >= len(row_b):
                continue

            key = row_b[key_b]
            if key in matched_keys_b:
                continue

            output_row = []
            for col in columns:
                if not col.get('selected', True):
                    continue

                if col['source'] == 'B':
                    idx = col['index']
                    output_row.append(row_b[idx] if idx < len(row_b) else '')
                else:
                    output_row.append('')

            result.append(output_row)

    print(f"✅ 結合完了: {len(result)-1}行出力")
    return result


def apply_conversion_rules(data, rules):
    """変換ルールを適用"""
    if not rules:
        return data

    headers = data[0]
    column_indices = {header: idx for idx, header in enumerate(headers)}

    converted_count = 0
    for rule in rules:
        if not rule.get('column') or not rule.get('from'):
            continue

        col_idx = column_indices.get(rule['column'])
        if col_idx is None:
            continue

        for row in data[1:]:
            if col_idx < len(row) and row[col_idx] == rule['from']:
                row[col_idx] = rule['to']
                converted_count += 1

    if converted_count > 0:
        print(f"✅ 変換ルール適用: {converted_count}件変換")

    return data


def remove_duplicates(data):
    """重複行を除去"""
    seen = set()
    unique = [data[0]]  # ヘッダーは残す

    for row in data[1:]:
        key = '|'.join(row)
        if key not in seen:
            seen.add(key)
            unique.append(row)

    removed_count = len(data) - len(unique)
    if removed_count > 0:
        print(f"✅ 重複行除去: {removed_count}行除去")

    return unique, removed_count


def save_csv(data, output_path):
    """CSVファイルを保存（BOM付きUTF-8）"""
    try:
        # output ディレクトリが存在しない場合は作成
        os.makedirs('output', exist_ok=True)

        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        print(f"✅ CSVファイルを保存しました: {output_path}")
        return True
    except Exception as e:
        print(f"❌ エラー: CSVファイルの保存に失敗しました: {e}")
        return False


def save_log(config_name, file_a, file_b, output_rows, warnings, removed_count, output_file):
    """実行ログを保存"""
    # output ディレクトリが存在しない場合は作成
    os.makedirs('output', exist_ok=True)

    log_path = 'output/run_log.csv'

    # ログファイルが存在しない場合はヘッダーを作成
    if not os.path.exists(log_path):
        with open(log_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['実行日時', '設定名', 'ファイルA', 'ファイルB', '出力行数', '警告有無', '重複除去', '出力ファイル'])

    # ログを追記
    try:
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
        print(f"✅ 実行ログを保存しました: {log_path}")
    except Exception as e:
        print(f"⚠️  警告: 実行ログの保存に失敗しました: {e}")


def main():
    """メイン処理"""
    print("=" * 60)
    print("CSV結合・変換ツール - Pythonスクリプト版")
    print("=" * 60)
    print()

    # 必要なディレクトリを作成
    ensure_directories()

    # コマンドライン引数から設定ファイルを取得
    config_path = sys.argv[1] if len(sys.argv) > 1 else None

    # 設定ファイルを読み込む
    config = load_config(config_path)

    # 入力ファイルパスを取得
    file_a_name = config.get('fileNameA', 'input_a.csv')
    file_b_name = config.get('fileNameB', 'input_b.csv')

    # CSVファイルを読み込む
    print("📂 CSVファイルを読み込んでいます...")
    data_a = load_csv(file_a_name)
    data_b = load_csv(file_b_name)
    print()

    # データ検証
    print("🔍 データ検証中...")
    warnings = validate_data(data_a, data_b, config)
    print()

    # 結合実行
    print("🔄 CSV結合を実行中...")
    result = perform_join(data_a, data_b, config)
    print()

    # 変換ルール適用
    if config.get('rules'):
        print("🔧 変換ルールを適用中...")
        result = apply_conversion_rules(result, config['rules'])
        print()

    # 重複行除去
    removed_count = 0
    if config.get('validation', {}).get('removeDuplicates', False):
        print("🗑️  重複行を除去中...")
        result, removed_count = remove_duplicates(result)
        print()

    # 出力ファイル名を生成
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_base = config.get('name', 'output').replace(' ', '_')
    output_file = f"{output_base}_{timestamp}.csv"
    output_path = os.path.join('output', output_file)

    # CSVファイルを保存
    print("💾 CSVファイルを保存中...")
    if save_csv(result, output_path):
        print()

        # 実行ログを保存
        print("📝 実行ログを保存中...")
        save_log(
            config['name'],
            file_a_name,
            file_b_name,
            len(result) - 1,
            warnings,
            removed_count,
            output_file
        )
        print()

        # 結果サマリー
        print("=" * 60)
        print("✨ 処理完了")
        print("=" * 60)
        print(f"📄 出力ファイル: {output_path}")
        print(f"📊 出力行数: {len(result)-1}行")
        print(f"📊 出力カラム数: {len(result[0])}列")
        if removed_count > 0:
            print(f"🗑️  重複除去: {removed_count}行")
        if warnings:
            print(f"⚠️  警告: {len(warnings)}件")
        print("=" * 60)

        return 0
    else:
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  処理を中断しました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
