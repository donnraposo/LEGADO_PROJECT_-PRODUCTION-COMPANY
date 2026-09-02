param(
    [Parameter(Mandatory = $true)][string]$Backup,
    [Parameter(Mandatory = $true)][ValidateSet("RESTAURAR")][string]$ConfirmRestore,
    [string]$AgentDatabase = ""
)

$ErrorActionPreference = "Stop"
$backupRoot = (Resolve-Path -LiteralPath $Backup).Path
$manifestPath = Join-Path $backupRoot "manifest.json"
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { throw "Manifesto ausente." }
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
foreach ($file in $manifest.files) {
    $path = Join-Path $backupRoot $file.name
    $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $file.sha256) { throw "Integridade inválida em $($file.name)." }
}

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$composeFile = Join-Path $projectRoot "infrastructure/docker/compose.dev.yaml"
$envFile = Join-Path $projectRoot "infrastructure/docker/.env.dev"
foreach ($database in @("legado", "keycloak", "n8n")) {
    $source = Join-Path $backupRoot "$database.sql"
    Get-Content -LiteralPath $source -Raw |
        docker compose --env-file $envFile -f $composeFile exec -T postgres `
            psql -v ON_ERROR_STOP=1 -U legado -d $database
    if ($LASTEXITCODE -ne 0) { throw "Falha ao restaurar o banco $database." }
}

if ($AgentDatabase -and (Test-Path -LiteralPath (Join-Path $backupRoot "agent.sqlite3"))) {
    $agentTarget = [IO.Path]::GetFullPath($AgentDatabase)
    if ([IO.Path]::GetFileName($agentTarget) -ne "agent.sqlite3") {
        throw "O destino local deve terminar em agent.sqlite3."
    }
    Copy-Item -LiteralPath (Join-Path $backupRoot "agent.sqlite3") -Destination $agentTarget -Force
}
