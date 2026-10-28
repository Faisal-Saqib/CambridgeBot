# Claude job runner for CambridgeBot.
# Start once from PowerShell:
#   powershell -ExecutionPolicy Bypass -File D:\Downloads\CambridgeBot\.claude_jobs\runner.ps1
# It runs every *.ps1 placed in .claude_jobs\queue (oldest name first), one at a
# time, from the repo root, writing output to .claude_jobs\out\<name>.log and
# moving the job to .claude_jobs\done. Close the window (or Ctrl+C) to stop.
$ErrorActionPreference = 'Continue'
$jobs = $PSScriptRoot
$root = Split-Path $jobs -Parent
$queue = Join-Path $jobs 'queue'
$out = Join-Path $jobs 'out'
$done = Join-Path $jobs 'done'
foreach ($d in @($queue, $out, $done)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
Write-Host "Claude runner watching $queue (repo $root). Ctrl+C to stop."
while ($true) {
    Set-Content -Path (Join-Path $jobs 'heartbeat.txt') -Value (Get-Date -Format o)
    $next = Get-ChildItem -Path $queue -Filter '*.ps1' | Sort-Object Name | Select-Object -First 1
    if ($null -eq $next) { Start-Sleep -Seconds 3; continue }
    $name = $next.BaseName
    $log = Join-Path $out "$name.log"
    $running = Join-Path $done "$name.ps1"
    Move-Item -Force $next.FullName $running
    Write-Host "$(Get-Date -Format T) running $name"
    Set-Content -Path (Join-Path $jobs 'current.txt') -Value $name
    Push-Location $root
    try {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $running *>&1 | Out-File -FilePath $log -Encoding utf8
        $code = $LASTEXITCODE
    } catch {
        $_ | Out-File -FilePath $log -Append -Encoding utf8
        $code = -1
    }
    Pop-Location
    Add-Content -Path $log -Value "`n[runner] exit $code at $(Get-Date -Format o)" -Encoding utf8
    Set-Content -Path (Join-Path $jobs 'current.txt') -Value ''
    Write-Host "$(Get-Date -Format T) finished $name (exit $code)"
}
