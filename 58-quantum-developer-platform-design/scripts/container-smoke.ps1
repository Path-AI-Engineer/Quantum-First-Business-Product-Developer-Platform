$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

docker info *> $null
if ($LASTEXITCODE -ne 0) { throw 'Docker Desktop Linux daemon is not ready.' }
docker compose up --build --detach --wait
if ($LASTEXITCODE -ne 0) { throw "Container startup failed with exit code $LASTEXITCODE." }
try {
    $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8058/v1/health/ready' -TimeoutSec 20
    if ($health.status -ne 'ready') { throw 'API readiness response is invalid.' }
    $portal = Invoke-WebRequest -Uri 'http://127.0.0.1:3058' -UseBasicParsing -TimeoutSec 20
    if ($portal.StatusCode -ne 200) { throw 'Portal did not return HTTP 200.' }
    Write-Host 'Project 58 container integration smoke passed.' -ForegroundColor Green
}
finally {
    docker compose down --volumes
}

