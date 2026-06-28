$ErrorActionPreference = "Stop"

Write-Host "# === Windows Builder ==="

$AppName = "ZapZap"

$UiFiles = @(
    @("zapzap/ui/ui_mainwindow.ui", "zapzap/views/ui_mainwindow.py"),
    @("zapzap/ui/ui_page_general.ui", "zapzap/views/ui_page_general.py"),
    @("zapzap/ui/ui_page_network.ui", "zapzap/views/ui_page_network.py")
)

$AdditionalData = @(
    @("zapzap/po", "zapzap/po"),
    @("zapzap/ui", "zapzap/ui"),
    @("zapzap/resources", "zapzap/resources"),
    @("zapzap/webengine/webrtc_shield.js", "zapzap/webengine"),
    @("zapzap/webengine/theme_controller.js", "zapzap/webengine")
)

Write-Host "# === Instalando dependências ==="
python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install -r requirements.txt

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
    $Args += "--add-data"
    $Args += "$($item[0]);$($item[1])"
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