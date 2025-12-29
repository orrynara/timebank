Param(
    [string]$OutputDir = "dist",
    [string]$Name = "CanvasToon_Builder",
    [int]$Port = 8501
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot ".."))
Set-Location $Root

Write-Host "[1/4] Installing build deps (pyinstaller)..."
python -m pip install -U pip
python -m pip install pyinstaller

Write-Host "[2/4] Preparing icon (.ico)..."
$IcoPath = Join-Path $Root "assets\app.ico"
if (-not (Test-Path $IcoPath)) {
    Write-Host "  assets/app.ico not found. Trying to generate it from an existing image..." -ForegroundColor Yellow

    $Candidates = @(
        (Join-Path $Root "cut_01.png"),
        (Join-Path $Root "test_character\DURICO HOME.png"),
        (Join-Path $Root "test_character\MONKEY.png"),
        (Join-Path $Root "test_character\KIN_KONG.png")
    )

    $Src = $null
    foreach ($c in $Candidates) {
        if (Test-Path $c) { $Src = $c; break }
    }

    if ($Src) {
        Write-Host "  Using: $Src"
        python -m pip install pillow
        python (Join-Path $Root "scripts\make_app_icon.py") --src "$Src" --dst "$IcoPath"
    } else {
        Write-Host "  No suitable image found for icon generation." -ForegroundColor Yellow
    }
}

if (Test-Path $IcoPath) {
    $IconArg = @("--icon", $IcoPath)
} else {
    Write-Host "  Building without icon." -ForegroundColor Yellow
    $IconArg = @()
}

Write-Host "[3/4] Building onedir exe..."
# 내부 번들로 포함될 파일/폴더들:
# - .env (민감정보) : 내부에서만 사용 (dist 루트에 노출되지 않음)
# - launcher.py, ui/, modules/, assets/, projects/ 등 런타임 필요 파일
# - portable_entry.py : 엔트리

$EnvPath = Join-Path $Root ".env"
if (-not (Test-Path $EnvPath)) {
    throw "Missing .env at repo root. For internal portable build, .env is required."
}

$AddData = @(
    "launcher.py;app",
    ".env;data/.env",
    "ui;ui",
    "modules;modules",
    "assets;app/assets",
    "projects;app/projects"
)

# tkinter는 표준 라이브러리지만, 런타임에 Tcl/Tk 데이터 디렉터리가 필요하다.
# 빌드 머신의 Python에서 Tcl 루트(<Python>\tcl)를 탐지해 dist/_internal/tcl로 포함한다.
Write-Host "Detecting Tcl/Tk runtime for tkinter..."
try {
    $TclRoot = (python -c "import tkinter; from pathlib import Path; t=tkinter.Tcl(); p=Path(t.eval('info library')).resolve(); print(str(p.parent))")
    $TclRoot = ($TclRoot | Out-String).Trim()
} catch {
    $TclRoot = ""
}

if ($TclRoot -and (Test-Path $TclRoot)) {
    Write-Host "  Tcl root detected: $TclRoot"
    $AddData += @("$TclRoot;tcl")
} else {
    Write-Host "  WARNING: Tcl root not detected. tkinter runtime may fail on other PCs." -ForegroundColor Yellow
}

$AddArgs = @()
foreach ($d in $AddData) {
    $AddArgs += @("--add-data", $d)
}

# Streamlit가 자체적으로 dynamic imports가 많아 hidden-import가 필요할 수 있음
$Hidden = @(
    "streamlit",
    "streamlit.web",
    "streamlit.web.cli",
    "streamlit.runtime",
    "streamlit.runtime.scriptrunner",
    "openai",
    "tkinter",
    "_tkinter",
    "tkinter.filedialog",
    "tkinter.ttk",
    "tkinter.messagebox",
    "tkinter.simpledialog",
    "altair",
    "pyarrow"
)
$HiddenArgs = @()
foreach ($h in $Hidden) {
    $HiddenArgs += @("--hidden-import", $h)
}

# 포트는 런타임 ENV로도 바꿀 수 있지만, 기본 8501
$Env:PORT = "$Port"

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --name $Name `
    --collect-all streamlit `
    --collect-all openai `
    --collect-all tkinter `
    @IconArg `
    @AddArgs `
    @HiddenArgs `
    portable_entry.py

Write-Host "[4/4] Done. Output at: $Root\dist\$Name\" -ForegroundColor Green
