param([string]$Action = "build")
& "$PSScriptRoot/build-core.ps1" -Action $Action
exit $LASTEXITCODE
