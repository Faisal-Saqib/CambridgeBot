$py = if (Get-Command py -ErrorAction SilentlyContinue) { 'py' } else { 'python' }
foreach ($b in @('forge-shop','forge')) {
  Write-Output "=== broad gate $b"
  & $py -X utf8 scripts\panel.py $b --opps apex apex22 --jobs 8 --quiet
}
