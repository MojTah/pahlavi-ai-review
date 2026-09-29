# Start the remaining TITUS text collection independently of Codex.
# Rerun after a clean stop to resume verified cached downloads.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = '[USER_HOME]\.venvs\codex-science\Scripts\python.exe'
$archivePath = Join-Path $projectRoot 'sources\local\public-texts-2026-09-20\titus'
$lockPath = Join-Path $archivePath 'collector.lock'
if (Test-Path -LiteralPath $lockPath) {
    throw "Collector lock exists at $lockPath. Check its process before recovering a stopped run."
}
if (-not (Test-Path -LiteralPath $pythonPath)) { throw "Python is missing: $pythonPath" }
$logFolder = Join-Path $archivePath 'logs'
$null = New-Item -ItemType Directory -Path $logFolder -Force
$stamp = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss-fff')
$stdoutPath = Join-Path $logFolder "$stamp.stdout.log"
$stderrPath = Join-Path $logFolder "$stamp.stderr.log"
$downloadProcess = Start-Process -FilePath $pythonPath -WorkingDirectory $projectRoot `
    -ArgumentList '-u scripts/collect_public_texts.py sources/titus-collection.json --limit 1800 --workers 2 --retry-transport-once' `
    -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
$record = [ordered]@{
    pid = $downloadProcess.Id
    launched_utc = [DateTime]::UtcNow.ToString('o')
    stdout = $stdoutPath
    stderr = $stderrPath
    status_file = (Join-Path $archivePath 'run-status.json')
    resume = 'Run this launcher again after completion or a clean stop; it verifies and reuses saved bytes.'
}
$record | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $archivePath 'background-process.json') -Encoding utf8
$record | ConvertTo-Json
