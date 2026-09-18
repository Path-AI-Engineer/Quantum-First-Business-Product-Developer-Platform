$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Wait-Endpoint {
    param([string]$Uri, [int]$Attempts = 40)
    for ($attempt = 0; $attempt -lt $Attempts; $attempt++) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $Uri -TimeoutSec 3
            if ($response.StatusCode -eq 200) { return }
        }
        catch { Start-Sleep -Milliseconds 500 }
    }
    throw "Endpoint did not become ready: $Uri"
}

try {
    docker compose up --build -d
    if ($LASTEXITCODE -ne 0) { throw "Container startup failed with exit code $LASTEXITCODE." }
    Wait-Endpoint 'http://127.0.0.1:8057/health'
    Wait-Endpoint 'http://127.0.0.1:3057'
    $headers = @{ 'X-Demo-Identity' = 'operations-owner'; 'Content-Type' = 'application/json' }
    $snapshot = Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8057/v1/snapshot' -Headers $headers
    if ($snapshot.instance_count -ne 90 -or $snapshot.test_locked_count -ne 24) {
        throw 'Container API did not expose the frozen 90/24 corpus.'
    }
    $proxied = Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:3057/api/v1/snapshot' -Headers $headers
    if ($proxied.instance_count -ne 90) { throw 'Web proxy did not preserve the API contract.' }
    Write-Host 'Project 57 container smoke passed.' -ForegroundColor Green
}
finally {
    docker compose down --remove-orphans
}
