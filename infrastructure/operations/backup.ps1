param(
    [Parameter(Mandatory = $true)][string]$Destination,
    [string]$AgentDatabase = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$composeFile = Join-Path $projectRoot "infrastructure/docker/compose.dev.yaml"
$envFile = Join-Path $projectRoot "infrastructure/docker/.env.dev"
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupRoot = [IO.Path]::GetFullPath((Join-Path $Destination "legado-$stamp"))
New-Item -ItemType Directory -Path $backupRoot | Out-Null

foreach ($database in @("legado", "keycloak", "n8n")) {
    $target = Join-Path $backupRoot "$database.sql"
    docker compose --env-file $envFile -f $composeFile exec -T postgres `
        pg_dump --clean --if-exists --no-owner --no-privileges -U legado $database |
        Set-Content -Encoding utf8 $target
    if ($LASTEXITCODE -ne 0) { throw "Falha ao copiar o banco $database." }
}

if ($AgentDatabase) {
    $agentSource = (Resolve-Path -LiteralPath $AgentDatabase).Path
    Copy-Item -LiteralPath $agentSource -Destination (Join-Path $backupRoot "agent.sqlite3")
}

$files = Get-ChildItem -LiteralPath $backupRoot -File
$manifest = @{
    created_at = (Get-Date).ToUniversalTime().ToString("o")
    format_version = 1
    files = @($files | ForEach-Object {
        @{ name = $_.Name; bytes = $_.Length; sha256 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
    })
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8 (Join-Path $backupRoot "manifest.json")
Write-Output $backupRoot
