$py = if (Get-Command py -ErrorAction SilentlyContinue) { 'py' } else { 'python' }
$maps = @('00the_line','00anvil','00stampede','01starfish','00expanse','02treasure_box')
foreach ($b in @('forge-shop','forge')) {
  Write-Output "=== panel $b"
  & $py -X utf8 scripts\panel.py $b --opps apex apex22 --maps @maps --jobs 8
}
