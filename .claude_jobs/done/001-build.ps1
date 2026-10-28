foreach ($b in @('forge','forge-shop')) {
  New-Item -ItemType Directory -Force -Path "bots\$b\.cargo" | Out-Null
  Copy-Item -Force bots\apex\.cargo\config.toml "bots\$b\.cargo\config.toml"
}
cambc --version
py --version
python --version
foreach ($b in @('forge-shop','forge')) {
  Write-Output "=== build $b"
  cambc build $b 2>&1 | ForEach-Object { "$_" } | Select-String -Pattern "built|error|-->|^\s+\|" 
}
Get-ChildItem bots\forge*\.cambc -Recurse -Filter bot-injected.wasm | Select-Object FullName, Length, LastWriteTime | Format-List
