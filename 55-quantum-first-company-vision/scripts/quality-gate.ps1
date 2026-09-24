param()
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$gateStarted = Get-Date
$gateSteps = [System.Collections.Generic.List[object]]::new()
function Invoke-Checked {
    param([string]$Label, [scriptblock]$Action)
    Write-Host "  -> $Label" -ForegroundColor Cyan
    $stepStarted = Get-Date
    & $Action
    if ($LASTEXITCODE -ne 0) { throw "$Label failed with exit code $LASTEXITCODE." }
    $gateSteps.Add(@{ label = $Label; status = 'passed'; seconds = [math]::Round(((Get-Date)-$stepStarted).TotalSeconds, 2) })
}
Push-Location $projectRoot
try {
    $python = Join-Path $projectRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $python)) { throw 'Run scripts/setup.ps1 first.' }
    Invoke-Checked 'Ruff lint' { & $python -m ruff check src scripts tests }
    Invoke-Checked 'Ruff format' { & $python -m ruff format --check src scripts tests }
    Invoke-Checked 'mypy strict' { & $python -m mypy }
    Invoke-Checked 'Python dependency consistency' { & $python -m pip check }
    Invoke-Checked 'Evidence coverage, confidence and decision-to-source traces' { & $python -m venture_evidence.cli evidence validate }
    Invoke-Checked 'Unit, property, API, CLI and tamper tests' { & $python -m pytest -q }
    $parseErrors = @()
    Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.ps1' | ForEach-Object {
        $tokens = $null
        $errors = $null
        $null = [System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$tokens, [ref]$errors)
        $parseErrors += $errors
    }
    if ($parseErrors.Count -gt 0) { throw ($parseErrors | Out-String) }
    Invoke-Checked 'Research documents and contract examples' { & $python scripts/build_documents.py }
    Invoke-Checked 'Reports and JSON Schemas' { & $python -m venture_evidence.cli report build }
    Invoke-Checked 'Candidate handoff export' { & $python -m venture_evidence.cli handoff export --version company-vision-v1 }
    Push-Location (Join-Path $projectRoot 'apps\web')
    try {
        Invoke-Checked 'Frontend security audit' { & npm.cmd audit --audit-level=high }
        Invoke-Checked 'Web TypeScript' { & npm.cmd run typecheck }
        Invoke-Checked 'Web lint' { & npm.cmd run lint }
        Invoke-Checked 'Web production build' { & npm.cmd run build }
        Invoke-Checked 'Playwright evidence, responsive and accessibility flows' { & npm.cmd run test:e2e }
    } finally { Pop-Location }
    Invoke-Checked 'Bundle checksums and lineage after frontend build' { & $python -m venture_evidence.cli handoff verify }
    $repoRoot = Split-Path -Parent $projectRoot
    Invoke-Checked 'Project whitespace diff' { & git -c "safe.directory=$repoRoot" diff --check -- $projectRoot }
    $result = @{
        project = 55
        status = 'technical_gates_passed'
        human_approval = 'pending_human_review'
        completed_at = (Get-Date).ToUniversalTime().ToString('o')
        elapsed_seconds = [math]::Round(((Get-Date)-$gateStarted).TotalSeconds, 2)
        checks = $gateSteps.ToArray()
        cloud_deployed = $false
        interviews_conducted = 0
    }
    $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath 'reports\week-223\quality-gate.local.json' -Encoding UTF8
    Write-Host 'All Project 55 technical quality gates passed. Human thesis approval remains pending.' -ForegroundColor Green
} finally { Pop-Location }
