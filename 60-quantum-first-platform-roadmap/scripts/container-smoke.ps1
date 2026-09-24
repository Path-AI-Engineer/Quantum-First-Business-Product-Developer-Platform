$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$compose = Join-Path $root "compose.yaml"

docker info *> $null
if ($LASTEXITCODE -ne 0) { throw "Docker Desktop Linux engine is not ready." }

try {
    docker compose -f $compose up --build --detach
    if ($LASTEXITCODE -ne 0) { throw "Container startup failed with exit code $LASTEXITCODE." }

    $apiReady = $false
    $webReady = $false
    for ($attempt = 1; $attempt -le 36; $attempt++) {
        try {
            $api = Invoke-RestMethod -Uri "http://127.0.0.1:8060/health" -TimeoutSec 3
            $apiReady = $api.status -eq "ok"
        } catch { $apiReady = $false }
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:8960" -UseBasicParsing -TimeoutSec 3
            $webReady = $response.StatusCode -eq 200
        } catch { $webReady = $false }
        if ($apiReady -and $webReady) { break }
        Start-Sleep -Seconds 5
    }
    if (-not ($apiReady -and $webReady)) {
        docker compose -f $compose ps
        docker compose -f $compose logs --tail 120 api portal
        throw "Project 60 containers did not become healthy."
    }
    $roadmap = Invoke-RestMethod -Uri "http://127.0.0.1:8060/v1/roadmap" -TimeoutSec 10
    if ($roadmap.approval_status -ne "technical_candidate_unapproved") { throw "Runtime truth boundary mismatch." }
    Write-Host "Project 60 container smoke passed." -ForegroundColor Green
}
finally {
    docker compose -f $compose down --volumes
}

