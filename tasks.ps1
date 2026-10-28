# Shortcuts for common cambc commands. Usage: .\tasks.ps1 <task> [-Bot main] [-Opp starter-cpp] [-Map 00ambush]
param(
    [Parameter(Position = 0)][string]$Task = "help",
    [string]$Bot = "main",
    [string]$Opp = "starter-cpp",
    [string]$Map = "00ambush"
)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

switch ($Task) {
    "build"    { cambc build $Bot }
    "release"  { cambc build --release $Bot }
    "run"      { cambc run $Bot $Opp --map $Map }
    "view"     { cambc view }
    "gauntlet" { py scripts\gauntlet.py $Bot $Opp }
    "bundle"   { cambc bundle $Bot }
    "submit"   { cambc submit $Bot }
    "maps"     { cambc maps pull }
    default    { Write-Output "tasks: build release run view gauntlet bundle submit maps" }
}
exit $LASTEXITCODE
