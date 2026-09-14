$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$api = "http://127.0.0.1:8056"
$web = "http://127.0.0.1:3056"
$headers = @{ "x-demo-identity" = "demo-northstar-owner" }

function Wait-ApiReady {
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        try {
            $probe = Invoke-RestMethod "$api/health" -TimeoutSec 2
            if ($probe.status -eq "ok") { return }
        } catch { Start-Sleep -Seconds 1 }
    }
    throw "API did not become ready."
}

Push-Location $root
try {
    Wait-ApiReady
    $page = Invoke-WebRequest "$web/" -UseBasicParsing
    if ($page.StatusCode -ne 200) { throw "Web health check failed." }
    $assets = Invoke-RestMethod "$web/api/v1/assets" -Headers $headers
    if ($assets.Count -ne 45) { throw "Northstar tenant asset count mismatch: $($assets.Count)." }
    $otherStatus = curl.exe -sS -o NUL -w '%{http_code}' -H 'x-demo-identity: demo-northstar-owner' "$api/v1/assets/aster-asset-000"
    if ($LASTEXITCODE -ne 0 -or $otherStatus -ne "404") { throw "Cross-tenant asset was exposed or request failed." }

    $assessment = Invoke-RestMethod "$api/v1/assessments" -Method Post -Headers $headers
    $fixture = Get-Content "data\fixtures\cbom.json" -Raw | ConvertFrom-Json
    $importBody = @{ source_type = "cbom"; payload = $fixture } | ConvertTo-Json -Depth 8 -Compress
    $import = Invoke-RestMethod "$api/v1/assessments/$($assessment.id)/imports" -Method Post -Headers $headers -ContentType "application/json" -Body $importBody
    if ($import.accepted -notin @(0, 1)) { throw "Import count invalid." }
    $report = Invoke-RestMethod "$api/v1/reports" -Method Post -Headers $headers -ContentType "application/json" -Body '{"type":"executive"}'
    if ($report.asset_count -ne 45 -or $report.observation_count -lt 91) { throw "Report reconciliation failed." }
    if ($report.object_sha256 -notmatch '^[0-9a-f]{64}$') { throw "Report object digest missing." }

    docker compose restart api | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "API restart failed." }
    Wait-ApiReady
    $restored = Invoke-RestMethod "$api/v1/reports/$($report.id)" -Headers $headers
    if ($restored.sha256 -ne $report.sha256 -or $restored.object_sha256 -ne $report.object_sha256) {
        throw "PostgreSQL report restore mismatch."
    }
    docker compose exec -T api sh -c "test -f /app/data/local/objects/$($report.object_sha256).json"
    if ($LASTEXITCODE -ne 0) { throw "Report object did not survive API restart." }
    Write-Host "Project 56 Compose smoke passed: PostgreSQL, tenant isolation, API proxy, report/object restore." -ForegroundColor Green
} finally { Pop-Location }
