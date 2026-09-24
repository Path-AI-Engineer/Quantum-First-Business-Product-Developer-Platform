$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
docker info *> $null
if ($LASTEXITCODE -ne 0) { throw "Docker Desktop Linux engine is unavailable." }
try {
    docker compose -f "$root\compose.yaml" up --build --detach
    if ($LASTEXITCODE -ne 0) { throw "Container startup failed." }
    $health = $null
    $portal = $null
    for ($attempt = 1; $attempt -le 30; $attempt++) {
        try {
            $health = Invoke-RestMethod -Uri "http://127.0.0.1:8059/health" -TimeoutSec 3
            $portal = Invoke-WebRequest -Uri "http://127.0.0.1:8959" -TimeoutSec 3 -UseBasicParsing
            break
        }
        catch {
            if ($attempt -eq 30) {
                docker compose -f "$root\compose.yaml" ps
                docker compose -f "$root\compose.yaml" logs api portal --tail 100
                throw
            }
            Start-Sleep -Seconds 1
        }
    }
    if ($health.status -ne "ok" -or $portal.StatusCode -ne 200) { throw "Container health validation failed." }
    Write-Host "Project 59 container smoke passed." -ForegroundColor Green
}
finally {
    docker compose -f "$root\compose.yaml" down --volumes
}
