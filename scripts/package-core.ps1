param([string]$MsysRoot = 'C:/msys64', [string]$Python = 'python')
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$dll = 'target/release/zeebx_libretro.dll'
if (!(Test-Path -LiteralPath $dll)) { throw 'Compile o core antes de empacotar.' }
& $Python ferramentas/verifica_core.py $dll
if ($LASTEXITCODE -ne 0) { throw 'Falha na verificação da ABI.' }
$imports = & "$MsysRoot/ucrt64/bin/objdump.exe" -p $dll
if ($LASTEXITCODE -ne 0) { throw 'Falha ao examinar as dependências.' }
$names = @($imports | Select-String 'DLL Name:\s*(\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
if (!$names.Count) { throw 'Lista de dependências vazia.' }
foreach ($name in $names) {
    if ($name -notmatch '^(api-ms-win-.*|KERNEL32|ntdll|WS2_32|bcryptprimitives|bcrypt|ADVAPI32|USER32|GDI32|ole32|SHELL32|USERENV|ucrtbase)\.dll$') {
        throw "Dependência externa inesperada: $name"
    }
}
$version = ((Select-String -Path frontends/libretro/Cargo.toml -Pattern '^version = "([^"]+)"').Matches.Groups[1].Value)
if (!$version) { throw 'Versão não encontrada.' }
$stage = Join-Path (Get-Location) 'target/package'
# A pasta é exclusiva desta execução: nunca empacotar sobras de um pacote anterior.
$stage = Join-Path $stage ([guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $stage -Force | Out-Null
Copy-Item -LiteralPath $dll -Destination $stage
Copy-Item -LiteralPath frontends/libretro/zeebx_libretro.info -Destination $stage
foreach ($name in @('LICENSE','LICENSE-GPL3','THIRD-PARTY-NOTICES.txt','README.md')) {
    Copy-Item -LiteralPath $name -Destination $stage
}
Copy-Item -LiteralPath examples/Z-Wheel.zeebo -Destination $stage
# Além das crates, a DLL incorpora os runtimes GNU e pthread do MSYS2.
& (Join-Path $PSScriptRoot 'copy-runtime-licenses.ps1') -MsysRoot $MsysRoot -Destination $stage
$hash = (Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash.ToLowerInvariant()
"$hash  zeebx_libretro.dll" | Set-Content -LiteralPath (Join-Path $stage 'SHA256SUMS.txt') -Encoding ascii
New-Item -ItemType Directory -Path dist -Force | Out-Null
$zip = "dist/zeebx-emuvr-$version-windows-x64.zip"
Compress-Archive -Path "$stage/*" -DestinationPath $zip -Force
$zipHash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
"$zipHash  $([IO.Path]::GetFileName($zip))" | Set-Content -LiteralPath "$zip.sha256" -Encoding ascii
Write-Output "Pacote: $zip"
Write-Output "DLL SHA256: $hash"
