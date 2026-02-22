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
