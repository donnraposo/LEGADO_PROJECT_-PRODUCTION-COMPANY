[CmdletBinding()]
param(
    [string]$InnoCompiler = "",
    [string]$CertificateThumbprint = ""
)

$ErrorActionPreference = "Stop"
$agentDir = $PSScriptRoot
$python = Join-Path $agentDir ".venv\Scripts\python.exe"
$spec = Join-Path $agentDir "packaging\legado-agent.spec"
$distDir = Join-Path $agentDir "dist"
$workDir = Join-Path $agentDir "build"
$installerScript = Join-Path $agentDir "packaging\legado-agent.iss"
$releaseDir = Join-Path $agentDir "release"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Ambiente de construção não encontrado: $python"
}

if (-not $InnoCompiler) {
    $compilerCandidates = @(
        "$env:LOCALAPPDATA\Programs\Inno Setup 7\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 7\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 7\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
    )
    $InnoCompiler = $compilerCandidates |
        Where-Object { $_ -and (Test-Path -LiteralPath $_) } |
        Select-Object -First 1
}

if (-not $InnoCompiler -or -not (Test-Path -LiteralPath $InnoCompiler)) {
    throw "Compilador Inno Setup não encontrado. Instale o Inno Setup 7 ou informe -InnoCompiler."
}

& $python -m PyInstaller --noconfirm --clean `
    --distpath $distDir --workpath $workDir $spec
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao gerar o aplicativo autocontido."
}

& $InnoCompiler $installerScript
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao gerar o instalador."
}

$installer = Get-ChildItem -LiteralPath $releaseDir -Filter "LegadoAgent-Setup-*.exe" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if (-not $installer) {
    throw "O instalador não foi encontrado após a compilação."
}

if ($CertificateThumbprint) {
    $signTool = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin" `
        -Filter signtool.exe -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match '\\x64\\signtool\.exe$' } |
        Sort-Object FullName -Descending |
        Select-Object -First 1
    if (-not $signTool) {
        throw "SignTool não encontrado; instale o Windows SDK para assinar o instalador."
    }
    & $signTool.FullName sign /sha1 $CertificateThumbprint /fd SHA256 `
        /tr http://timestamp.digicert.com /td SHA256 $installer.FullName
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao assinar o instalador."
    }
}

Write-Output $installer.FullName
