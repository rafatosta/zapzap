$ErrorActionPreference = "Stop"

Write-Host "# === Windows Builder ==="

$AppName = "ZapZap"

# Generated Qt Python files now live in zapzap/ui/generated and are committed.
# Keep this list for future .ui sources, but do not point to removed legacy paths.
$UiFiles = @()

$AdditionalData = @(
    @("zapzap/po", "zapzap/po"),
    @("zapzap/assets", "zapzap/assets"),
    @("zapzap/features/browser/web/scripts", "zapzap/features/browser/web/scripts")
)

Write-Host "# === Instalando dependências ==="
python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install -r requirements.txt

if ($UiFiles.Count -gt 0) {
    Write-Host "# === Compilando arquivos .ui ==="

    foreach ($item in $UiFiles) {
        $source = $item[0]
        $target = $item[1]

        if (-not (Test-Path $source)) {
            Write-Host "[IGNORADO] $source"
            continue
        }

        Write-Host "$source -> $target"

        python -m PyQt6.uic.pyuic -x $source -o $target
    }
} else {
    Write-Host "# === Nenhum arquivo .ui para compilar ==="
}

Write-Host "# === Limpando builds anteriores ==="

if (Test-Path "dist") {
    Remove-Item "dist" -Recurse -Force
}

if (Test-Path "build") {
    Remove-Item "build" -Recurse -Force
}

Write-Host "# === Executando PyInstaller ==="

$Args = @(
    "--name", $AppName,
    "--onefile",
    "--windowed",
    "--noconfirm"
)

foreach ($item in $AdditionalData) {
    $source = $item[0]
    $target = $item[1]

    if (-not (Test-Path $source)) {
        throw "Arquivo ou diretório de dados não encontrado: $source"
    }

    $Args += "--add-data"
    $Args += "$source;$target"
}

$Args += "zapzap/__main__.py"

python -m PyInstaller @Args

Write-Host "# === Renomeando executável ==="

$VersionLine = Get-Content "zapzap/__init__.py" | Where-Object {
    $_ -match "^__version__"
} | Select-Object -First 1

if ($VersionLine -match "=\s*['""]([^'""]+)['""]") {
    $Version = $Matches[1]
} else {
    $Version = "dev"
}

$ExePath = "dist/ZapZap.exe"
$FinalPath = "dist/ZapZap-$Version-windows-x86_64.exe"

if (-not (Test-Path $ExePath)) {
    throw "Executável não encontrado: $ExePath"
}

if (Test-Path $FinalPath) {
    Remove-Item $FinalPath -Force
}

Move-Item -Path $ExePath -Destination $FinalPath -Force

Write-Host "Executável gerado: $FinalPath"
