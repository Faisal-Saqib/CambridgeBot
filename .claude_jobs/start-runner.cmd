@echo off
cd /d D:\Downloads\CambridgeBot
start "Claude runner" powershell -NoExit -ExecutionPolicy Bypass -File D:\Downloads\CambridgeBot\.claude_jobs\runner.ps1
